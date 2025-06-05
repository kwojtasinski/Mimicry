import pathlib

import pytest

from mimicry.core import load_table_config
from mimicry.models import (
    DeltaLakeSinkConfiguration,
    DuckDBSinkConfiguration,
    SinkConfiguration,
    TableConfiguration,
)

STATIC_PATH = pathlib.Path(__file__).parent / "static"


@pytest.fixture
def sample_people_table_config() -> TableConfiguration:
    return load_table_config(
        STATIC_PATH / "people.yaml",
    )


@pytest.fixture
def sample_people_deltalake_sink_config(tmpdir) -> SinkConfiguration:
    return SinkConfiguration(
        configuration=DeltaLakeSinkConfiguration(
            path=str(tmpdir / "people"),
        ),
    )


@pytest.fixture
def sample_people_duckdb_sink_config(tmpdir) -> SinkConfiguration:
    return SinkConfiguration(
        configuration=DuckDBSinkConfiguration(
            path=str(tmpdir / "people"),
            table_name="people",
        ),
    )
