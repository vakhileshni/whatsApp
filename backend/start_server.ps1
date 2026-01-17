# Start the FastAPI server using the correct virtual environment Python
Set-Location $PSScriptRoot

# Get the current venv Python (the one that's activated)
$venvPython = "$PSScriptRoot\venv\Scripts\python.exe"

# If that doesn't exist, try the alternative location
if (-not (Test-Path $venvPython)) {
    $venvPython = "C:\Users\rana\Desktop\WhatApp bussines\backend\venv\Scripts\python.exe"
}

# Set PYTHONPATH to include user site-packages (where system Python installs packages)
$userSitePackages = "$env:APPDATA\Python\Python313\site-packages"
if (Test-Path $userSitePackages) {
    $env:PYTHONPATH = $userSitePackages
}

# Start uvicorn with the venv Python
& $venvPython -m uvicorn main:app --reload --host 0.0.0.0 --port 4000
