#!/bin/bash

# Deployment script for Internshala Scraper

set -e

echo "🚀 Starting deployment of Internshala Scraper..."

# Build the Docker image
echo "📦 Building Docker image..."
docker build -t internshala-scraper .

# Stop and remove existing container if it exists
echo "🛑 Stopping existing container..."
docker stop internshala-scraper || true
docker rm internshala-scraper || true

# Run the new container
echo "▶️  Starting new container..."
docker run -d \
  --name internshala-scraper \
  -p 8000:8000 \
  -v $(pwd)/downloads:/app/downloads \
  --restart unless-stopped \
  internshala-scraper

# Wait for the application to start
echo "⏳ Waiting for application to start..."
sleep 10

# Check if the application is running
echo "🔍 Checking application health..."
if curl -f http://localhost:8000/health; then
    echo "✅ Application is running successfully!"
    echo "🌐 Access your application at: http://localhost:8000"
else
    echo "❌ Application failed to start properly"
    echo "📋 Container logs:"
    docker logs internshala-scraper
    exit 1
fi

echo "🎉 Deployment completed successfully!" 