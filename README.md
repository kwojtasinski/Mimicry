
# Mimicry

Mimicry is a Python-based tool designed for generating and streaming synthetic data. It allows users to define data schemas, generate mock data based on these schemas using the powerful [mimesis](https://mimesis.name/master/) library, and stream this data to various sinks like [Delta Lake](https://delta.io/) or [DuckDB](https://duckdb.org/). Additionally, Mimicry can expose the generated data through a FastAPI-based web server.

## Warning
This project is in its early stages and is not yet production-ready. It is intended for testing and development purposes only. Use at your own risk.

**Purpose**

The primary purpose of Mimicry is to provide developers and data engineers with a flexible and easy-to-use tool for:

* **Generating realistic mock data**: For testing, development, and demonstration purposes.  
* **Simulating data streams**: To test data pipelines and stream processing applications.  
* **Providing mock APIs**: For frontend development or microservice testing when backend services are not yet ready.

**Features**

* **Schema-based Data Generation**: Define the structure and type of your data using simple YAML configuration files.  
* **Rich Data Types**: Leverages the mimesis library for a wide variety of data field types (names, addresses, numbers, dates, custom patterns, etc.).  
* **Multiple Sinks**: Stream generated data to different storage solutions.  
  * **Delta Lake**: For robust, transactional data lake storage.  
  * **DuckDB**: For fast, embedded analytical database operations.  
* **Data Streaming**: Continuously generate and append data in batches at specified intervals.  
* **API Server**: Automatically build and run a FastAPI web server to expose data generation endpoints.  

### **Prerequisites**

* Python 3.12+  
* [uv](https://docs.astral.sh/uv/)

### **How to use it**
You can either run this project using the `uv` command or via Docker image.

```bash
uv run mimicry --help
```

```bash
docker run -it --port 8000:8000 kwojtasinski/mimicry:latest mimicry --help
```


**Configuration**

Mimicry uses YAML files to define how data should be generated (table configuration) and where it should be sent (sink configuration).

### **Table Configuration**

A table configuration file defines the schema of the data to be generated. It specifies the table's name, description, locale for data generation, and a list of fields.  

**Example `my_table_schema.yaml`:**

```yaml
name: DimEmployees
locale: en
description: Dimension table for employee information.
fields:
- description: Unique identifier for the employee.
  mimesis_field_args: []
  mimesis_field_kwargs:
    mask: EMP-#####
  mimesis_field_name: person.identifier
  name: employee_id
- description: National identification number for the employee.
  mimesis_field_args: []
  mimesis_field_kwargs: {}
  mimesis_field_name: person.identifier
  name: national_id
- description: Full name of the employee.
  mimesis_field_args: []
  mimesis_field_kwargs: {}
  mimesis_field_name: person.full_name
  name: full_name
- description: Job title or position held by the employee.
  mimesis_field_args: []
  mimesis_field_kwargs: {}
  mimesis_field_name: person.occupation
  name: job_title
- description: Work email address of the employee.
  mimesis_field_args: []
  mimesis_field_kwargs: {}
  mimesis_field_name: person.email
  name: email
- description: Date when the employee was hired.
  mimesis_field_args: []
  mimesis_field_kwargs:
    end: 2024
    start: 2010
  mimesis_field_name: datetime.date
  name: hire_date
- description: Annual salary of the employee in USD.
  mimesis_field_args: []
  mimesis_field_kwargs:
    maximum: 150000
    minimum: 30000
  mimesis_field_name: finance.price
  name: salary
- description: Employee ID of the manager (foreign key).
  mimesis_field_args: []
  mimesis_field_kwargs:
    mask: EMP-#####
  mimesis_field_name: person.identifier
  name: manager_id_fk
- description: City where the employee's office is located.
  mimesis_field_args: []
  mimesis_field_kwargs: {}
  mimesis_field_name: address.city
  name: office_location
- description: Indicates if the employee is currently active.
  mimesis_field_args: []
  mimesis_field_kwargs: {}
  mimesis_field_name: development.boolean
  name: is_active
```

Please refer to the [Mimesis documentation](https://mimesis.name/en/latest/) for a complete list of available fields and their parameters.

**Fields in TableConfiguration:**

* name (str): The name of the table.  
* description (str): A description of the table.  
* locale (str, optional): The Mimesis locale to use for data generation (e.g., "en", "de", "ja"). Defaults to "en".  
* fields (list): A list of FieldConfiguration objects.

**Fields in FieldConfiguration:**

* name (str): The name of the field (column name).  
* description (str): A description of the field.  
* mimesis_field_name (str): The Mimesis provider and method to use (e.g., "person.full_name", "address.city", "numeric.float_number").  
* mimesis_field_args (list, optional): A list of positional arguments to pass to the Mimesis method.  
* mimesis_field_kwargs (dict, optional): A dictionary of keyword arguments to pass to the Mimesis method.

### **Sink Configuration**

A sink configuration file defines where the generated data should be stored or sent.  
**Example `my_sink_config.yaml`:**

```yaml
configuration:
  # type_of_sink: "delta_lake"  # or "duckdb"
  # path: "./my_data/users_delta"
  # partition_by: ["year", "month"] # Optional for Delta Lake
  # optimize: 10 # Optional: optimize every 10 batches for Delta Lake
  # vacuum: 20 # Optional: vacuum every 20 batches for Delta Lake

  type_of_sink: "duckdb"
  path: "./my_database.duckdb"
  table_name: "users_table"
```

The top-level key is `configuration`, which then contains the specific sink type and its parameters.

#### **Delta Lake Sink**

* type_of_sink (`"delta_lake"`): Must be "delta_lake".  
* path (str): The path to the Delta Lake table directory.  
* partition_by (list[str], optional): A list of column names to partition the Delta table by.  
* optimize (int, optional): If set, performs a COMPACT optimization on the Delta table every N batches.  
* vacuum (int, optional): If set, vacuums the Delta table every N batches to remove old, unreferenced files.

#### **DuckDB Sink**

* type_of_sink (`"duckdb"`): Must be "duckdb".  
* path (str): The path to the DuckDB database file.  
* table_name (str): The name of the table within the DuckDB database where data will be appended.

**Command-Line Interface (CLI)**

Mimicry provides a CLI for its main functionalities, built using Typer. You can access help for any command by appending `--help`.

```bash
uv run mimicry --help
```

### **Generating and Streaming Data (generate)**

This command generates data based on a schema and streams it to a configured sink.

```bash
uv run mimicry generate \
    -s examples/sinks/deltalake_sink.yaml \
    -p examples/tables/DimEmployees.yaml \
    -i 2 \
    -c 100 \
    -b 5 \
    --strict
```

**Options for generate:**

* `-s`: Path to the sink configuration YAML file. (Required)  
* `-p`: Path to the table schema configuration YAML file. (Required)  
* `-i`: Interval in seconds between generating batches. (Required)  
* `-c`: Number of rows to generate per batch. (Required)  
* `-b`: Number of batches to generate. If less than 0, streams indefinitely. (Required)  
* `--strict`: If True, will raise an error if the schema is not valid. Otherwise, logs a warning. (Optional, defaults to False)

### **Serving Data via FastAPI (serve)**

This command builds and runs a FastAPI server that exposes endpoints for generating data based on one or more table schemas.

```bash
uv run mimicry serve \
    --title "My Mock API" \
    --description "API for generating mock user and product data." \
    --version "0.1.0" \
    --schema examples/tables/DimEmployees.yaml \
    --schema examples/tables/DimProducts.yaml \
    --port 8080 \
    --host "0.0.0.0" \
    --strict
```

**Options for serve:**

* `-t, --name TEXT`: Title of the FastAPI application. (Default: "Mimicry API")  
* `-d, --description TEXT`: Description of the FastAPI application. (Default: "Mimicry API for data generation")  
* `-v, --version TEXT`: Version of the FastAPI application. (Default: "1.0.0")  
* `-s, --schema-paths PATH`: Path to a table schema configuration YAML file. Can be specified multiple times for multiple tables. (Required)  
* `-p, --port INTEGER`: Port to run the FastAPI server on. (Default: 8000)  
* `-h, --host TEXT`: Host to run the FastAPI server on. (Default: "0.0.0.0")  
* `--strict`: If True, raises an error if any schema is not valid. Otherwise, logs a warning. (Optional, defaults to False)

Once running, the API will provide endpoints like `/tables/{table_name}?count={number_of_records}`. For example, if you have a table named "DimEmployees", you can access it via `http://<host>:<port>/tables/DimEmployees?count=10`. The API documentation (Swagger UI) will be available at `http://<host>:<port>/docs`.


**Environment Variables**

* `MIMICRY_DEBUG`: If set to any value (e.g., "true", "1"), the logging level is set to DEBUG. Otherwise, it defaults to INFO.  
* `MIMICRY_UNSAFE_DUCKDB`: If set to "TRUE" (case-insensitive), allows the use of DuckDB table names without sanitization in the CREATE TABLE statement when the table doesn't exist. This can be a security risk (SQL injection) if table names come from untrusted sources. Use with caution.

**Examples**
For more examples, check the `examples` directory in the repository. It contains various sink configurations and table schemas to help you get started quickly.

### Demo

**Data streaming using Delta Lake**
[![asciicast](https://asciinema.org/a/bWUj005LMLppxeGGOL50mPnu4.svg)](https://asciinema.org/a/bWUj005LMLppxeGGOL50mPnu4)

**Serving data via FastAPI**
[![asciicast](https://asciinema.org/a/1Gt2xNjgsySB1o0cL8TNuxdIK.svg)](https://asciinema.org/a/1Gt2xNjgsySB1o0cL8TNuxdIK)


### TODOs
* Add more sink types (e.g., Iceberg, Kafka).
* Improve docs and examples.
* Setup proper CI/CD pipeline.