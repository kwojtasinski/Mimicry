# Welcome to Mimicry!

Mimicry is a Python-based tool designed for generating and streaming synthetic data. It allows users to define data schemas, generate mock data based on these schemas using the powerful [mimesis](https://mimesis.name/master/) library, and stream this data to various sinks like [Delta Lake](https://delta.io/), [DuckDB](https://duckdb.org/), [PostgreSQL](https://www.postgresql.org/), [Apache Kafka](https://kafka.apache.org/), or [Apache Iceberg](https://iceberg.apache.org/). Additionally, Mimicry can expose the generated data through a FastAPI-based web server.

!!! warning "Early Stage Project"
    This project is in its early stages and is not yet production-ready. It is intended for testing and development purposes only. Use at your own risk.

## Purpose

The primary purpose of Mimicry is to provide developers and data engineers with a flexible and easy-to-use tool for:

*   **Generating realistic mock data**: For testing, development, and demonstration purposes.
*   **Simulating data streams**: To test data pipelines and stream processing applications.
*   **Providing mock APIs**: For frontend development or microservice testing when backend services are not yet ready.

## Features

*   **Schema-based Data Generation**: Define the structure and type of your data using simple YAML configuration files. See [Configuration](configuration.md).
*   **Rich Data Types**: Leverages the mimesis library for a wide variety of data field types (names, addresses, numbers, dates, custom patterns, etc.).
*   **Multiple Sinks**: Stream generated data to different storage solutions. See [Supported Sinks](sinks.md).
    *   Delta Lake: For robust, transactional data lake storage.
    *   DuckDB: For fast, embedded analytical database operations.
    *   PostgreSQL: For reliable relational database storage.
    *   Apache Kafka: For high-throughput, distributed event streaming.
    *   Apache Iceberg: For managing large, analytic datasets with a table format.
*   **Data Streaming**: Continuously generate and append data in batches at specified intervals. See the [CLI documentation](cli.md#generating-and-streaming-data-generate).
*   **API Server**: Automatically build and run a FastAPI web server to expose data generation endpoints. See the [CLI documentation](cli.md#running-as-an-api-server-serve).

## Getting Started

To get started with Mimicry, check out the [Development](development.md) guide for installation and usage instructions.

Navigate through the documentation using the menu to learn more about [Configuration](configuration.md), [Supported Sinks](sinks.md), and the [Command-Line Interface (CLI)](cli.md).
