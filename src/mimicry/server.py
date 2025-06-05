import logging

import pydantic
from fastapi import FastAPI, HTTPException, Request
from fastapi.routing import APIRoute

from mimicry.data import generate_data
from mimicry.exceptions import MimicryInvalidCountValueError
from mimicry.models import TableConfiguration

logger = logging.getLogger(__name__)


def prepare_base_fastapi_app(
    name: str,
    description: str,
    version: str = "1.0.0",
) -> FastAPI:
    """Prepare a base FastAPI application instance.

    Args:
        name (str): The name of the application.
        description (str): A description of the application.
        version (str): The version of the application.

    Returns:
        FastAPI: The prepared FastAPI application instance.

    """
    app = FastAPI(
        title=name,
        description=description,
        version=version,
    )

    @app.exception_handler(MimicryInvalidCountValueError)
    async def count_value_exception_handler(
        request: Request,
        exc: MimicryInvalidCountValueError,
    ) -> None:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    return app


def build_table_model(
    table: TableConfiguration,
    strict: bool,
) -> type[pydantic.BaseModel]:
    """Build a Pydantic model for the given table configuration.
    Args:
        table (TableConfiguration): The table configuration to build the model for.
        strict (bool): Whether to enforce strict validation.
    Returns:
        type[pydantic.BaseModel]: The Pydantic model class for the table.
    """
    sample_data = generate_data(table, 1, strict).to_dicts()[0]

    result_type = pydantic.create_model(
        table.name,
        **{
            field.name: (
                type(sample_data[field.name]),
                pydantic.Field(..., description=field.description),
            )
            for field in table.fields
            if field.name in sample_data
        },
    )

    return result_type


def build_api_route(
    table: TableConfiguration, strict: bool, max_count: int
) -> APIRoute:
    """
    Build an API route for the given table configuration.
    Args:
        table (TableConfiguration): The table configuration to build the route for.
        strict (bool): Whether to enforce strict validation. If True, raises an error if the table configuration is invalid.
    Returns:
        APIRoute: The FastAPI route for the table.
    """
    result_type = build_table_model(table=table, strict=strict)
    route_path = f"/tables/{table.name}"

    def endpoint_callable(count: int):
        count = min(count, max_count)
        return generate_data(table=table, count=count, strict=strict).to_dicts()

    return APIRoute(
        path=route_path,
        description=table.description,
        response_model=list[result_type],
        endpoint=endpoint_callable,
        methods=["GET"],
        name=table.name,
    )


def build_fastapi_app(
    *tables: TableConfiguration,
    name: str,
    description: str,
    strict: bool,
    max_count: int,
    version: str = "1.0.0",
) -> FastAPI:
    """
    Build a FastAPI application with routes for the provided table configurations.
    Args:
        *tables (TableConfiguration): The table configurations to build routes for.
        name (str): The name of the FastAPI application.
        description (str): A description of the FastAPI application.
        strict (bool): If True, raises an error if the table configuration is invalid. If True, the application will not start if any table configuration is invalid.
        version (str): The version of the FastAPI application.
    Returns:
        FastAPI: The FastAPI application instance with the built routes.
    Raises:
        ValueError: If no valid tables are provided to build the FastAPI application.
    """

    app = prepare_base_fastapi_app(name=name, description=description, version=version)

    routes = []

    for table in tables:
        try:
            routes.append(
                build_api_route(table=table, strict=strict, max_count=max_count)
            )
        except Exception as e:
            logger.error(
                "Error building API route for table '%s': %s",
                table.name,
                e,
            )
            continue
    if not routes:
        raise ValueError("No valid tables provided to build the FastAPI application.")

    app.routes.extend(routes)

    return app
