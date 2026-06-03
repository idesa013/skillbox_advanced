# Cookbook API

Async FastAPI service for a recipe book. It uses SQLAlchemy with SQLite and
includes tests plus CI quality gates.

## Run locally

```bash
python -m pip install -r requirements.txt
uvicorn cookbook.main:app --app-dir src --reload
```

Interactive documentation is available at `/docs` and `/redoc`.

## Checks

```bash
python -m pytest
python -m mypy
python -m black --check src tests
python -m isort --check-only src tests
python -m flake8 src tests
```

GitHub Actions runs the same checks on every push and pull request.

