# EC2 Deployment Guide - WhatsApp Business Application

## Prerequisites
- EC2 instance running Ubuntu 22.04
- SSH access to your EC2 instance

## Step-by-Step Deployment

### Step 1: SSH into your EC2 instance
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 2: Install Docker
```bash
# Update system packages
sudo apt update

# Install Docker
sudo apt install docker.io -y

# Start Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group (to run docker without sudo)
sudo usermod -aG docker ubuntu

# Verify Docker installation
docker --version
```

**Important:** After adding yourself to the docker group, you need to:
- Log out and log back in, OR
- Run: `newgrp docker`

### Step 3: Clone Repository (if not already cloned)
```bash
# Navigate to home directory
cd ~

# Clone the repository
git clone https://github.com/vakhileshni/whatsApp.git

# Navigate into the project
cd whatsApp
```

### Step 4: Build Docker Image
```bash
# Build the Docker image (this will take a few minutes)
docker build -t whatsapp-business-app .
```

### Step 5: Run the Container
```bash
# Run the container
docker run -d \
  --name whatsapp-app \
  -p 4000:4000 \
  --restart unless-stopped \
  whatsapp-business-app
```

### Step 6: Verify It's Running
```bash
# Check if container is running
docker ps

# View logs
docker logs whatsapp-app

# Check if backend is responding
curl http://localhost:4000/docs
```

### Step 7: Configure EC2 Security Group
1. Go to AWS Console → EC2 → Security Groups
2. Select your instance's security group
3. Add inbound rule:
   - Type: Custom TCP
   - Port: 4000
   - Source: 0.0.0.0/0 (or your specific IP for security)

### Step 8: Access Your Application
- **API Endpoint:** `http://your-ec2-public-ip:4000`
- **API Documentation:** `http://your-ec2-public-ip:4000/docs`

## Useful Docker Commands

### View Logs
```bash
docker logs -f whatsapp-app
```

### Stop Container
```bash
docker stop whatsapp-app
```

### Start Container
```bash
docker start whatsapp-app
```

### Restart Container
```bash
docker restart whatsapp-app
```

### Remove Container
```bash
docker stop whatsapp-app
docker rm whatsapp-app
```

### Update Application (after code changes on GitHub)
```bash
# Stop and remove old container
docker stop whatsapp-app
docker rm whatsapp-app

# Pull latest code (if you have the repo cloned)
cd ~/whatsApp
git pull

# Rebuild image
docker build -t whatsapp-business-app .

# Run new container
docker run -d \
  --name whatsapp-app \
  -p 4000:4000 \
  --restart unless-stopped \
  whatsapp-business-app
```

## Alternative: Using Docker Compose

If you have `docker-compose` installed:

```bash
# Install docker-compose (if not already installed)
sudo apt install docker-compose -y

# Run with docker-compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop
docker-compose down
```

## Troubleshooting

### Docker permission denied
```bash
# Make sure you're in the docker group
sudo usermod -aG docker $USER
newgrp docker
```

### Port already in use
```bash
# Check what's using port 4000
sudo lsof -i :4000

# Or change port mapping (e.g., use 8080 instead)
docker run -d -p 8080:4000 --name whatsapp-app whatsapp-business-app
```

### Container keeps stopping
```bash
# Check logs for errors
docker logs whatsapp-app

# Check container status
docker ps -a
```

### Can't access from outside EC2
- Verify Security Group allows port 4000
- Check if the container is actually running: `docker ps`
- Test locally on EC2: `curl http://localhost:4000/docs`

## Summary

After installing Docker, you just need:
1. `docker build -t whatsapp-business-app .`
2. `docker run -d --name whatsapp-app -p 4000:4000 --restart unless-stopped whatsapp-business-app`

That's it! Your backend API will be running on port 4000.

