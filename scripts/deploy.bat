@echo off
REM Deployment script for Internshala Scraper (Windows)

setlocal enabledelayedexpansion

REM Configuration
set COMPOSE_FILE=docker-compose.yml
set DEV_COMPOSE_FILE=docker-compose.dev.yml
set ENVIRONMENT=production

REM Parse command line arguments
:parse_args
if "%~1"=="" goto :end_parse
if "%~1"=="-e" (
    set ENVIRONMENT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--env" (
    set ENVIRONMENT=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-f" (
    set COMPOSE_FILE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="--file" (
    set COMPOSE_FILE=%~2
    shift
    shift
    goto :parse_args
)
if "%~1"=="-h" (
    goto :show_usage
)
if "%~1"=="--help" (
    goto :show_usage
)
if "%~1"=="start" (
    set COMMAND=start
    shift
    goto :parse_args
)
if "%~1"=="stop" (
    set COMMAND=stop
    shift
    goto :parse_args
)
if "%~1"=="restart" (
    set COMMAND=restart
    shift
    goto :parse_args
)
if "%~1"=="status" (
    set COMMAND=status
    shift
    goto :parse_args
)
if "%~1"=="logs" (
    set COMMAND=logs
    shift
    goto :parse_args
)
if "%~1"=="update" (
    set COMMAND=update
    shift
    goto :parse_args
)
if "%~1"=="backup" (
    set COMMAND=backup
    shift
    goto :parse_args
)
if "%~1"=="restore" (
    set COMMAND=restore
    shift
    goto :parse_args
)
echo [ERROR] Unknown option: %~1
goto :show_usage

:end_parse

REM Validate environment
if not "%ENVIRONMENT%"=="production" if not "%ENVIRONMENT%"=="development" (
    echo [ERROR] Invalid environment: %ENVIRONMENT%. Use 'production' or 'development'
    exit /b 1
)

REM Set compose file based on environment
if "%ENVIRONMENT%"=="development" (
    set COMPOSE_FILE=%DEV_COMPOSE_FILE%
)

REM Check if compose file exists
if not exist "%COMPOSE_FILE%" (
    echo [ERROR] Docker Compose file not found: %COMPOSE_FILE%
    exit /b 1
)

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not running. Please start Docker and try again.
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker Compose is not installed or not in PATH
    exit /b 1
)

REM Main command execution
if "%COMMAND%"=="start" goto :start_app
if "%COMMAND%"=="stop" goto :stop_app
if "%COMMAND%"=="restart" goto :restart_app
if "%COMMAND%"=="status" goto :show_status
if "%COMMAND%"=="logs" goto :show_logs
if "%COMMAND%"=="update" goto :update_app
if "%COMMAND%"=="backup" goto :create_backup
if "%COMMAND%"=="restore" goto :restore_backup
echo [ERROR] No command specified
goto :show_usage

:start_app
echo [INFO] Starting Internshala Scraper in %ENVIRONMENT% mode...

REM Create necessary directories
if not exist "downloads" mkdir downloads
if not exist "logs" mkdir logs

REM Start the services
docker-compose -f "%COMPOSE_FILE%" up -d
if errorlevel 1 (
    echo [ERROR] Failed to start application!
    exit /b 1
)
echo [SUCCESS] Application started successfully!

REM Wait for services to be ready
echo [INFO] Waiting for services to be ready...
timeout /t 10 /nobreak >nul

REM Check health
call :check_health
if errorlevel 1 (
    echo [WARNING] Some services may not be fully ready yet
) else (
    echo [SUCCESS] All services are healthy!
)
exit /b 0

:stop_app
echo [INFO] Stopping Internshala Scraper...
docker-compose -f "%COMPOSE_FILE%" down
if errorlevel 1 (
    echo [ERROR] Failed to stop application!
    exit /b 1
)
echo [SUCCESS] Application stopped successfully!
exit /b 0

:restart_app
echo [INFO] Restarting Internshala Scraper...
call :stop_app
timeout /t 2 /nobreak >nul
call :start_app
exit /b 0

:show_status
echo [INFO] Application status:
docker-compose -f "%COMPOSE_FILE%" ps

echo.
echo [INFO] Service logs (last 10 lines):
docker-compose -f "%COMPOSE_FILE%" logs --tail=10
exit /b 0

:show_logs
echo [INFO] Showing application logs (press Ctrl+C to exit):
docker-compose -f "%COMPOSE_FILE%" logs -f
exit /b 0

:check_health
REM Check if the main service is responding
curl -f http://localhost:8000/ >nul 2>&1
exit /b %errorlevel%

:update_app
echo [INFO] Updating Internshala Scraper...

REM Pull latest changes (if using git)
if exist ".git" (
    echo [INFO] Pulling latest changes from git...
    git pull origin main
)

REM Rebuild and restart
echo [INFO] Rebuilding Docker images...
docker-compose -f "%COMPOSE_FILE%" build --no-cache

call :restart_app
exit /b 0

:create_backup
echo [INFO] Creating backup...

set BACKUP_DIR=backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
if not exist "backups" mkdir backups
mkdir "%BACKUP_DIR%"

REM Backup downloads
if exist "downloads" (
    xcopy "downloads" "%BACKUP_DIR%\downloads\" /E /I /Y >nul
    echo [SUCCESS] Downloads backed up to %BACKUP_DIR%\downloads
)

REM Backup logs
if exist "logs" (
    xcopy "logs" "%BACKUP_DIR%\logs\" /E /I /Y >nul
    echo [SUCCESS] Logs backed up to %BACKUP_DIR%\logs
)

REM Create backup archive
powershell -Command "Compress-Archive -Path '%BACKUP_DIR%' -DestinationPath '%BACKUP_DIR%.zip' -Force"
rmdir /s /q "%BACKUP_DIR%"

echo [SUCCESS] Backup created: %BACKUP_DIR%.zip
exit /b 0

:restore_backup
if "%~1"=="" (
    echo [ERROR] Please specify backup file to restore from
    exit /b 1
)

set BACKUP_FILE=%~1

if not exist "%BACKUP_FILE%" (
    echo [ERROR] Backup file not found: %BACKUP_FILE%
    exit /b 1
)

echo [INFO] Restoring from backup: %BACKUP_FILE%

REM Stop application
call :stop_app

REM Extract backup
set BACKUP_DIR=backups\%date:~-4,4%%date:~-10,2%%date:~-7,2%_%time:~0,2%%time:~3,2%%time:~6,2%
set BACKUP_DIR=%BACKUP_DIR: =0%
powershell -Command "Expand-Archive -Path '%BACKUP_FILE%' -DestinationPath 'backups' -Force"

REM Restore data
if exist "%BACKUP_DIR%\downloads" (
    if exist "downloads" rmdir /s /q "downloads"
    xcopy "%BACKUP_DIR%\downloads" "downloads\" /E /I /Y >nul
    echo [SUCCESS] Downloads restored
)

if exist "%BACKUP_DIR%\logs" (
    if exist "logs" rmdir /s /q "logs"
    xcopy "%BACKUP_DIR%\logs" "logs\" /E /I /Y >nul
    echo [SUCCESS] Logs restored
)

REM Clean up
rmdir /s /q "%BACKUP_DIR%"

REM Start application
call :start_app

echo [SUCCESS] Restore completed successfully!
exit /b 0

:show_usage
echo Usage: %~nx0 [OPTIONS] COMMAND
echo.
echo Commands:
echo   start       Start the application
echo   stop        Stop the application
echo   restart     Restart the application
echo   status      Show application status
echo   logs        Show application logs
echo   update      Update and restart the application
echo   backup      Create backup of data
echo   restore     Restore from backup
echo.
echo Options:
echo   -e, --env ENV    Environment (production|development, default: production)
echo   -f, --file FILE  Docker Compose file to use
echo   -h, --help       Show this help message
echo.
echo Examples:
echo   %~nx0 start                    # Start production environment
echo   %~nx0 -e development start     # Start development environment
echo   %~nx0 -f custom-compose.yml start  # Use custom compose file
exit /b 0 