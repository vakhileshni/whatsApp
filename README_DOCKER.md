# Docker Setup for WhatsApp Business Application

This Docker setup automatically installs all dependencies and runs the backend API. Perfect for EC2 deployment!

## Prerequisites

- Docker installed on your system
- For EC2: Ensure security group allows inbound traffic on port 4000

## Quick Start

### 1. Build the Docker Image

```bash
docker build -t whatsapp-business-app .
```

### 2. Run with Docker Compose (Recommended)

```bash
docker-compose up
```

### 3. Run with Docker Run

```bash
docker run -d -p 4000:4000 --name whatsapp-app whatsapp-business-app
```

## Access Points

Once running, you can access:

- **Backend API**: http://localhost:4000 (or http://your-ec2-ip:4000)
- **API Documentation**: http://localhost:4000/docs

## View Logs

```bash
# Docker Compose
docker-compose logs -f

# Docker Run
docker logs -f whatsapp-app
```

## Stop the Container

```bash
# Docker Compose
docker-compose down

# Docker Run
docker stop whatsapp-app
docker rm whatsapp-app
```

## EC2 Deployment

### Steps for EC2:

1. **Launch EC2 Instance**
   - Choose Ubuntu 22.04 AMI
   - Configure security group to allow port 4000 (and 22 for SSH)

2. **SSH into EC2**
   ```bash
   ssh -i your-key.pem ubuntu@your-ec2-ip
   ```

3. **Install Docker on EC2**
   ```bash
   sudo apt update
   sudo apt install docker.io docker-compose -y
   sudo systemctl start docker
   sudo systemctl enable docker
   sudo usermod -aG docker ubuntu
   # Log out and back in for group changes to take effect
   ```

4. **Clone or upload Dockerfile**
   ```bash
   # Option 1: Clone your repo
   git clone https://github.com/vakhileshni/whatsApp.git
   cd whatsApp
   
   # Option 2: Upload Dockerfile manually
   ```

5. **Build and Run**
   ```bash
   docker build -t whatsapp-business-app .
   docker run -d -p 4000:4000 --name whatsapp-app --restart unless-stopped whatsapp-business-app
   ```

6. **Access Your API**
   - From anywhere: `http://your-ec2-public-ip:4000`
   - API Docs: `http://your-ec2-public-ip:4000/docs`

## What's Included

The Docker image includes:

- ✅ Ubuntu 22.04 base
- ✅ Python 3.10 with pip
- ✅ Node.js 20.x (required for Next.js 16)
- ✅ Git
- ✅ All backend Python dependencies (from `backend/requirements.txt`)
- ✅ All frontend npm packages (from `frontend/package.json`)
- ✅ Automatic startup of backend on port 4000

## Notes

- The backend runs on port 4000 inside the container
- Make sure your EC2 security group allows inbound traffic on port 4000
- The frontend is installed but not started by default (backend API only)
- All code is cloned from: https://github.com/vakhileshni/whatsApp.git
- The container automatically restarts if it crashes (with `--restart unless-stopped`)


