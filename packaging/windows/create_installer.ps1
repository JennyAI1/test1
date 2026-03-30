$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $scriptDir

& "$scriptDir/build_exe.ps1"

if (-not (Get-Command iscc -ErrorAction SilentlyContinue)) {
  throw "Inno Setup Compiler (iscc) not found. Install Inno Setup and ensure iscc is on PATH."
}

iscc "$scriptDir/ResearchWorkspace.iss"

Write-Host "Installer created under $scriptDir/dist-installer"
Pop-Location
