# Backend (FastAPI + PostgreSQL)

## Run (development)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/apply_migrations.py
uvicorn app.main:app --reload --port 8000
```

## Migration commands

```bash
python scripts/apply_migrations.py
python scripts/apply_migrations.py --status
```

## Run (production)

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
```

In containerized deployment, migrations run at startup before launching uvicorn.

## Key API groups

- Auth: `/auth/*`
- Ingestion: `/ingestion/*`
- Literature reviews: `/literature-reviews/*`
- Research/suggestions: `/research/*`
- Embedded apps: `/embedded-apps/*`
- Learning tracker: `/learning-tracker/*`
- AI endpoints: `/ai/project-ideas/*`, `/ai/learning-coach/*`

## Security controls

- Embedded URL validation (https-only, domain allowlist, localhost/private-network blocking)
- User-scoped data access checks for source/research records
- In-memory rate limiting for AI/suggestion endpoints
- Prompt and output debug logging to `ai_evaluation_logs`
