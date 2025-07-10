# Supported Sinks

Mimicry can stream generated data to various storage solutions.

## Delta Lake Sink

* `type_of_sink` (`"delta_lake"`): Must be "delta_lake".
* `path` (str): The path to the Delta Lake table directory.
* `partition_by` (list[str], optional): A list of column names to partition the Delta table by.
* `optimize` (int, optional): If set, performs a COMPACT optimization on the Delta table every N batches.
* `vacuum` (int, optional): If set, vacuums the Delta table every N batches to remove old, unreferenced files.

### Local File System Example

**Example:**

```yaml
configuration:
  type_of_sink: "delta_lake"
  path: "/mnt/data/my_delta_table"
  partition_by: ["year", "month"]
  optimize: 10
  vacuum: 20
```

### Amazon S3 Example

Delta Lake supports Amazon S3 using the `s3://` URI scheme. Authentication is handled via environment variables. Please check [object_store docs](https://docs.rs/object_store/latest/object_store/aws/enum.AmazonS3ConfigKey.html#variants) for more.

**Configuration:**

```yaml
configuration:
  type_of_sink: "delta_lake"
  path: "s3://${S3_BUCKET_NAME}/delta-tables/employees"
  partition_by: ["year", "month", "day"]
  optimize: 10
  vacuum: 20
```

**Required Environment Variables:**

```bash
# AWS Credentials
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_REGION=us-east-1
```

**Optional Environment Variables:**

```bash
# For temporary credentials (IAM roles, etc.)
export AWS_SESSION_TOKEN=your_session_token

# For S3-compatible storage (MinIO, etc.)
export AWS_ENDPOINT_URL=https://your-s3-compatible-endpoint
```

### Google Cloud Storage Example

Delta Lake supports Google Cloud Storage using the `gs://` URI scheme. Authentication is handled via environment variables. Please check [object_store docs](https://docs.rs/object_store/latest/object_store/gcp/enum.GoogleConfigKey.html#variants) for more.

**Configuration:**

```yaml
configuration:
  type_of_sink: "delta_lake"
  path: "gs://bucket_name/delta-tables/employees"
  partition_by: ["year", "month", "day"]
  optimize: 10
  vacuum: 20
```

**Authentication Methods:**

1. **Service Account Key** (Recommended for Production):

   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

   Check [GOOGLE_APPLICATION_CREDENTIALS environment variable](https://cloud.google.com/docs/authentication/application-default-credentials#GAC) for more

2. **Application Default Credentials** (Development):

   ```bash
   # Login with gcloud CLI
   gcloud auth application-default login
   ```

3. **Workload Identity** (Kubernetes):
   No additional environment variables needed if configured properly in your Kubernetes cluster.

**Optional Environment Variables:**

```bash
# Google Cloud Project
export GOOGLE_CLOUD_PROJECT=your-project-id
```

**Docker Example:**

```bash
# Mounting Service Account JSON File Key
docker run --rm \
  -v /path/to/secret_file.json:/secrets/gcp-key.json:ro \
  -e GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcp-key.json \
  -e GOOGLE_CLOUD_PROJECT=GOOGLE_CLOUD_PROJECT_ID \
  mimicry:latest \
    uv run mimicry generate \
    --schema examples/tables/DimGeospatialData.yaml \
    --sink examples/sinks/deltalake_gcs_sink.yaml \
    --count 1000 \
    --interval 2 \
    --batches 10
```

## DuckDB Sink

!!! warning "DuckDB does not support read and write operations by multiple processes simultaneously."
    This means that if you are generating data to a DuckDB sink, ensure that no other processes are trying to read from or write to the same DuckDB database file at the same time.

!!! warning "MIMICRY_UNSAFE_DUCKDB environment variable"
    If you set the `MIMICRY_UNSAFE_DUCKDB` environment variable to `true` mimicry will create the DuckDB table if missing. Note that this is unsafe, if the table name is not sanitized, it may lead to SQL injection vulnerabilities.

* `type_of_sink` (`"duckdb"`): Must be "duckdb".
* `path` (str): The path to the DuckDB database file.
* `table_name` (str): The name of the table within the DuckDB database where data will be appended.

**Example:**

```yaml
configuration:
  type_of_sink: "duckdb"
  path: "my_database.db"
  table_name: "raw_events"
```

## PostgreSQL Sink

* `type_of_sink` (`"postgres"`): Must be "postgres".
* `connection_string` (str): The SQLAlchemy connection string for the PostgreSQL database.
* `table_name` (str): The name of the table within the PostgreSQL database where data will be appended.

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

* `type_of_sink` (`"kafka"`): Must be "kafka".
* `producer_config` (dict): Configuration for the Kafka producer. Please refer to the [kafka-python documentation](https://kafka-python.readthedocs.io/en/master/apidoc/KafkaProducer.html) for available options.
* `topic` (str): The Kafka topic to which messages will be sent.

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

* `type_of_sink` (`"iceberg"`): Must be "iceberg".
* `table_name` (str): The fully qualified name of the Iceberg table (e.g., `nessie.db.my_table`).
* `catalog_properties` (dict[str, str]): Properties to configure the Iceberg catalog. This typically includes settings for the catalog type (e.g., REST, Hive, Nessie), URI, warehouse location, and any authentication details.

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
