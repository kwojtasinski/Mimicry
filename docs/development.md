# Development

## Prerequisites

*   Python 3.12+
*   [uv](https://docs.astral.sh/uv/) (for local development)
*   Docker (for running as a container)

## How to Use

You can either run this project using the `uv` command or via a Docker image.

### Using `uv` (Local Development)

Ensure `uv` is installed. Then, from the project root directory:

1.  **Install dependencies:**
    ```bash
    uv pip install -r requirements.txt 
    # or if you have a pyproject.toml with dependencies defined
    uv pip install .
    ```

2.  **Run Mimicry commands:**
    Use `uv run` to execute the `mimicry` CLI. For example, to see the help message:
    ```bash
    uv run mimicry --help
    ```
    To generate data:
    ```bash
    uv run mimicry generate -p examples/tables/DimEmployees.yaml -s examples/sinks/deltalake_sink.yaml --strict
    ```
    To start the API server:
    ```bash
    uv run mimicry serve -p examples/tables/DimEmployees.yaml --strict
    ```

### Using Docker

A Docker image is available for Mimicry.

1.  **Pull the latest image (if not building locally):**
    ```bash
    docker pull k0wojtasinski/mimicry:latest 
    ```
    (Note: Replace with the correct image name if it's different)

2.  **Run Mimicry commands within a container:**
    For example, to see the help message:
    ```bash
    docker run -it --rm k0wojtasinski/mimicry:latest mimicry --help
    ```
    To run the API server and expose it on port 8000:
    ```bash
    docker run -it --rm -p 8000:8000 k0wojtasinski/mimicry:latest mimicry serve -p examples/tables/DimEmployees.yaml --host 0.0.0.0
    ```
    You might need to mount volumes for your configuration files:
    ```bash
    docker run -it --rm -p 8000:8000 \
      -v $(pwd)/examples:/app/examples \
      k0wojtasinski/mimicry:latest \
      mimicry serve -p /app/examples/tables/DimEmployees.yaml --host 0.0.0.0
    ```
