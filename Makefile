format:
	uv run ruff format .
fix:
	uv run ruff check --fix .
check:
	uv run ruff check .
test:
	uv run pytest -ssv