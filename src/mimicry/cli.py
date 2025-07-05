import uvicorn

import typer

from mimicry.core import load_sink_config, load_table_config
from mimicry.data import stream_data
from mimicry.server import build_fastapi_app


app = typer.Typer(
    no_args_is_help=True,
    help="Mimicry CLI for data generation and streaming",
)


@app.command(no_args_is_help=True)
def generate(
    sink_path: str = typer.Option(..., "-s", "--sink", help="Sink configuration path"),
    schema_path: str = typer.Option(
        ..., "-p", "--schema", help="Schema configuration path"
    ),
    interval: int = typer.Option(
        ..., "-i", "--interval", help="Interval in seconds between generating batches."
    ),
    count: int = typer.Option(
        ...,
        "-c",
        "--count",
        help="Count/number of rows to be added per batch",
    ),
    batches: int = typer.Option(
        ...,
        "-b",
        "--batches",
        help="Number of batches to be appended. If < 0 then indefinitely (until it is stopped)",
    ),
    strict: bool = typer.Option(
        False,
        "-x",
        "--strict",
        help="If True, will raise an error if the schema is not valid. If False, will log a warning.",
    ),
) -> None:
    """
    Generate and stream data based on the provided configuration.
    This command will read the schema and sink configurations, then stream data
    according to the specified parameters.
    """
    stream_data(
        table=load_table_config(schema_path),
        count=count,
        num_of_batches=batches,
        interval=interval,
        sink=load_sink_config(sink_path),
        strict=strict,
    )


@app.command(no_args_is_help=True)
def serve(
    name: str = typer.Option(
        "Mimicry API",
        "-t",
        "--title",
        help="Title of the FastAPI application",
    ),
    description: str = typer.Option(
        "Mimicry API for data generation",
        "-d",
        "--description",
        help="Description of the FastAPI application",
    ),
    version: str = typer.Option(
        "1.0.0",
        "-v",
        "--version",
        help="Version of the FastAPI application",
    ),
    schema_paths: list[str] = typer.Option(
        ...,
        "-s",
        "--schema",
        help="Schema configuration path",
    ),
    port: int = typer.Option(
        8000, "-p", "--port", help="Port to run the FastAPI server on"
    ),
    host: str = typer.Option(
        "0.0.0.0", "-H", "--host", help="Host to run the FastAPI server on"
    ),
    strict: bool = typer.Option(
        False,
        "-x",
        "--strict",
        help="If True, will raise an error if the schema is not valid. If False, will log a warning.",
    ),
    max_count: int = typer.Option(
        1000, "-m", "--max-count", help="Maximum number of rows to return per request"
    ),
):
    """
    Serve the Mimicry API with the provided schema configurations.
    This command will build a FastAPI application based on the provided schema paths
    and run it on the specified host and port.
    """
    tables = [load_table_config(schema_path) for schema_path in schema_paths]

    app = build_fastapi_app(
        *tables,
        strict=strict,
        name=name,
        description=description,
        version=version,
        max_count=max_count,
    )

    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    app()
