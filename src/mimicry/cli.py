import uvicorn

import typer

from mimicry.core import load_sink_config, load_table_config
from mimicry.data import stream_data
from mimicry.interactive import interactive_table_definition, save_table_configuration
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


@app.command()
def define(
    output: str = typer.Option(
        None,
        "-o",
        "--output",
        help="Output path for the table configuration file. If not provided, uses table name.",
    ),
) -> None:
    """
    Interactively define a table configuration using mimesis providers.
    This command will guide you through selecting providers, methods, and configuring fields
    to create a complete table definition.
    """
    try:
        # Run interactive table definition
        table_config = interactive_table_definition()
        
        # Save the configuration
        output_path = save_table_configuration(table_config, output)
        
        typer.echo(f"✅ Table configuration saved to: {output_path}")
        typer.echo(f"📊 Table '{table_config.name}' with {len(table_config.fields)} fields")
        
        # Show a preview of the configuration
        typer.echo("\n📋 Configuration preview:")
        typer.echo(f"Name: {table_config.name}")
        typer.echo(f"Description: {table_config.description}")
        typer.echo(f"Locale: {table_config.locale}")
        typer.echo(f"Fields:")
        for field in table_config.fields:
            typer.echo(f"  - {field.name}: {field.mimesis_field_name}")
            
    except KeyboardInterrupt:
        typer.echo("\n❌ Operation cancelled by user")
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"❌ Error: {e}")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
