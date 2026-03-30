from __future__ import annotations

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


def open_logs_terminal() -> int:
    ensure_env_file()
    cmd = (
        f'docker compose --env-file "{ENV_FILE}" -f "{COMPOSE_FILE}" '
        "logs -f --tail 100"
    )
    return subprocess.Popen(["cmd", "/c", "start", "cmd", "/k", cmd], cwd=APP_DIR).returncode


def print_help() -> None:
    print(
        "Usage: ResearchWorkspaceLauncher.exe [up|down|status|logs|gui]\n"
        "  up      Start local stack (db, backend, frontend)\n"
        "  down    Stop stack\n"
        "  status  Show container status\n"
        "  logs    Tail logs\n"
        "  gui     Open desktop launcher UI"
    )


def run_gui() -> int:
    import tkinter as tk
    from tkinter import messagebox

    root = tk.Tk()
    root.title("Research Workspace Launcher")
    root.geometry("420x260")

    status_var = tk.StringVar(value="Ready")

    def do_action(fn, success_message: str) -> None:
        try:
            rc = fn()
            if rc == 0:
                status_var.set(success_message)
            else:
                status_var.set(f"Command exited with code {rc}")
                messagebox.showwarning("Research Workspace", f"Command exited with code {rc}")
        except Exception as exc:  # noqa: BLE001
            status_var.set(str(exc))
            messagebox.showerror("Research Workspace", str(exc))

    tk.Label(root, text="Research Workspace", font=("Segoe UI", 16, "bold")).pack(pady=(16, 4))
    tk.Label(root, text="Control your local Dockerized stack", font=("Segoe UI", 10)).pack(pady=(0, 12))

    button_frame = tk.Frame(root)
    button_frame.pack(pady=8)

    tk.Button(button_frame, text="Start", width=14, command=lambda: do_action(up, "Stack started.")).grid(row=0, column=0, padx=6, pady=6)
    tk.Button(button_frame, text="Stop", width=14, command=lambda: do_action(down, "Stack stopped.")).grid(row=0, column=1, padx=6, pady=6)
    tk.Button(button_frame, text="Status", width=14, command=lambda: do_action(status, "Status printed in console.")).grid(row=1, column=0, padx=6, pady=6)
    tk.Button(button_frame, text="Open Logs", width=14, command=lambda: do_action(open_logs_terminal, "Logs opened in terminal window.")).grid(row=1, column=1, padx=6, pady=6)

    tk.Label(root, textvariable=status_var, fg="#444", wraplength=380).pack(pady=(10, 8))
    tk.Button(root, text="Exit", width=12, command=root.destroy).pack(pady=(0, 12))

    root.mainloop()
    return 0


def main() -> int:
    if len(sys.argv) == 1:
        return run_gui()

    command = sys.argv[1].strip().lower()
    if command == "up":
        return up()
    if command == "down":
        return down()
    if command == "status":
        return status()
    if command == "logs":
        return logs()
    if command == "gui":
        return run_gui()

    print_help()
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
