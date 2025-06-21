#!/bin/bash

# Build script for Internshala Scraper Docker image

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
IMAGE_NAME="internshala-scraper"
TAG="latest"
REGISTRY=""
FULL_IMAGE_NAME=""

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
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -t, --tag TAG         Docker image tag (default: latest)"
    echo "  -r, --registry REG    Docker registry (optional)"
    echo "  -p, --push            Push image to registry after build"
    echo "  -c, --clean           Clean up old images after build"
    echo "  -h, --help            Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Build with default settings"
    echo "  $0 -t v1.0.0         # Build with specific tag"
    echo "  $0 -r myregistry.com -p  # Build and push to registry"
    echo "  $0 -c                # Build and clean old images"
}

# Parse command line arguments
PUSH=false
CLEAN=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -r|--registry)
            REGISTRY="$2"
            shift 2
            ;;
        -p|--push)
            PUSH=true
            shift
            ;;
        -c|--clean)
            CLEAN=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Set full image name
if [[ -n "$REGISTRY" ]]; then
    FULL_IMAGE_NAME="${REGISTRY}/${IMAGE_NAME}:${TAG}"
else
    FULL_IMAGE_NAME="${IMAGE_NAME}:${TAG}"
fi

print_status "Building Docker image: $FULL_IMAGE_NAME"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker and try again."
    exit 1
fi

# Build the image
print_status "Starting Docker build..."
if docker build -t "$FULL_IMAGE_NAME" .; then
    print_success "Docker image built successfully!"
else
    print_error "Docker build failed!"
    exit 1
fi

# Push to registry if requested
if [[ "$PUSH" == true ]]; then
    if [[ -z "$REGISTRY" ]]; then
        print_error "Registry is required for pushing. Use -r option."
        exit 1
    fi
    
    print_status "Pushing image to registry..."
    if docker push "$FULL_IMAGE_NAME"; then
        print_success "Image pushed successfully!"
    else
        print_error "Failed to push image!"
        exit 1
    fi
fi

# Clean up old images if requested
if [[ "$CLEAN" == true ]]; then
    print_status "Cleaning up old images..."
    docker image prune -f
    print_success "Cleanup completed!"
fi

# Show image information
print_status "Image details:"
docker images "$FULL_IMAGE_NAME"

print_success "Build process completed successfully!"
print_status "To run the container:"
echo "  docker run -p 8000:8000 $FULL_IMAGE_NAME"
echo ""
print_status "Or use docker-compose:"
echo "  docker-compose up" 