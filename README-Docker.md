# Internshala Scraper - Docker Deployment Guide

This guide provides comprehensive instructions for deploying the Internshala Scraper application using Docker and Docker Compose.

## 📋 Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Files Overview](#docker-files-overview)
- [Deployment Options](#deployment-options)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Security Considerations](#security-considerations)

## 🚀 Prerequisites

Before you begin, ensure you have the following installed:

- **Docker** (version 20.10 or higher)
- **Docker Compose** (version 2.0 or higher)
- **Git** (for cloning the repository)
- **curl** (for health checks)

### Installing Docker

#### Ubuntu/Debian:
```bash
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl enable --now docker
sudo usermod -aG docker $USER
```

#### Windows:
Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)

#### macOS:
Download and install Docker Desktop from [docker.com](https://www.docker.com/products/docker-desktop)

## ⚡ Quick Start

### 1. Clone the Repository
```bash
git clone <repository-url>
cd internshala
```

### 2. Build and Run (Development)
```bash
# Build the Docker image
docker-compose -f docker-compose.dev.yml up --build

# Or use the build script
chmod +x scripts/build.sh
./scripts/build.sh
```

### 3. Access the Application
Open your browser and navigate to: `http://localhost:8000`

## 📁 Docker Files Overview

### Core Files

| File | Purpose | Usage |
|------|---------|-------|
| `Dockerfile` | Main Docker image definition | Development and basic production |
| `Dockerfile.prod` | Production-optimized image | Production deployment |
| `docker-compose.yml` | Basic deployment configuration | Simple production setup |
| `docker-compose.dev.yml` | Development environment | Development with hot reload |
| `docker-compose.prod.yml` | Production environment | Production with nginx |

### Configuration Files

| File | Purpose |
|------|---------|
| `nginx.conf` | Nginx reverse proxy configuration |
| `.dockerignore` | Files to exclude from Docker build |
| `scripts/build.sh` | Automated build script |
| `scripts/deploy.sh` | Deployment management script |

## 🎯 Deployment Options

### 1. Development Environment

Best for development and testing:

```bash
# Start development environment
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop development environment
docker-compose -f docker-compose.dev.yml down
```

**Features:**
- Hot code reload
- Debug mode enabled
- Additional development tools (Redis, PostgreSQL, pgAdmin)
- Source code mounted for live editing

### 2. Basic Production

Simple production deployment:

```bash
# Start basic production
docker-compose up -d

# View status
docker-compose ps

# Stop services
docker-compose down
```

**Features:**
- Health checks
- Automatic restarts
- Volume persistence

### 3. Full Production with Nginx

Complete production setup with reverse proxy:

```bash
# Start full production environment
docker-compose -f docker-compose.prod.yml up -d
```

**Features:**
- Multi-stage Docker build
- Resource limits
- Nginx reverse proxy
- SSL support (configurable)

## ⚙️ Configuration

### Environment Variables

Create a `.env` file for production:

```bash
# Application
FLASK_ENV=production
FLASK_DEBUG=0
PYTHONUNBUFFERED=1
```

### Nginx Configuration

The `nginx.conf` file includes:
- Reverse proxy setup
- Rate limiting
- Gzip compression
- SSL configuration (commented)
- Health check endpoint

## 🔧 Scripts Usage

### Build Script

```bash
# Basic build
./scripts/build.sh

# Build with specific tag
./scripts/build.sh -t v1.0.0

# Build and push to registry
./scripts/build.sh -r myregistry.com -p

# Build with cleanup
./scripts/build.sh -c
```

### Deployment Script

```bash
# Start production
./scripts/deploy.sh start

# Start development
./scripts/deploy.sh -e development start

# Check status
./scripts/deploy.sh status

# View logs
./scripts/deploy.sh logs

# Create backup
./scripts/deploy.sh backup

# Restore from backup
./scripts/deploy.sh restore backup_file.tar.gz
```

## 🐛 Troubleshooting

### Common Issues

#### 1. Port Already in Use
```bash
# Check what's using the port
sudo lsof -i :8000

# Kill the process
sudo kill -9 <PID>
```

#### 2. Permission Denied
```bash
# Fix Docker permissions
sudo chmod 666 /var/run/docker.sock

# Or add user to docker group
sudo usermod -aG docker $USER
```

#### 3. Playwright Browser Issues
```bash
# Rebuild with browser installation
docker-compose build --no-cache

# Or install browsers manually
docker-compose exec internshala-scraper playwright install chromium
```

#### 4. Memory Issues
```bash
# Check container resource usage
docker stats

# Increase Docker memory limit in Docker Desktop settings
```

### Logs and Debugging

```bash
# View all logs
docker-compose logs

# View specific service logs
docker-compose logs internshala-scraper

# Follow logs in real-time
docker-compose logs -f

# View container details
docker inspect internshala-scraper
```

### Health Checks

```bash
# Check application health
curl http://localhost:8000/

# Check nginx health
curl http://localhost/health

# Check container health
docker-compose ps
```

## 🔒 Security Considerations

### 1. Production Security

- **Use strong passwords** for all services
- **Enable SSL/TLS** for production deployments
- **Limit container resources** to prevent DoS
- **Regular security updates** for base images
- **Network isolation** using Docker networks

### 2. Environment Variables

```bash
# Never commit sensitive data
echo ".env" >> .gitignore
echo "ssl/" >> .gitignore
```

### 3. Container Security

```bash
# Run containers as non-root user (already configured)
# Use read-only file systems where possible
# Implement resource limits
# Regular vulnerability scanning
```

### 4. Network Security

```bash
# Use internal networks for inter-service communication
# Expose only necessary ports
# Implement rate limiting
# Use reverse proxy for SSL termination
```

## 📈 Performance Optimization

### 1. Resource Limits

```yaml
deploy:
  resources:
    limits:
      memory: 2G
      cpus: '1.0'
    reservations:
      memory: 512M
      cpus: '0.5'
```

### 2. Caching

- Implement browser caching
- Use CDN for static assets
- Optimize database queries

### 3. Database Optimization

- Use connection pooling
- Implement database indexing
- Regular database maintenance

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ./scripts/deploy.sh update
```

## 📞 Support

For issues and questions:

1. Check the troubleshooting section
2. Review Docker and application logs
3. Ensure all prerequisites are met
4. Verify network connectivity
5. Check resource availability

## 📝 License

This Docker setup is provided as-is for educational and development purposes. Ensure compliance with Internshala's terms of service when using this scraper. 