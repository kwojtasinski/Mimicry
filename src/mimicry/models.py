from typing import Literal

from pydantic import BaseModel, Field, field_validator


class FieldConfiguration(BaseModel):
    name: str
    description: str
    mimesis_field_name: str
    mimesis_field_args: list[str | int | float | bool] = Field(default_factory=list)
    mimesis_field_kwargs: dict[str, str | int | float | bool | list[str]] = Field(
        default_factory=dict,
    )


class TableConfiguration(BaseModel):
    name: str
    description: str
    locale: str = "en"
    fields: list[FieldConfiguration] = Field(default_factory=list)


class SinkConfigurationType(BaseModel):
    type_of_sink: str


class DeltaLakeSinkConfiguration(BaseModel):
    type_of_sink: Literal["delta_lake"] = "delta_lake"
    path: str
    partition_by: list[str] | None = None
    optimize: int | None = None
    vacuum: int | None = None


class DuckDBSinkConfiguration(BaseModel):
    type_of_sink: Literal["duckdb"] = "duckdb"
    path: str
    table_name: str


class SinkConfiguration(BaseModel):
    configuration: DeltaLakeSinkConfiguration | DuckDBSinkConfiguration = Field(
        discriminator="type_of_sink",
    )
