# Windows .exe Installer Build

This folder builds a Windows launcher EXE and wraps it into a Windows installer.

## Prerequisites (on Windows)

- Python 3.11+
- Docker Desktop (with Docker Compose)
- Inno Setup 6 (`iscc` available in PATH)

## Build steps

From PowerShell:

```powershell
cd packaging/windows
./create_installer.ps1
```

Outputs:
- `packaging/windows/dist/ResearchWorkspaceLauncher.exe`
- `packaging/windows/dist-installer/ResearchWorkspaceInstaller.exe`

## What the launcher does

The installed launcher executes Docker Compose commands against `docker-compose.prod.yml`:

- `ResearchWorkspaceLauncher.exe up` (default if no arg)
- `ResearchWorkspaceLauncher.exe down`
- `ResearchWorkspaceLauncher.exe status`
- `ResearchWorkspaceLauncher.exe logs`

It auto-creates `.env` from `.env.example` on first run.
