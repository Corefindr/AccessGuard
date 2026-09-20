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

These capabilities are **not implemented yet**. This repository currently contains the project foundation only.

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
- Pydantic

### Database (later)

- SQLite initially
- PostgreSQL may be used later

SQLAlchemy models, persistence, and compliance logic are deferred to a later phase.

## Project structure

```text
.
├── README.md
├── .gitignore
├── backend/
│   ├── app/
│   │   ├── api/            # HTTP routers
│   │   ├── core/           # settings and shared configuration
│   │   ├── models/         # reserved for future SQLAlchemy models
│   │   ├── schemas/        # reserved for future Pydantic schemas
│   │   └── services/       # reserved for future business logic
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

## Current status

**Phase 1 – Foundation**

Shipped:

- Frontend and backend project layout
- FastAPI application with CORS for local development
- `GET /api/health`
- Landing page that reports backend **Connected** / **Disconnected**

Not started:

- Authentication
- Database tables and SQLAlchemy models
- CRUD
- Dashboard
- CSV import
- Reminder / escalation engines
- ServiceNow, Microsoft Teams, email, or AI features

## Roadmap

1. **Phase 1 – Foundation** (current): project structure, health check, landing page
2. **Phase 2 – Data model**: SQLite, SQLAlchemy entities (User, Application, AccessRecord, ReminderHistory)
3. **Phase 3 – Access inventory**: CRUD and basic list/detail views
4. **Phase 4 – Compliance**: dormancy/expiry evaluation and GREEN / AMBER / RED / UNKNOWN status
5. **Phase 5 – Operations**: reminders, escalations, and reporting
6. **Phase 6 – Integrations**: email, Teams, ServiceNow (as needed)

## License

No license has been selected yet. Treat the source as proprietary until a license file is added.
