#!/bin/bash

# Alternative build script for Render deployment using Selenium

set -e  # Exit on any error

echo "🚀 Starting alternative build process with Selenium..."

# Upgrade pip and install build tools
echo "📦 Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements_alternative.txt

# Verify selenium installation
echo "🔍 Verifying Selenium installation..."
python -c "import selenium; print('Selenium imported successfully')"

# Install Chrome dependencies for Selenium
echo "🔧 Installing Chrome dependencies..."
apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    libxss1 \
    libnss3 \
    libnspr4 \
    libatk-bridge2.0-0 \
    libdrm2 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    libatspi2.0-0 \
    libgtk-3-0 \
    libgdk-pixbuf2.0-0 \
    && rm -rf /var/lib/apt/lists/*

echo "✅ Alternative build completed successfully!" 