# Supported Sinks

Mimicry can stream generated data to various storage solutions.

## Delta Lake Sink

*   `type_of_sink` (`"delta_lake"`): Must be "delta_lake".
*   `path` (str): The path to the Delta Lake table directory.
*   `partition_by` (list[str], optional): A list of column names to partition the Delta table by.
*   `optimize` (int, optional): If set, performs a COMPACT optimization on the Delta table every N batches.
*   `vacuum` (int, optional): If set, vacuums the Delta table every N batches to remove old, unreferenced files.

**Example:**
```yaml
configuration:
  type_of_sink: "delta_lake"
  path: "/mnt/data/my_delta_table"
  partition_by: ["year", "month"]
  optimize: 10
  vacuum: 20
```

## DuckDB Sink

!!! warning "DuckDB does not support read and write operations by multiple processes simultaneously."
    This means that if you are generating data to a DuckDB sink, ensure that no other processes are trying to read from or write to the same DuckDB database file at the same time.

!!! warning "MIMICRY_UNSAFE_DUCKDB environment variable"
    If you set the `MIMICRY_UNSAFE_DUCKDB` environment variable to `true` mimicry will create the DuckDB table if missing. Note that this is unsafe, if the table name is not sanitized, it may lead to SQL injection vulnerabilities.


*   `type_of_sink` (`"duckdb"`): Must be "duckdb".
*   `path` (str): The path to the DuckDB database file.
*   `table_name` (str): The name of the table within the DuckDB database where data will be appended.

**Example:**
```yaml
configuration:
  type_of_sink: "duckdb"
  path: "my_database.db"
  table_name: "raw_events"
```

## PostgreSQL Sink

*   `type_of_sink` (`"postgres"`): Must be "postgres".
*   `connection_string` (str): The SQLAlchemy connection string for the PostgreSQL database.
*   `table_name` (str): The name of the table within the PostgreSQL database where data will be appended.

**Example:**
```yaml
configuration:
  type_of_sink: "postgres"
  connection_string: "postgresql://user:password@host:port/database"
  table_name: "fact_orders"
```

## Kafka Sink

!!! warning "Kafka Sink is experimental and may not be fully functional."
    It might not be the most efficient way to stream data to Kafka.

*   `type_of_sink` (`"kafka"`): Must be "kafka".
*   `producer_config` (dict): Configuration for the Kafka producer. Please refer to the [kafka-python documentation](https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html) for available options.
*   `topic` (str): The Kafka topic to which messages will be sent.

**Example:**
```yaml
configuration:
  type_of_sink: "kafka"
  producer_config:
    bootstrap_servers: "kafka1:9092,kafka2:9092"
    client_id: "mimicry-producer"
  topic: "user_activity_stream"
```

## Iceberg Sink
!!! warning "Iceberg Sink is experimental and may not be fully functional."
    It was tested only with the REST catalog and may not work with other catalog types.

*   `type_of_sink` (`"iceberg"`): Must be "iceberg".
*   `table_name` (str): The fully qualified name of the Iceberg table (e.g., `nessie.db.my_table`).
*   `catalog_properties` (dict[str, str]): Properties to configure the Iceberg catalog. This typically includes settings for the catalog type (e.g., REST, Hive, Nessie), URI, warehouse location, and any authentication details.

**Example (REST Catalog):**
```yaml
configuration:
  type_of_sink: "iceberg"
  table_name: "my_catalog.my_schema.my_iceberg_table"
  catalog_properties:
    uri: "http://localhost:8181"
    s3.endpoint: "http://minio:9000"
    s3.access-key-id: "minioadmin"
    s3.secret-access-key: "minioadmin"
    # Add other necessary properties for your specific catalog
```
