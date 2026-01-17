@echo off
REM Start the FastAPI server using the correct virtual environment Python
cd /d "%~dp0"

REM Set environment variables to ensure subprocess uses venv Python
set "PYTHONPATH=C:\Users\rana\Desktop\WhatApp bussines\backend\venv\Lib\site-packages"
set "PYTHONHOME=C:\Users\rana\Desktop\WhatApp bussines\backend\venv"

REM Start uvicorn with the venv Python
"C:\Users\rana\Desktop\WhatApp bussines\backend\venv\Scripts\python.exe" -m uvicorn main:app --reload --host 0.0.0.0 --port 4000
