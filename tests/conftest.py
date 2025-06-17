import pathlib
from typing import Iterator
import requests

from kafka import KafkaAdminClient
import pytest
from pytest_docker import Services
import psycopg2

from mimicry.core import load_table_config
from mimicry.models import (
    DeltaLakeSinkConfiguration,
    DuckDBSinkConfiguration,
    IcebergSinkConfiguration,
    KafkaSinkConfiguration,
    PostgresSinkConfiguration,
    SinkConfiguration,
    TableConfiguration,
)

STATIC_PATH = pathlib.Path(__file__).parent / "static"


def is_kafka_responsive(docker_ip, kafka_port):
    """
    Check if the Kafka broker is responsive by attempting to connect and list topics.

    Args:
        docker_ip (str): The IP address of the Docker host running Kafka.
        kafka_port (int): The port number on which Kafka is exposed.

    Returns:
        bool: True if Kafka is responsive, False otherwise.

    Raises:
        None: All exceptions are caught and handled internally.
    """
    try:
        client = KafkaAdminClient(
            bootstrap_servers=f"{docker_ip}:{kafka_port}",
            client_id="test-healthcheck-client",
            request_timeout_ms=2000,
        )
        client.list_topics()
        client.close()
        return True
    except Exception:
        return False


def is_postgres_responsive(docker_ip, postgres_port):
    """
    Check if the Postgres database is responsive by attempting to connect.

    Args:
        docker_ip (str): The IP address of the Docker host running Postgres.
        postgres_port (int): The port number on which Postgres is exposed.

    Returns:
        bool: True if Postgres is responsive, False otherwise.

    Raises:
        None: All exceptions are caught and handled internally.
    """
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="postgres",
            host=docker_ip,
            port=postgres_port,
        )
        conn.close()
        return True
    except Exception:
        return False


def is_minio_ready(docker_ip: str, minio_port: int) -> bool:
    """
    Check if the MinIO container is ready by making an HTTP GET request to its health endpoint.

    Args:
        docker_ip (str): The IP address of the Docker host running MinIO.
        minio_port (int): The port number on which MinIO is exposed.

    Returns:
        bool: True if MinIO is ready, False otherwise.

    Raises:
        None: All exceptions are caught and handled internally.
    """
    try:
        response = requests.get(
            f"http://{docker_ip}:{minio_port}/minio/health/live", timeout=5
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException as e:
        print(e)
        return False


def is_iceberg_rest_ready(docker_ip: str, docker_port: int) -> bool:
    """
    Check if the Apache Iceberg REST fixture container is ready by polling its config endpoint.

    Args:
        docker_ip (str): The IP address of the Docker host running Iceberg REST.
        docker_port (int): The port number on which Iceberg REST is exposed.

    Returns:
        bool: True if the service is ready, False otherwise.

    Raises:
        None: All exceptions are caught and handled internally.
    """
    try:
        response = requests.get(
            f"http://{docker_ip}:{docker_port}/v1/config", timeout=5
        )
        response.raise_for_status()
        return True
    except requests.exceptions.RequestException:
        return False


@pytest.fixture
def sample_people_table_config() -> TableConfiguration:
    """
    Fixture providing a sample TableConfiguration loaded from a static YAML file.

    Returns:
        TableConfiguration: The loaded table configuration.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        Exception: If loading the configuration fails.
    """
    return load_table_config(
        STATIC_PATH / "people.yaml",
    )


@pytest.fixture
def sample_people_deltalake_sink_config(tmpdir) -> SinkConfiguration:
    """
    Fixture providing a sample DeltaLakeSinkConfiguration for testing.

    Args:
        tmpdir (py.path.local): Temporary directory provided by pytest.

    Returns:
        SinkConfiguration: The DeltaLake sink configuration.

    Raises:
        None
    """
    return SinkConfiguration(
        configuration=DeltaLakeSinkConfiguration(
            path=str(tmpdir / "people"),
        ),
    )


@pytest.fixture
def sample_people_duckdb_sink_config(tmpdir) -> SinkConfiguration:
    """
    Fixture providing a sample DuckDBSinkConfiguration for testing.

    Args:
        tmpdir (py.path.local): Temporary directory provided by pytest.

    Returns:
        SinkConfiguration: The DuckDB sink configuration.

    Raises:
        None
    """
    return SinkConfiguration(
        configuration=DuckDBSinkConfiguration(
            path=str(tmpdir / "people"),
            table_name="people",
        ),
    )


@pytest.fixture
def sample_people_kafka_sink_config(
    docker_ip: str, docker_services: Iterator[Services]
) -> SinkConfiguration:
    """
    Fixture providing a sample KafkaSinkConfiguration for testing.

    Args:
        docker_ip (str): The IP address of the Docker host running Kafka.
        docker_services (Iterator[Services]): Docker services fixture.

    Returns:
        SinkConfiguration: The Kafka sink configuration.

    Raises:
        None
    """
    bootstrap_server = f"{docker_ip}:{docker_services.port_for('kafka', 9092)}"
    return SinkConfiguration(
        configuration=KafkaSinkConfiguration(
            topic="people",
            producer_config={
                "bootstrap_servers": [bootstrap_server],
            },
        ),
    )


@pytest.fixture(scope="session")
def sample_people_postgres_sink_config(
    docker_ip: str, docker_services: Iterator[Services]
) -> SinkConfiguration:
    """
    Fixture providing a sample PostgresSinkConfiguration for testing.

    Args:
        docker_ip (str): The IP address of the Docker host running Postgres.
        docker_services (Iterator[Services]): Docker services fixture.

    Returns:
        SinkConfiguration: The Postgres sink configuration.

    Raises:
        None
    """
    return SinkConfiguration(
        configuration=PostgresSinkConfiguration(
            connection_string=f"postgresql://postgres:postgres@{docker_ip}:{docker_services.port_for('postgres', 5432)}/postgres",
            table_name="people",
        ),
    )


@pytest.fixture(scope="session")
def sample_people_iceberg_sink_config(
    docker_ip: str, docker_services: Iterator[Services]
) -> SinkConfiguration:
    """
    Fixture providing a sample IcebergSinkConfiguration for testing.

    Args:
        docker_ip (str): The IP address of the Docker host running Iceberg REST and MinIO.
        docker_services (Iterator[Services]): Docker services fixture.

    Returns:
        SinkConfiguration: The Iceberg sink configuration.

    Raises:
        None
    """
    return SinkConfiguration(
        configuration=IcebergSinkConfiguration(
            table_name="test.people",
            catalog_properties={
                "uri": f"http://{docker_ip}:{docker_services.port_for('iceberg', 8181)}",
                "s3.endpoint": f"http://{docker_ip}:{docker_services.port_for('minio', 9000)}",
                "py-io-impl": "pyiceberg.io.pyarrow.PyArrowFileIO",
                "s3.access-key-id": "admin",
                "s3.secret-access-key": "password",
            },
        )
    )


@pytest.fixture(scope="session")
def kafka_is_ready(docker_ip, docker_services: Iterator[Services]):
    """
    Session-scoped fixture that waits until Kafka is ready to accept connections.

    Args:
        docker_ip (str): The IP address of the Docker host running Kafka.
        docker_services (Iterator[Services]): Docker services fixture.

    Returns:
        None

    Raises:
        TimeoutError: If Kafka does not become responsive within the timeout.
    """
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=1.0,
        check=lambda: is_kafka_responsive(
            docker_ip,
            docker_services.port_for("kafka", 9092),
        ),
    )


@pytest.fixture(scope="session")
def postgres_is_ready(docker_ip: str, docker_services: Iterator[Services]):
    """
    Session-scoped fixture that waits until Postgres is ready to accept connections.

    Args:
        docker_ip (str): The IP address of the Docker host running Postgres.
        docker_services (Iterator[Services]): Docker services fixture.

    Returns:
        None

    Raises:
        TimeoutError: If Postgres does not become responsive within the timeout.
    """
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=1.0,
        check=lambda: is_postgres_responsive(
            docker_ip,
            docker_services.port_for("postgres", 5432),
        ),
    )


@pytest.fixture(scope="session")
def iceberg_is_ready(docker_ip: str, docker_services: Iterator[Services]) -> None:
    """
    Session-scoped fixture that waits until the Iceberg REST service is ready.

    Args:
        docker_ip (str): The IP address of the Docker host running Iceberg REST.
        docker_services (Iterator[Services]): Docker services fixture.

    Returns:
        None

    Raises:
        TimeoutError: If Iceberg REST does not become responsive within the timeout.
    """
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=1.0,
        check=lambda: is_iceberg_rest_ready(
            docker_ip,
            docker_services.port_for("iceberg", 8181),
        ),
    )


@pytest.fixture(scope="session")
def minio_is_ready(docker_ip: str, docker_services: Iterator[Services]) -> None:
    """
    Session-scoped fixture that waits until MinIO is ready.

    Args:
        docker_ip (str): The IP address of the Docker host running MinIO.
        docker_services (Iterator[Services]): Docker services fixture.

    Returns:
        None

    Raises:
        TimeoutError: If MinIO does not become responsive within the timeout.
    """
    docker_services.wait_until_responsive(
        timeout=30.0,
        pause=1.0,
        check=lambda: is_minio_ready(
            docker_ip,
            docker_services.port_for("minio", 9000),
        ),
    )
