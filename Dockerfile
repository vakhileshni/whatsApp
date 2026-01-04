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
RUN npm install --legacy-peer-deps

# Create startup script
RUN printf '#!/bin/bash\n\
set -e\n\
\n\
echo "==========================================="\n\
echo "Starting WhatsApp Business Application"\n\
echo "==========================================="\n\
echo "Starting Backend API on port 4000..."\n\
cd /app/backend\n\
echo "Backend will be available at: http://0.0.0.0:4000"\n\
echo "API Documentation: http://0.0.0.0:4000/docs"\n\
echo ""\n\
# Start backend (foreground process)\n\
exec uvicorn main:app --host 0.0.0.0 --port 4000\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port
EXPOSE 4000

# Set working directory
WORKDIR /app

# Start script
CMD ["/app/start.sh"]

