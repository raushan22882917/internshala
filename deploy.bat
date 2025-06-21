@echo off
echo 🚀 Starting deployment of Internshala Scraper...

REM Build the Docker image
echo 📦 Building Docker image...
docker build -t internshala-scraper .

REM Stop and remove existing container if it exists
echo 🛑 Stopping existing container...
docker stop internshala-scraper 2>nul
docker rm internshala-scraper 2>nul

REM Run the new container
echo ▶️  Starting new container...
docker run -d ^
  --name internshala-scraper ^
  -p 8000:8000 ^
  -v %cd%/downloads:/app/downloads ^
  --restart unless-stopped ^
  internshala-scraper

REM Wait for the application to start
echo ⏳ Waiting for application to start...
timeout /t 10 /nobreak >nul

REM Check if the application is running
echo 🔍 Checking application health...
curl -f http://localhost:8000/health >nul 2>&1
if %errorlevel% equ 0 (
    echo ✅ Application is running successfully!
    echo 🌐 Access your application at: http://localhost:8000
) else (
    echo ❌ Application failed to start properly
    echo 📋 Container logs:
    docker logs internshala-scraper
    exit /b 1
)

echo 🎉 Deployment completed successfully!
pause 