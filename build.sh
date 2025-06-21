#!/bin/bash

# Build script for Render deployment

echo "🚀 Starting build process..."

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "🌐 Installing Playwright browsers..."
playwright install chromium

# Install Playwright dependencies
echo "🔧 Installing Playwright system dependencies..."
playwright install-deps chromium

echo "✅ Build completed successfully!" 