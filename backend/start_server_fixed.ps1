# Start the FastAPI server with proper environment setup
Set-Location $PSScriptRoot

# Get the venv Python path
$venvPython = "C:\Users\rana\Desktop\WhatApp bussines\backend\venv\Scripts\python.exe"
$venvSitePackages = "C:\Users\rana\Desktop\WhatApp bussines\backend\venv\Lib\site-packages"

# Verify venv Python exists
if (-not (Test-Path $venvPython)) {
    Write-Host "Error: Virtual environment Python not found at: $venvPython" -ForegroundColor Red
    exit 1
}

# Set environment variables for subprocess
$env:PYTHONPATH = "$venvSitePackages;$PSScriptRoot"
$env:PYTHONHOME = Split-Path (Split-Path $venvPython -Parent) -Parent

# Also add user site-packages to PYTHONPATH (where system Python installs packages)
$userSitePackages = "$env:APPDATA\Python\Python313\site-packages"
if (Test-Path $userSitePackages) {
    $env:PYTHONPATH = "$env:PYTHONPATH;$userSitePackages"
}

Write-Host "Starting server with Python: $venvPython" -ForegroundColor Green
Write-Host "PYTHONPATH: $env:PYTHONPATH" -ForegroundColor Cyan

# Start uvicorn
& $venvPython -m uvicorn main:app --reload --host 0.0.0.0 --port 4000
