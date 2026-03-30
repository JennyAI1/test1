# Research Workspace

A full-stack research workspace prototype with a FastAPI backend, Next.js frontend, PostgreSQL migrations, and AI-assisted workflows.

## Stack
- Frontend: Next.js + TipTap
- Backend: FastAPI + SQLAlchemy
- DB: PostgreSQL

## Environment setup

```bash
cp .env.example .env
```

Update secrets and URLs before running/deploying.

## Migration commands

```bash
make migrate
make migrate-status
```

Or directly:

```bash
cd backend
python scripts/apply_migrations.py
python scripts/apply_migrations.py --status
```

## Local development

```bash
docker compose up -d db

cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/apply_migrations.py
uvicorn app.main:app --reload --port 8000

cd ../frontend
npm install
NEXT_PUBLIC_API_URL=http://localhost:8000 npm run dev
```

## Production deployment

Use Docker Compose production config:

```bash
docker compose --env-file .env -f docker-compose.prod.yml up -d --build
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for full production instructions.

## Windows `.exe` installer

A Windows installer pipeline is included under `packaging/windows/`.

On a Windows machine (PowerShell):

```powershell
cd packaging/windows
./create_installer.ps1
```

This produces:
- `packaging/windows/dist/ResearchWorkspaceLauncher.exe`
- `packaging/windows/dist-installer/ResearchWorkspaceInstaller.exe`

The EXE now opens a desktop GUI launcher by default (Start/Stop/Status/Open Logs).
