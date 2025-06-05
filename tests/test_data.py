import os
import duckdb
import polars as pl
import pytest

from mimicry.data import generate_data, stream_data
from mimicry.exceptions import MimicryInvalidCountValueError
from mimicry.models import SinkConfiguration, TableConfiguration


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


def test_generate_data_with_invalid_count_raises_error(
    sample_people_table_config: TableConfiguration,
) -> None:
    with pytest.raises(MimicryInvalidCountValueError):
        generate_data(table=sample_people_table_config, count=-1, strict=True)

    with pytest.raises(MimicryInvalidCountValueError):
        generate_data(table=sample_people_table_config, count=0, strict=True)


def test_generate_data_works_as_expected(
    sample_people_table_config: TableConfiguration,
) -> None:
    df = generate_data(table=sample_people_table_config, count=100, strict=True)
    is_sample_people_df_valid(df)


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

    print(sample_people_duckdb_sink_config.configuration.path)

    with duckdb.connect(sample_people_duckdb_sink_config.configuration.path) as conn:
        df = conn.table("people").pl()
        is_sample_people_df_valid(df)
