# Deployment Guide for Internshala Scraper

This guide will help you deploy the Internshala Scraper application using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose (optional, for easier management)

## Quick Start

### Option 1: Using the deployment script (Recommended)

**For Windows:**
```bash
deploy.bat
```

**For Linux/Mac:**
```bash
chmod +x deploy.sh
./deploy.sh
```

### Option 2: Manual Docker commands

1. **Build the Docker image:**
   ```bash
   docker build -t internshala-scraper .
   ```

2. **Run the container:**
   ```bash
   docker run -d \
     --name internshala-scraper \
     -p 8000:8000 \
     -v $(pwd)/downloads:/app/downloads \
     --restart unless-stopped \
     internshala-scraper
   ```

### Option 3: Using Docker Compose

```bash
docker-compose up -d
```

## Accessing the Application

Once deployed, you can access the application at:
- **Main application:** http://localhost:8000
- **Health check:** http://localhost:8000/health

## Container Management

### View logs
```bash
docker logs internshala-scraper
```

### Stop the container
```bash
docker stop internshala-scraper
```

### Remove the container
```bash
docker rm internshala-scraper
```

### Restart the container
```bash
docker restart internshala-scraper
```

## Environment Variables

You can customize the deployment by setting environment variables:

- `PORT`: Port number (default: 8000)
- `FLASK_ENV`: Environment mode (default: production)

Example:
```bash
docker run -d \
  --name internshala-scraper \
  -p 8000:8000 \
  -e PORT=8080 \
  -e FLASK_ENV=production \
  -v $(pwd)/downloads:/app/downloads \
  internshala-scraper
```

## Production Deployment

For production deployment, consider the following:

1. **Use a reverse proxy** (nginx, Apache) in front of the application
2. **Set up SSL/TLS certificates** for HTTPS
3. **Configure proper logging** and monitoring
4. **Use environment-specific configuration**
5. **Set up automated backups** for the downloads directory

### Example with Nginx reverse proxy:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Container won't start
1. Check if port 8000 is already in use:
   ```bash
   netstat -tulpn | grep :8000
   ```

2. View container logs:
   ```bash
   docker logs internshala-scraper
   ```

### Application is not responding
1. Check the health endpoint:
   ```bash
   curl http://localhost:8000/health
   ```

2. Verify the container is running:
   ```bash
   docker ps
   ```

### Playwright issues
If you encounter Playwright-related errors:
1. Ensure the container has enough memory (at least 2GB recommended)
2. Check if all browser dependencies are installed correctly
3. Verify the container has internet access for web scraping

## Security Considerations

- The application runs as a non-root user inside the container
- Downloads directory is mounted as a volume for persistence
- Health checks are configured for monitoring
- Container restart policy is set to `unless-stopped`

## Monitoring

The application includes a health check endpoint at `/health` that returns:
```json
{
  "status": "healthy",
  "message": "Internshala Scraper is running"
}
```

You can use this endpoint for monitoring and load balancer health checks. 