.PHONY: migrate migrate-status backend-dev frontend-dev

migrate:
	cd backend && python scripts/apply_migrations.py

migrate-status:
	cd backend && python scripts/apply_migrations.py --status

backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

frontend-dev:
	cd frontend && npm run dev
