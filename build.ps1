# Builds dist\HEICViewer\HEICViewer.exe (standalone, no Python needed to run it).
$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot

$py = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path $py)) {
    Write-Error "Missing .venv - run: python -m venv .venv; .venv\Scripts\pip install -r requirements.txt"
}

& $py make_icon.py

& (Join-Path $PSScriptRoot '.venv\Scripts\pyinstaller.exe') `
    --noconfirm --clean --onedir --windowed `
    --name HEICViewer `
    --icon assets\heic.ico `
    heic_viewer.py

Write-Host "`nBuilt: dist\HEICViewer\HEICViewer.exe"
Write-Host "Next:  .\install.ps1  (registers .heic/.heif to open with it)"
