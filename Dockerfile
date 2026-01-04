# Multi-stage Dockerfile for WhatsApp Business SaaS
FROM ubuntu:22.04

# Avoid interactive prompts during installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies and programming languages
RUN apt-get update && apt-get install -y \
    python3.10 \
    python3-pip \
    python3-venv \
    git \
    curl \
    wget \
    ca-certificates \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js 20.x (required for Next.js 16)
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs

# Create app directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/vakhileshni/whatsApp.git .

# Install Python dependencies (Backend)
WORKDIR /app/backend
RUN pip3 install --no-cache-dir -r requirements.txt

# Install Node.js dependencies (Frontend)
WORKDIR /app/frontend

# Allow setting API URL at build time (defaults to localhost:4000)
ARG NEXT_PUBLIC_API_URL=http://localhost:4000
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL}

RUN npm install --legacy-peer-deps

# Build frontend for production
RUN npm run build

# Create startup script
RUN printf '#!/bin/bash\n\
set -e\n\
\n\
echo "==========================================="\n\
echo "Starting WhatsApp Business Application"\n\
echo "==========================================="\n\
\n\
# Start backend in background\n\
echo "🚀 Starting Backend API on port 4000..."\n\
cd /app/backend\n\
uvicorn main:app --host 0.0.0.0 --port 4000 &\n\
BACKEND_PID=$!\n\
\n\
# Wait for backend to start\n\
sleep 3\n\
\n\
# Start frontend in background\n\
echo "🚀 Starting Frontend on port 3000..."\n\
cd /app/frontend\n\
npm start -- -p 3000 &\n\
FRONTEND_PID=$!\n\
\n\
echo ""\n\
echo "✅ Services started:"\n\
echo "   Backend API: http://0.0.0.0:4000"\n\
echo "   API Docs: http://0.0.0.0:4000/docs"\n\
echo "   Frontend: http://0.0.0.0:3000"\n\
echo ""\n\
echo "Press Ctrl+C to stop all services"\n\
\n\
# Wait for processes\n\
wait $BACKEND_PID $FRONTEND_PID\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose ports
EXPOSE 3000 4000

# Set working directory
WORKDIR /app

# Start script
CMD ["/app/start.sh"]

