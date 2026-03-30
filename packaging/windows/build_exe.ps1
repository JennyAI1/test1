$ErrorActionPreference = "Stop"

python -m pip install --upgrade pip
python -m pip install pyinstaller

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Resolve-Path (Join-Path $scriptDir "../..")
$launcherPath = Join-Path $scriptDir "launcher.py"

pyinstaller `
  --noconfirm `
  --clean `
  --onefile `
  --name ResearchWorkspaceLauncher `
  --distpath (Join-Path $scriptDir "dist") `
  $launcherPath

Write-Host "EXE created at: $scriptDir/dist/ResearchWorkspaceLauncher.exe"
