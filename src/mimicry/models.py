from typing import Any, Literal

from pydantic import BaseModel, Field, field_validator


class FieldConfiguration(BaseModel):
    name: str
    description: str
    mimesis_field_name: str
    mimesis_field_args: list[Any] = Field(default_factory=list)
    mimesis_field_kwargs: dict[str, Any] = Field(
        default_factory=dict,
    )

    @field_validator("name")
    def validate_name(cls, value: str) -> str:
        proper_value = value.strip().replace(" ", "_").lower()
        if not proper_value.isalnum() and "_" not in proper_value:
            raise ValueError(
                "Field name must be alphanumeric or contain underscores only."
            )
        return proper_value


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


class PostgresSinkConfiguration(BaseModel):
    type_of_sink: Literal["postgres"] = "postgres"
    connection_string: str
    table_name: str


class KafkaSinkConfiguration(BaseModel):
    type_of_sink: Literal["kafka"] = "kafka"
    producer_config: dict = Field(
        default_factory=dict,
        description="Configuration for the Kafka producer. Please refer to the [kafka-python documentation](https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html) for available options.",
    )
    topic: str


class IcebergSinkConfiguration(BaseModel):
    type_of_sink: Literal["iceberg"] = "iceberg"
    table_name: str
    catalog_properties: dict[str, str] = Field(
        default_factory=dict,
    )


class SinkConfiguration(BaseModel):
    configuration: (
        DeltaLakeSinkConfiguration
        | DuckDBSinkConfiguration
        | PostgresSinkConfiguration
        | KafkaSinkConfiguration
        | IcebergSinkConfiguration
    ) = Field(
        discriminator="type_of_sink",
    )
