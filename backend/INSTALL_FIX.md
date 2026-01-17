# Installation Fix for Python 3.13

## Problem
`psycopg2-binary==2.9.9` doesn't have pre-built wheels for Python 3.13, causing build errors.

## Solution
Upgraded to `psycopg2-binary>=2.9.10` which has Python 3.13 support.

## What Was Fixed

1. **Updated requirements.txt**: Changed `psycopg2-binary==2.9.9` to `psycopg2-binary>=2.9.10`
2. **Installed newer version**: `psycopg2-binary-2.9.11` now supports Python 3.13

## Verify Installation

```bash
cd backend
python -c "import sqlalchemy; import psycopg2; print('OK')"
```

## If You Still Have Issues

### Option 1: Use psycopg (newer alternative)
```bash
pip install psycopg[binary]
```

Then update `backend/database.py` to use:
```python
# Change from:
DATABASE_URL = "postgresql://..."

# To:
DATABASE_URL = "postgresql+psycopg://..."
```

### Option 2: Use Python 3.11 or 3.12
Python 3.13 is very new. Many packages have better support for 3.11/3.12:
```bash
# Create virtual environment with Python 3.11 or 3.12
python3.11 -m venv venv
```

## Status
✅ Fixed - psycopg2-binary-2.9.11 installed successfully
