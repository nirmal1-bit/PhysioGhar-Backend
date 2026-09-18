# PhysioGhar Backend

FastAPI backend for the PhysioGhar therapist and patient application. The API
supports authentication, therapist profiles, weekly availability, bookings,
patient records, session notes, and complaints.

## Technology

- Python 3.12+
- FastAPI and Uvicorn
- PostgreSQL
- SQLAlchemy Core with Psycopg 3 (raw SQL; no ORM)
- Alembic migrations
- JWT authentication
- Bcrypt password hashing
- Cloudinary profile-image storage
- `uv` for dependency and virtual-environment management

## Local setup

### Requirements

- Python 3.12 or newer
- PostgreSQL
- `uv`

Create the local database if it does not already exist:

```bash
createdb physioghar
```

Install dependencies and create the virtual environment:

```bash
uv sync
```

Create `.env` from `.env.example` and update the values for the local
environment:

```bash
cp .env.example .env
```

At minimum, configure `DATABASE_URL` and replace the development
`JWT_SECRET_KEY`. Cloudinary values are required for profile image uploads.
Never commit `.env`, API secrets, SSH keys, or server-address files.

## Database migrations

Apply all migrations:

```bash
uv run alembic upgrade head
```

The current migration chain creates:

1. Shared `users` table for therapist and patient accounts
2. Therapist `profiles`
3. Weekly therapist availability and schedule slots
4. Therapist-scoped patient records
5. Patient session notes
6. Therapist complaints

Create a new migration with:

```bash
uv run alembic revision -m "describe the change"
```

## Run the API

Development server:

```bash
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Useful URLs when running locally:

- Health: `http://127.0.0.1:8000/api/v1/health`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`

For a physical device on the same network, use the development machine's LAN
address instead of `127.0.0.1`.

## Authentication

Register with `POST /api/v1/auth/register` and log in with
`POST /api/v1/auth/login`.

The login response contains a JWT access token and the backend user type:

```json
{
  "access_token": "<token>",
  "token_type": "bearer",
  "user_type": "therapist"
}
```

Send the token on protected requests:

```http
Authorization: Bearer <token>
```

Authorization is derived from the signed JWT on the server. Therapist-only
operations do not trust a role supplied by the client request body.

## API endpoints

All endpoints are prefixed with `/api/v1`.

### Authentication

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| POST | `/auth/register` | Public | Create a therapist or patient account |
| POST | `/auth/login` | Public | Authenticate and receive a JWT |

### Therapist profile

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/profile` | Therapist | Read the current therapist profile |
| POST | `/profile` | Therapist | Create a profile, optionally with an image |
| PUT | `/profile` | Therapist | Update profile details and optionally replace the image |

Profile image requests use `multipart/form-data` and are uploaded to
Cloudinary. Images are limited to 5 MB.

### Dashboard and availability

The dashboard combines booking and availability data on the client.

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/schedule/availability` | Therapist | Read global availability |
| PUT | `/schedule/availability` | Therapist | Enable or disable booking availability |
| GET | `/schedule?date=YYYY-MM-DD` | Therapist | Read the selected weekly schedule |
| POST | `/schedule/slots` | Therapist | Add a recurring weekday time slot |
| PATCH | `/schedule/slots/{slot_id}?date=YYYY-MM-DD` | Therapist | Change a slot to open or blocked |

Schedule slots are defined by day of week and are materialized for the selected
week. A booked slot is read-only while a recurring open slot can be blocked or
unblocked.

### Bookings

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/bookings/available-therapists?date=YYYY-MM-DD` | Public | List therapists with available slots |
| GET | `/bookings/therapists/{therapist_id}/available-slots?date=YYYY-MM-DD` | Public | List available slots for a therapist |
| POST | `/bookings` | Public | Create a patient booking request |
| GET | `/bookings/therapist` | Therapist | List the current therapist's bookings |
| PATCH | `/bookings/{booking_id}/status` | Therapist | Accept, decline, complete, or cancel a booking |
| PATCH | `/bookings/{booking_id}/reschedule` | Therapist | Move a booking to another available slot |
| PATCH | `/bookings/{booking_id}/notes` | Therapist | Save therapist remarks for a session |

Booking creation reserves the requested slot transactionally and rejects an
already-booked slot with a conflict response.

### Patient records and notes

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/patients` | Therapist | List the therapist's patients |
| POST | `/patients` | Therapist | Create a patient record |
| GET | `/patients/{patient_id}` | Therapist | Read details, sessions, and notes |
| PUT | `/patients/{patient_id}` | Therapist | Update a patient record |
| DELETE | `/patients/{patient_id}` | Therapist | Delete a patient record |
| POST | `/patients/{patient_id}/notes` | Therapist | Add a session note |
| PUT | `/patients/{patient_id}/notes/{note_id}` | Therapist | Edit a session note |

Notes can only be created for patients who have an accepted or completed
session with the therapist.

### Complaints

| Method | Endpoint | Access | Purpose |
| --- | --- | --- | --- |
| GET | `/complaints` | Therapist | List submitted complaints |
| POST | `/complaints` | Therapist | Submit a complaint to the PhysioGhar admin |

Complaint categories are `patient_issue`, `booking_issue`, `payment_issue`,
`technical_issue`, and `other`.

## Project structure

```text
app/
├── api/                 # API versioning and router registration
├── core/                # Settings, database, security, and Cloudinary
└── features/
    ├── auth/            # Registration, login, JWT creation
    ├── booking/         # Availability discovery and booking lifecycle
    ├── complaint/       # Therapist complaints
    ├── dashboard/       # Dashboard API namespace
    ├── patient/         # Patient records and session notes
    ├── profile/         # Therapist profile and image upload
    └── schedule/        # Weekly availability and schedule slots

migrations/              # Alembic migration history
pyproject.toml           # Dependencies and Ruff configuration
uv.lock                  # Reproducible dependency lockfile
```

Each feature keeps HTTP routing, validation schemas, service logic, and raw
SQL repository logic separate. Database writes use connection transactions;
read queries use async connections.

## Production deployment

The production server runs the same source project rather than a compiled
binary:

```bash
uv sync
uv run alembic upgrade head
uv run uvicorn app.main:app --host 127.0.0.1 --port 4001
```

`systemd` keeps Uvicorn running, while Caddy terminates HTTPS and reverse
proxies `prod.creativeinkflow.tech` to the local API port. Caddy manages the
TLS certificate automatically.

Production secrets are stored only in the server's protected `.env` file and
are not part of this repository.

## Code quality

Run the backend checks with:

```bash
uv run ruff check .
uv run python -m compileall -q app migrations
```

## Assignment assumptions

- The assignment's primary workflow is the therapist application; patient
  booking support is included for the end-to-end booking flow.
- Therapist authorization is enforced from the signed JWT user type.
- Patient notes are linked to a therapist-patient session and are unavailable
  before an accepted or completed booking.
- Profile account name and email are sourced from the shared `users` table;
  therapist profile records store professional details and contact/profile
  information.
- Complaint administration/replies are outside the assignment scope. The API
  persists therapist submissions and exposes their current status for future
  admin tooling.
