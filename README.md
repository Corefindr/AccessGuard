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

CRUD APIs, dashboards, reminder engines, and integrations are **not implemented yet**.

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
│   │   ├── api/               # HTTP routers (health only in Phase 1–2)
│   │   ├── core/              # settings and enums
│   │   ├── database/          # engine, session, declarative base
│   │   ├── models/            # SQLAlchemy models
│   │   ├── schemas/           # Pydantic schemas for future APIs
│   │   └── services/          # reserved for future business logic
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

The landing page is unchanged in Phase 2: it still shows **Backend Status: Connected / Disconnected**.

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
- Pydantic Base / Create / Read schemas (no CRUD routes yet)
- Optional development seed script
- Lightweight persistence tests

Not started:

- Authentication
- CRUD API routes and inventory UI
- Dashboard
- CSV import
- Compliance calculation (status remains stored; default `UNKNOWN`)
- Reminder / escalation engines
- ServiceNow, Microsoft Teams, email, or AI features

## Roadmap

1. **Phase 1 – Foundation** (complete): project structure, health check, landing page
2. **Phase 2 – Data model** (complete): SQLite, SQLAlchemy entities, Alembic, seed data
3. **Phase 3 – Access inventory**: CRUD and basic list/detail views
4. **Phase 4 – Compliance**: dormancy/expiry evaluation and GREEN / AMBER / RED / UNKNOWN status
5. **Phase 5 – Operations**: reminders, escalations, and reporting
6. **Phase 6 – Integrations**: email, Teams, ServiceNow (as needed)

## License

No license has been selected yet. Treat the source as proprietary until a license file is added.
