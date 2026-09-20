# AccessGuard

IT Access Compliance and Dormancy Management portal for Service Desk and IT Operations teams.

AccessGuard helps organizations track employee access across multiple applications, identify dormant or expiring entitlements, and (in later phases) automate reminders, escalations, and compliance reporting.

## Problem statement

Employee access often remains active long after it is unused, expired, or overdue for recertification. Service Desk and IT Operations teams need a single place to:

- See who has access to which applications
- Identify dormant or soon-to-expire access
- Coordinate reminders and escalations
- Produce a defensible compliance trail

Spreadsheet tracking does not scale across applications, owners, and managers.

## Planned features

- Employee and application inventory
- Access records with last login, validation, and expiry dates
- Compliance status (GREEN / AMBER / RED / UNKNOWN)
- Dormancy and expiry detection
- Reminder and escalation workflows
- Compliance reporting
- Optional integrations (email, Microsoft Teams, ServiceNow)

CRUD dashboards, reminder engines, and integrations are **not implemented yet**. User and Application HTTP APIs are available.

## Technology stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- React Router

### Backend

- Python
- FastAPI
- Pydantic v2
- SQLAlchemy 2.x
- Alembic

### Database

- SQLite for local development (`DATABASE_URL` in `.env`)
- PostgreSQL may be used later

Schema changes are applied only through Alembic migrations. The API does not call `create_all()` on startup.

## Project structure

```text
.
├── README.md
├── .gitignore
├── backend/
│   ├── alembic.ini
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/          # migration scripts
│   ├── app/
│   │   ├── api/               # HTTP routers (health, users, applications)
│   │   ├── core/              # settings, enums, domain exceptions
│   │   ├── database/          # engine, session, declarative base
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   └── services/          # user and application CRUD services
│   ├── scripts/
│   │   └── seed.py            # optional development demo data
│   ├── tests/
│   ├── requirements.txt
│   ├── run.py
│   └── .env.example
└── frontend/
    ├── src/
    │   ├── api/
    │   ├── components/
    │   ├── hooks/
    │   ├── pages/
    │   └── types/
    ├── .env.example
    └── package.json
```

## Local setup

### Prerequisites

- Node.js 20+
- Python 3.12+
- `python3-venv` (on Debian/Ubuntu: `sudo apt install python3.12-venv`)

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

`.env` should include a SQLite URL, for example:

```env
DATABASE_URL=sqlite:///./accessguard.db
```

The SQLite file is created relative to the working directory you start the backend from (normally `backend/`).

### Create the local database (Alembic)

From `backend/` with the virtualenv active:

```bash
alembic upgrade head
```

This creates `accessguard.db` (gitignored) and the four core tables. Do not create tables by calling `Base.metadata.create_all()`.

### Optional seed data

The seed script is for local development only. It does **not** run when the API starts.

```bash
python scripts/seed.py
```

It inserts five fictional users, four applications (ServiceNow, CyberArk, Microsoft 365, Mainframe Access), access records, and one sample reminder-history row. Re-running it is idempotent for those demo keys.

### Start the API

```bash
python run.py
```

The API listens on [http://127.0.0.1:8472](http://127.0.0.1:8472). Confirm it is up:

```bash
curl http://127.0.0.1:8472/api/health
```

Expected response:

```json
{"status":"ok","application":"AccessGuard"}
```

`GET /api/health` does not require rows in the database.

### Backend tests

```bash
cd backend
source .venv/bin/activate
pytest
```

Tests run Alembic against a temporary SQLite file. They do not use your development `accessguard.db`.

### Frontend

In a second terminal:

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

The UI is served at [http://127.0.0.1:43123](http://127.0.0.1:43123).

`VITE_API_BASE_URL` in `frontend/.env` must point at the FastAPI origin (default `http://127.0.0.1:8472`). CORS on the backend is configured for the Vite dev origin.

The landing page is unchanged in Phase 3: it still shows **Backend Status: Connected / Disconnected**. There are no User or Application management screens yet.

### User and Application APIs

Interactive docs: [http://127.0.0.1:8472/docs](http://127.0.0.1:8472/docs) (Swagger UI) and [http://127.0.0.1:8472/redoc](http://127.0.0.1:8472/redoc).

`DELETE` on users and applications is a **soft delete**: the row stays in SQLite and `active` is set to `false`.

| Method | Path | Notes |
| --- | --- | --- |
| GET | `/api/users` | Query: `active`, `team`, `search`, `skip`, `limit` |
| GET | `/api/users/{user_id}` | 404 if missing |
| POST | `/api/users` | 201 created; 409 on duplicate `employee_id` or `email` |
| PUT | `/api/users/{user_id}` | Full replace |
| PATCH | `/api/users/{user_id}` | Partial update |
| DELETE | `/api/users/{user_id}` | Soft delete (`active=false`) |
| GET | `/api/applications` | Query: `active`, `criticality`, `search`, `skip`, `limit` |
| GET | `/api/applications/{application_id}` | 404 if missing |
| POST | `/api/applications` | 201 created; 409 on duplicate `name` |
| PUT | `/api/applications/{application_id}` | Full replace |
| PATCH | `/api/applications/{application_id}` | Partial update |
| DELETE | `/api/applications/{application_id}` | Soft delete (`active=false`) |

List pagination: `skip` defaults to `0`, `limit` defaults to `50`, maximum `limit` is `200`.

Example requests:

```bash
curl http://127.0.0.1:8472/api/users
curl "http://127.0.0.1:8472/api/users?active=true&team=Service%20Desk"
curl "http://127.0.0.1:8472/api/users?search=nishant&skip=0&limit=25"

curl -X POST http://127.0.0.1:8472/api/users \
  -H "Content-Type: application/json" \
  -d '{"employee_id":"EMP001","name":"Alex Morgan","email":"alex.morgan@example.com","team":"Service Desk"}'

curl -X PATCH http://127.0.0.1:8472/api/users/1 \
  -H "Content-Type: application/json" \
  -d '{"team":"Identity Operations"}'

curl -X DELETE http://127.0.0.1:8472/api/users/1

curl http://127.0.0.1:8472/api/applications
curl "http://127.0.0.1:8472/api/applications?criticality=HIGH&active=true"

curl -X POST http://127.0.0.1:8472/api/applications \
  -H "Content-Type: application/json" \
  -d '{"name":"ServiceNow","criticality":"HIGH","dormancy_threshold_days":45,"reminder_before_days":14}'
```

AccessRecord and ReminderHistory APIs are not implemented yet.


## Current status

### Phase 1 – Foundation (complete)

- Frontend and backend project layout
- FastAPI application with CORS for local development
- `GET /api/health`
- Landing page that reports backend **Connected** / **Disconnected**

### Phase 2 – Database & core data model (complete)

- SQLAlchemy 2.x models: User, Application, AccessRecord, ReminderHistory
- SQLite via `DATABASE_URL`
- Alembic initial migration
- Pydantic Base / Create / Replace / Update / Read schemas
- Optional development seed script
- Lightweight persistence tests

### Phase 3 – User & Application CRUD APIs (complete)

- REST APIs for users and applications
- Filtering, search, and offset pagination
- Duplicate handling with HTTP 409
- Soft delete (`active=false`)
- Swagger UI at `/docs`

Not started:

- Authentication
- AccessRecord / ReminderHistory APIs
- Inventory UI and dashboards
- CSV import
- Compliance calculation (status remains stored; default `UNKNOWN`)
- Reminder / escalation engines
- ServiceNow, Microsoft Teams, email, or AI features

## Roadmap

1. **Phase 1 – Foundation** (complete): project structure, health check, landing page
2. **Phase 2 – Data model** (complete): SQLite, SQLAlchemy entities, Alembic, seed data
3. **Phase 3 – User & Application APIs** (complete): CRUD, filters, soft delete
4. **Phase 4 – Access inventory**: AccessRecord APIs and management UI
5. **Phase 5 – Compliance**: dormancy/expiry evaluation and GREEN / AMBER / RED / UNKNOWN status
6. **Phase 6 – Operations**: reminders, escalations, and reporting
7. **Phase 7 – Integrations**: email, Teams, ServiceNow (as needed)

## License

No license has been selected yet. Treat the source as proprietary until a license file is added.
