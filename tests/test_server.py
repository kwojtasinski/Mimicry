from fastapi.testclient import TestClient

from mimicry.models import TableConfiguration
from mimicry.server import build_fastapi_app


def test_simple_server_works_as_expected(
    sample_people_table_config: TableConfiguration,
) -> None:
    app = build_fastapi_app(
        sample_people_table_config,
        strict=True,
        name=f"API for {sample_people_table_config.name}",
        description="Test API",
        max_count=10,
    )
    client = TestClient(app)
    response = client.get(
        f"/tables/{sample_people_table_config.name}", params={"count": 10}
    )
    expected_field_names = [field.name for field in sample_people_table_config.fields]
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 10
    assert all([list(item.keys()) == expected_field_names for item in response.json()])
