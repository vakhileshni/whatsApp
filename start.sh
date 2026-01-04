#!/bin/bash
set -e

echo "==========================================="
echo "Starting WhatsApp Business Application"
echo "==========================================="
echo "Starting Backend API on port 4000..."
cd /app/backend
echo "Backend will be available at: http://0.0.0.0:4000"
echo "API Documentation: http://0.0.0.0:4000/docs"
echo ""
# Start backend (foreground process)
exec uvicorn main:app --host 0.0.0.0 --port 4000


