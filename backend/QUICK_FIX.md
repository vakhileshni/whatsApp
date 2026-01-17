# Quick Fix for passlib Import Error

## The Problem
Uvicorn's `--reload` feature on Windows spawns a subprocess that uses the system Python instead of your venv Python, causing `ModuleNotFoundError: No module named 'passlib'`.

## Solution

**Instead of running:**
```powershell
uvicorn main:app --reload --host 0.0.0.0 --port 4000
```

**Run this instead:**
```powershell
python -m uvicorn main:app --reload --host 0.0.0.0 --port 4000
```

This ensures uvicorn uses the Python from your activated venv.

## Alternative: Set PYTHONPATH

If the above doesn't work, set the PYTHONPATH environment variable:

```powershell
$env:PYTHONPATH = "$env:APPDATA\Python\Python313\site-packages"
python -m uvicorn main:app --reload --host 0.0.0.0 --port 4000
```

## Verify Installation

To verify passlib is installed in your venv:
```powershell
python -c "from passlib.context import CryptContext; print('OK')"
```
