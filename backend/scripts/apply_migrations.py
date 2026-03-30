from __future__ import annotations

import argparse
from pathlib import Path
import sys

from sqlalchemy import text

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.db.database import engine


def _ensure_migration_table(conn) -> None:
    conn.execute(
        text(
            """
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version TEXT PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )


def _get_applied_versions(conn) -> set[str]:
    rows = conn.execute(text("SELECT version FROM schema_migrations")).fetchall()
    return {row[0] for row in rows}


def run(show_status: bool = False) -> None:
    migrations_dir = BACKEND_DIR / "migrations"
    migration_files = sorted(migrations_dir.glob("*.sql"))

    with engine.begin() as conn:
        _ensure_migration_table(conn)
        applied = _get_applied_versions(conn)

        pending = [m for m in migration_files if m.stem not in applied]

        if show_status:
            print("Applied migrations:")
            for migration in migration_files:
                status = "applied" if migration.stem in applied else "pending"
                print(f"  - {migration.stem}: {status}")
            print(f"\nPending count: {len(pending)}")
            return

        if not pending:
            print("No pending migrations.")
            return

        for migration in pending:
            sql = migration.read_text()
            conn.execute(text(sql))
            conn.execute(
                text("INSERT INTO schema_migrations (version) VALUES (:version)"),
                {"version": migration.stem},
            )
            print(f"Applied migration: {migration.stem}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Apply SQL migrations to the configured database.")
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show migration status without applying pending migrations.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    run(show_status=args.status)
