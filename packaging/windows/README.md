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

## Launcher behavior

- Double-clicking the EXE opens a GUI with **Start / Stop / Status / Open Logs** buttons.
- CLI is also supported:
  - `ResearchWorkspaceLauncher.exe up`
  - `ResearchWorkspaceLauncher.exe down`
  - `ResearchWorkspaceLauncher.exe status`
  - `ResearchWorkspaceLauncher.exe logs`
  - `ResearchWorkspaceLauncher.exe gui`

The launcher auto-creates `.env` from `.env.example` on first run.
