#!/bin/bash

# Deployment script for Internshala Scraper

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
DEV_COMPOSE_FILE="docker-compose.dev.yml"
ENVIRONMENT="production"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  start       Start the application"
    echo "  stop        Stop the application"
    echo "  restart     Restart the application"
    echo "  status      Show application status"
    echo "  logs        Show application logs"
    echo "  update      Update and restart the application"
    echo "  backup      Create backup of data"
    echo "  restore     Restore from backup"
    echo ""
    echo "Options:"
    echo "  -e, --env ENV    Environment (production|development, default: production)"
    echo "  -f, --file FILE  Docker Compose file to use"
    echo "  -h, --help       Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start                    # Start production environment"
    echo "  $0 -e development start     # Start development environment"
    echo "  $0 -f custom-compose.yml start  # Use custom compose file"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        start|stop|restart|status|logs|update|backup|restore)
            COMMAND="$1"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate environment
if [[ "$ENVIRONMENT" != "production" && "$ENVIRONMENT" != "development" ]]; then
    print_error "Invalid environment: $ENVIRONMENT. Use 'production' or 'development'"
    exit 1
fi

# Set compose file based on environment
if [[ "$ENVIRONMENT" == "development" ]]; then
    COMPOSE_FILE="$DEV_COMPOSE_FILE"
fi

# Check if compose file exists
if [[ ! -f "$COMPOSE_FILE" ]]; then
    print_error "Docker Compose file not found: $COMPOSE_FILE"
    exit 1
fi

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed or not in PATH"
    exit 1
fi

# Function to start the application
start_app() {
    print_status "Starting Internshala Scraper in $ENVIRONMENT mode..."
    
    # Create necessary directories
    mkdir -p downloads logs
    
    # Start the services
    if docker-compose -f "$COMPOSE_FILE" up -d; then
        print_success "Application started successfully!"
        
        # Wait for services to be ready
        print_status "Waiting for services to be ready..."
        sleep 10
        
        # Check health
        if check_health; then
            print_success "All services are healthy!"
        else
            print_warning "Some services may not be fully ready yet"
        fi
    else
        print_error "Failed to start application!"
        exit 1
    fi
}

# Function to stop the application
stop_app() {
    print_status "Stopping Internshala Scraper..."
    if docker-compose -f "$COMPOSE_FILE" down; then
        print_success "Application stopped successfully!"
    else
        print_error "Failed to stop application!"
        exit 1
    fi
}

# Function to restart the application
restart_app() {
    print_status "Restarting Internshala Scraper..."
    stop_app
    sleep 2
    start_app
}

# Function to show status
show_status() {
    print_status "Application status:"
    docker-compose -f "$COMPOSE_FILE" ps
    
    echo ""
    print_status "Service logs (last 10 lines):"
    docker-compose -f "$COMPOSE_FILE" logs --tail=10
}

# Function to show logs
show_logs() {
    print_status "Showing application logs (press Ctrl+C to exit):"
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# Function to check health
check_health() {
    # Check if the main service is responding
    if curl -f http://localhost:8000/ > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to update application
update_app() {
    print_status "Updating Internshala Scraper..."
    
    # Pull latest changes (if using git)
    if [[ -d ".git" ]]; then
        print_status "Pulling latest changes from git..."
        git pull origin main
    fi
    
    # Rebuild and restart
    print_status "Rebuilding Docker images..."
    docker-compose -f "$COMPOSE_FILE" build --no-cache
    
    restart_app
}

# Function to create backup
create_backup() {
    print_status "Creating backup..."
    
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # Backup downloads
    if [[ -d "downloads" ]]; then
        cp -r downloads "$BACKUP_DIR/"
        print_success "Downloads backed up to $BACKUP_DIR/downloads"
    fi
    
    # Backup logs
    if [[ -d "logs" ]]; then
        cp -r logs "$BACKUP_DIR/"
        print_success "Logs backed up to $BACKUP_DIR/logs"
    fi
    
    # Create backup archive
    tar -czf "${BACKUP_DIR}.tar.gz" -C backups "$(basename "$BACKUP_DIR")"
    rm -rf "$BACKUP_DIR"
    
    print_success "Backup created: ${BACKUP_DIR}.tar.gz"
}

# Function to restore from backup
restore_backup() {
    if [[ $# -eq 0 ]]; then
        print_error "Please specify backup file to restore from"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    if [[ ! -f "$BACKUP_FILE" ]]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    print_status "Restoring from backup: $BACKUP_FILE"
    
    # Stop application
    stop_app
    
    # Extract backup
    tar -xzf "$BACKUP_FILE" -C backups/
    
    # Restore data
    BACKUP_DIR="backups/$(basename "$BACKUP_FILE" .tar.gz)"
    
    if [[ -d "$BACKUP_DIR/downloads" ]]; then
        rm -rf downloads
        cp -r "$BACKUP_DIR/downloads" .
        print_success "Downloads restored"
    fi
    
    if [[ -d "$BACKUP_DIR/logs" ]]; then
        rm -rf logs
        cp -r "$BACKUP_DIR/logs" .
        print_success "Logs restored"
    fi
    
    # Clean up
    rm -rf "$BACKUP_DIR"
    
    # Start application
    start_app
    
    print_success "Restore completed successfully!"
}

# Main command execution
case "$COMMAND" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    update)
        update_app
        ;;
    backup)
        create_backup
        ;;
    restore)
        restore_backup "$@"
        ;;
    *)
        print_error "No command specified"
        show_usage
        exit 1
        ;;
esac 