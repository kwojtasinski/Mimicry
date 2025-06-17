import os
import duckdb
import polars as pl
import pytest
import json

from mimicry.data import generate_data, stream_data
from mimicry.exceptions import MimicryInvalidCountValueError
from mimicry.models import SinkConfiguration, TableConfiguration
from kafka import KafkaConsumer
from pyiceberg.catalog import load_catalog


def get_dataframe_size(df: pl.DataFrame) -> int:
    return df.select(pl.len()).to_dicts()[0]["len"]


def is_sample_people_df_valid(df: pl.DataFrame, count: int = 100) -> None:
    assert df.schema == pl.Schema(
        {
            "id": pl.Int64,
            "first_name": pl.String,
            "last_name": pl.String,
            "birth_date": pl.Datetime(),
        },
    )
    assert get_dataframe_size(df) == count
    assert df.schema == pl.Schema(
        {
            "id": pl.Int64,
            "first_name": pl.String,
            "last_name": pl.String,
            "birth_date": pl.Datetime(),
        },
    )


@pytest.mark.unit
def test_generate_data_with_invalid_count_raises_error(
    sample_people_table_config: TableConfiguration,
) -> None:
    with pytest.raises(MimicryInvalidCountValueError):
        generate_data(table=sample_people_table_config, count=-1, strict=True)

    with pytest.raises(MimicryInvalidCountValueError):
        generate_data(table=sample_people_table_config, count=0, strict=True)


@pytest.mark.unit
def test_generate_data_works_as_expected(
    sample_people_table_config: TableConfiguration,
) -> None:
    df = generate_data(table=sample_people_table_config, count=100, strict=True)
    is_sample_people_df_valid(df)


@pytest.mark.unit
def test_stream_delta_lake_data_works_as_expected(
    sample_people_table_config: TableConfiguration,
    sample_people_deltalake_sink_config: SinkConfiguration,
) -> None:
    stream_data(
        table=sample_people_table_config,
        count=100,
        strict=True,
        num_of_batches=1,
        interval=1,
        sink=sample_people_deltalake_sink_config,
    )
    df = pl.read_delta(
        sample_people_deltalake_sink_config.configuration.path,
    )
    is_sample_people_df_valid(df)


@pytest.mark.unit
def test_stream_duckdb_data_works_as_expected(
    sample_people_table_config: TableConfiguration,
    sample_people_duckdb_sink_config: SinkConfiguration,
) -> None:
    os.environ["MIMICRY_UNSAFE_DUCKDB"] = "TRUE"

    stream_data(
        table=sample_people_table_config,
        count=100,
        strict=True,
        num_of_batches=1,
        interval=1,
        sink=sample_people_duckdb_sink_config,
    )

    with duckdb.connect(sample_people_duckdb_sink_config.configuration.path) as conn:
        df = conn.table("people").pl()
        is_sample_people_df_valid(df)


@pytest.mark.integration
def test_stream_kafka_data_works_as_expected(
    sample_people_table_config: TableConfiguration,
    sample_people_kafka_sink_config: SinkConfiguration,
    kafka_is_ready: None,
) -> None:
    topic_name = sample_people_kafka_sink_config.configuration.topic
    bootstrap_servers = sample_people_kafka_sink_config.configuration.producer_config[
        "bootstrap_servers"
    ]

    stream_data(
        table=sample_people_table_config,
        count=100,
        strict=True,
        num_of_batches=1,
        interval=1,
        sink=sample_people_kafka_sink_config,
    )

    consumer = KafkaConsumer(
        topic_name,
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset="earliest",
        consumer_timeout_ms=10000,  # 10 seconds timeout
        value_deserializer=lambda x: json.loads(x.decode("utf-8")),
        group_id="test_consumer_group",  # Unique group_id for each test run or ensure topic is clean
    )

    received_messages = [message.value for message in consumer]

    consumer.close()

    results = pl.DataFrame(received_messages)

    assert len(received_messages) == 100, (
        f"Expected 100 messages, but received {len(received_messages)}."
    )

    # FIXME: datetime parsing fails
    assert results.columns == [
        "id",
        "first_name",
        "last_name",
        "birth_date",
    ], f"Unexpected columns: {results.columns}"


@pytest.mark.integration
def test_append_to_postgres(
    sample_people_table_config: TableConfiguration,
    sample_people_postgres_sink_config: SinkConfiguration,
    postgres_is_ready: None,
) -> None:
    # Append to Postgres
    stream_data(
        table=sample_people_table_config,
        count=100,
        strict=True,
        num_of_batches=1,
        interval=1,
        sink=sample_people_postgres_sink_config,
    )

    # Read back from Postgres to verify
    df = pl.read_database_uri(
        "SELECT * FROM people",
        sample_people_postgres_sink_config.configuration.connection_string,
    )

    is_sample_people_df_valid(df)


@pytest.mark.integration
def test_append_to_iceberg(
    sample_people_table_config: TableConfiguration,
    sample_people_iceberg_sink_config: SinkConfiguration,
    iceberg_is_ready: None,
    minio_is_ready: None,
) -> None:
    # Append to Iceberg
    catalog = load_catalog(
        "main",
        **sample_people_iceberg_sink_config.configuration.catalog_properties,
    )
    catalog.create_namespace_if_not_exists(namespace="test")
    stream_data(
        table=sample_people_table_config,
        count=100,
        strict=True,
        num_of_batches=1,
        interval=1,
        sink=sample_people_iceberg_sink_config,
    )

    # Read back from Iceberg to verify
    table = catalog.load_table("test.people")

    is_sample_people_df_valid(table.to_polars().collect(), count=100)
