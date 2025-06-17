import json
import logging
import os
import time
from collections.abc import Callable

from kafka import KafkaProducer as Producer

import duckdb
import polars as pl
from deltalake import DeltaTable
from mimesis import Fieldset, Locale
from pyiceberg.catalog import load_catalog

from mimicry.exceptions import (
    MimicryInvalidCountValueError,
    MimicryInvalidFieldConfigurationError,
)
from mimicry.models import (
    DeltaLakeSinkConfiguration,
    DuckDBSinkConfiguration,
    IcebergSinkConfiguration,
    KafkaSinkConfiguration,
    PostgresSinkConfiguration,
    SinkConfiguration,
    TableConfiguration,
)

logger = logging.getLogger(__name__)


def does_duckdb_table_exist(conn: duckdb.DuckDBPyConnection, table_name: str) -> bool:
    try:
        conn.table(table_name=table_name)
        return True
    except duckdb.CatalogException:
        return False


def prepare_mimesis_schema(
    table: TableConfiguration,
    count: int,
    strict: bool,
) -> Callable:
    results = {}
    try:
        locale = getattr(Locale, table.locale.upper())
    except AttributeError:
        logger.warning("Locale '%s' not found. Defaulting to English.", table.locale)
        locale = Locale.EN

    fs = Fieldset(
        locale=locale,
        i=count,
    )

    try:
        count = int(count)
        assert count > 0, "Count must be a positive integer."
    except (ValueError, AssertionError):
        raise MimicryInvalidCountValueError(count=count)

    for field in table.fields:
        try:
            results[field.name] = fs(
                field.mimesis_field_name,
                *field.mimesis_field_args,
                **field.mimesis_field_kwargs,
            )
        except Exception as e:
            if strict:
                raise MimicryInvalidFieldConfigurationError(field=field, exception=e)
            logger.warning(
                "Failed to generate data for field '%s': %s. Skipping this field.",
                field.name,
                e,
            )
            continue

    return lambda: results


def generate_data(table: TableConfiguration, count: int, strict: bool) -> pl.DataFrame:
    """Generate data for a table configuration.

    Args:
        table (TableConfiguration): The table configuration.
        count (int): The number of records to generate.
        strict (bool): If True, raises an error if the table configuration is invalid.

    Returns:
        pl.DataFrame: A DataFrame representing the generated data.

    """
    schema = prepare_mimesis_schema(table=table, count=count, strict=strict)
    results = pl.DataFrame(schema())
    logger.info(
        "Generated %d records for table '%s' with schema:\n%s",
        count,
        table.name,
        json.dumps(results.schema, indent=4, default=str),
    )
    logger.debug(
        "Head of the generated data for table '%s':\n%s",
        table.name,
        results.head(5),  # Show only the first 5 records for debugging
    )
    return pl.DataFrame(schema())


def append_to_delta(
    config: DeltaLakeSinkConfiguration,
    data: pl.DataFrame,
    batch_idx: int,
) -> None:
    data.write_delta(target=config.path, mode="append")
    if config.vacuum is not None and batch_idx % config.vacuum == 0:
        logger.info(
            "Vacuuming Delta Lake table at '%s' after batch %d",
            config.path,
            batch_idx,
        )
        table = DeltaTable(config.path)
        table.vacuum()

    if config.optimize is not None and batch_idx % config.optimize == 0:
        logger.info(
            "Optimizing Delta Lake table at '%s' after batch %d",
            config.path,
            batch_idx,
        )
        table = DeltaTable(config.path)
        table.optimize.compact()


def append_to_duckdb(config: DuckDBSinkConfiguration, data: pl.DataFrame) -> None:
    MIMICRY_UNSAFE_DUCKDB = (
        os.environ.get("MIMICRY_UNSAFE_DUCKDB", "FALSE").upper() == "TRUE"
    )
    with duckdb.connect(config.path) as conn:
        if MIMICRY_UNSAFE_DUCKDB and not does_duckdb_table_exist(
            conn=conn, table_name=config.table_name
        ):
            logger.warning(
                'MIMICRY_UNSAFE_DUCKDB environment variable set to true. DuckDB table name: "%s" is not sanitized, hence it might result in the SQL injection attack.',
                config.table_name,
            )
            create_table_query = f"CREATE TABLE IF NOT EXISTS {config.table_name} AS SELECT * FROM data LIMIT 0"
            conn.execute(create_table_query)
        # TECH DEBT: to safely append data to the DuckDB table we use append method that supports only pandas DataFrame.
        # it raises the CatalogException if table is not created before the ingestion
        conn.append(config.table_name, data.to_pandas())


def append_to_postgres(
    config: PostgresSinkConfiguration, data: pl.DataFrame, batch_idx: int
) -> None:
    data.write_database(
        connection=config.connection_string,
        table_name=config.table_name,
        if_table_exists="append",
        engine="sqlalchemy",
    )


def append_to_iceberg(
    config: IcebergSinkConfiguration, data: pl.DataFrame, batch_idx: int
) -> None:
    catalog = load_catalog(
        "main",
        **config.catalog_properties,
    )
    if not catalog.table_exists(config.table_name):
        catalog.create_table(
            identifier=config.table_name,
            schema=data.to_arrow().schema,
        )
    table = catalog.load_table(config.table_name)
    table.append(data.to_arrow())


def append_to_kafka(
    config: KafkaSinkConfiguration, data: pl.DataFrame, batch_idx: int
) -> None:
    producer = Producer(**config.producer_config)
    topic = config.topic
    items = data.write_ndjson()

    for item in items.splitlines():
        producer.send(topic, value=item.encode("utf-8"))

    producer.flush()
    producer.close()


def append_to_sink(sink: SinkConfiguration, data: pl.DataFrame, batch_idx: int) -> None:
    match sink.configuration.type_of_sink:
        case "delta_lake":
            append_to_delta(config=sink.configuration, data=data, batch_idx=batch_idx)
        case "duckdb":
            append_to_duckdb(config=sink.configuration, data=data)
        case "postgres":
            append_to_postgres(
                config=sink.configuration, data=data, batch_idx=batch_idx
            )
        case "iceberg":
            append_to_iceberg(config=sink.configuration, data=data, batch_idx=batch_idx)
        case "kafka":
            append_to_kafka(config=sink.configuration, data=data, batch_idx=batch_idx)
        case _:
            raise ValueError(
                f"Unsupported sink type: {sink.configuration.type_of_sink}",
            )
    logger.info(
        "Appended %d records to sink of type '%s' in batch %d.",
        len(data),
        sink.configuration.type_of_sink,
        batch_idx,
    )


def is_stream_active(idx: int, num_of_batches: int) -> bool:
    return idx <= num_of_batches if num_of_batches > 0 else True


def stream_data(
    table: TableConfiguration,
    count: int,
    interval: int,
    num_of_batches: int,
    sink: SinkConfiguration,
    strict: bool = False,
) -> None:
    idx = 1
    logger.info(
        "Starting data streaming for table '%s' with %d records per batch, every %d seconds.",
        table.name,
        count,
        interval,
    )

    logger.info("Table configuration: %s", table.model_dump_json(indent=4))

    while is_stream_active(idx, num_of_batches):
        data = generate_data(table=table, count=count, strict=strict)

        if num_of_batches > 0:
            logger.info(
                "Generated %d records for table '%s' in batch %d/%d",
                count,
                table.name,
                idx,
                num_of_batches,
            )
        else:
            logger.info(
                "Generated %d records for table '%s' in batch %d (until stopped)",
                count,
                table.name,
                idx,
            )

        append_to_sink(sink=sink, data=data, batch_idx=idx)

        if num_of_batches == 1:
            logger.info(
                "Single batch completed. Exiting after appending %d records to sink of type '%s'.",
                count,
                sink.configuration.type_of_sink,
            )
            return

        logger.info(
            "Appended %d records to sink of type '%s' in batch %d. Waiting for %d seconds before next batch.",
            count,
            sink.configuration.type_of_sink,
            idx,
            interval,
        )

        time.sleep(interval)

        idx += 1


__all__ = ["stream_data", "generate_data"]
