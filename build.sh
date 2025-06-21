#!/bin/bash

# Build script for Render deployment

set -e  # Exit on any error

echo "🚀 Starting build process..."

# Upgrade pip and install build tools
echo "📦 Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Verify playwright installation
echo "🔍 Verifying Playwright installation..."
python -c "import playwright; print('Playwright imported successfully')"

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
python -m playwright install chromium

# Install Playwright dependencies
echo "🔧 Installing Playwright system dependencies..."
python -m playwright install-deps chromium

echo "✅ Build completed successfully!" 