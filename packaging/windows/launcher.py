from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
APP_DIR = ROOT_DIR
COMPOSE_FILE = APP_DIR / "docker-compose.prod.yml"
ENV_FILE = APP_DIR / ".env"


def run_cmd(args: list[str]) -> int:
    process = subprocess.run(args, cwd=APP_DIR)
    return process.returncode


def ensure_env_file() -> None:
    if ENV_FILE.exists():
        return
    example = APP_DIR / ".env.example"
    if not example.exists():
        raise FileNotFoundError("Missing .env.example in installed app bundle.")
    ENV_FILE.write_text(example.read_text(), encoding="utf-8")


def docker_compose_cmd() -> list[str]:
    return [
        "docker",
        "compose",
        "--env-file",
        str(ENV_FILE),
        "-f",
        str(COMPOSE_FILE),
    ]


def up() -> int:
    ensure_env_file()
    return run_cmd(docker_compose_cmd() + ["up", "-d", "--build"])


def down() -> int:
    ensure_env_file()
    return run_cmd(docker_compose_cmd() + ["down"])


def status() -> int:
    ensure_env_file()
    return run_cmd(docker_compose_cmd() + ["ps"])


def logs() -> int:
    ensure_env_file()
    return run_cmd(docker_compose_cmd() + ["logs", "-f", "--tail", "100"])


def print_help() -> None:
    print(
        "Usage: ResearchWorkspaceLauncher.exe [up|down|status|logs]\\n"
        "  up      Start local stack (db, backend, frontend)\\n"
        "  down    Stop stack\\n"
        "  status  Show container status\\n"
        "  logs    Tail logs"
    )


def main() -> int:
    if len(sys.argv) == 1:
        return up()

    command = sys.argv[1].strip().lower()
    if command == "up":
        return up()
    if command == "down":
        return down()
    if command == "status":
        return status()
    if command == "logs":
        return logs()

    print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
