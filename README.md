# PhysioGhar Backend

FastAPI backend for the PhysioGhar therapist application.

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

`uv sync` creates or updates the project virtual environment from
`pyproject.toml` and `uv.lock`.

## Run the API

```bash
uv run uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`.

- Health check: `GET /api/v1/health`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

## Code quality

```bash
uv run ruff check .
```

## Structure

```text
app/
  api/          HTTP routing and API versioning
  core/         Configuration and shared infrastructure
  features/     Feature modules such as dashboard, bookings, and patients
```
