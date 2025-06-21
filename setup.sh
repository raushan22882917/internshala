#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Make the script executable
chmod +x setup.sh 
