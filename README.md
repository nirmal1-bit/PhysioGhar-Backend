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
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API is available on all network interfaces at port `8000`. For a physical
device connected to the same network, use the development machine's LAN IP,
for example `http://10.235.75.138:8000`.

- Health check: `GET /api/v1/health`
- Register therapist: `POST /api/v1/auth/register`
- Login therapist: `POST /api/v1/auth/login`
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
  core/         Configuration and database infrastructure
  features/     Feature modules such as auth, dashboard, bookings, and patients
  migrations/   Versioned PostgreSQL schema migrations
```

## PostgreSQL

The application uses SQLAlchemy Core with Psycopg 3; it does not use an ORM.
The local connection URL uses the existing `postgres` role:

```env
DATABASE_URL=postgresql+psycopg://postgres@localhost/physioghar?sslmode=disable
```

Run migrations with:

```bash
uv run alembic upgrade head
```
