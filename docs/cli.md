# Command-Line Interface (CLI)

Mimicry provides a CLI for its main functionalities, built using Typer. You can access help for any command by appending `--help`.

```bash
uv run mimicry --help
```
Or, if using Docker:
```bash
docker run -it --rm k0wojtasinski/mimicry:latest mimicry --help
```

## Generating and Streaming Data (`generate`)

This command generates data based on a schema and streams it to a configured sink.

```bash
uv run mimicry generate \
    -p path/to/your/table_config.yaml \
    -s path/to/your/sink_config.yaml \
    --count 1000 \
    --interval 5 \
    --num-of-batches 10 \
    --strict
```

**Options for `generate`:**

*   `-p`, `--table-config-path` PATH: Path to the table schema configuration YAML file. (Required)
*   `-s`, `--sink-config-path` PATH: Path to the sink configuration YAML file. (Required)
*   `-c`, `--count` INTEGER: Number of records to generate per batch. [default: 1000]
*   `-i`, `--interval` INTEGER: Interval in seconds between generating batches. [default: 10]
*   `-n`, `--num-of-batches` INTEGER: Number of batches to generate. Set to 0 for continuous streaming. [default: 1]
*   `--strict` / `--no-strict`: If True, raises an error if the table configuration is invalid. [default: False]
*   `--help`: Show this message and exit.

## Running as an API Server (`serve`)

This command starts a FastAPI web server to expose data generation endpoints.

```bash
uv run mimicry serve \
    -p path/to/your/table_config1.yaml \
    -p path/to/your/table_config2.yaml \
    --name "My Mock API" \
    --description "An API for generating mock data." \
    --max-count 500 \
    --strict
```

**Options for `serve`:**

*   `-p`, `--table-config-path` PATH: Path to a table schema configuration YAML file. Can be specified multiple times for multiple tables. (Required)
*   `--name` TEXT: The name of the FastAPI application. [default: Mimicry API]
*   `--description` TEXT: A description of the FastAPI application. [default: A FastAPI application built with Mimicry.]
*   `--max-count` INTEGER: Maximum number of records that can be requested in a single API call. [default: 1000]
*   `--strict` / `--no-strict`: If True, the application will not start if any table configuration is invalid. [default: False]
*   `--version` TEXT: The version of the FastAPI application. [default: 1.0.0]
*   `--host` TEXT: The host to bind the server to. [default: 0.0.0.0]
*   `--port` INTEGER: The port to bind the server to. [default: 8000]
*   `--help`: Show this message and exit.
