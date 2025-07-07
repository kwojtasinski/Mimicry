format:
	uv run ruff format .
fix:
	uv run ruff check --fix .
check:
	uv run ruff check .
unit-tests:
	uv run pytest -m unit
integration-tests:
	uv run pytest -m integration
test:
	uv run pytest
docs-serve:
	uv run mkdocs serve