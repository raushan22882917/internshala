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

# Install Playwright dependencies without root privileges
echo "🔧 Installing Playwright system dependencies..."
# Use the --with-deps flag to install dependencies during browser installation
python -m playwright install chromium --with-deps

echo "✅ Build completed successfully!" 