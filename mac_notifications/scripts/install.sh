#!/bin/bash
set -e

echo "Mac Notifications System Installer"
echo "=================================="

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install package in development mode
echo "Installing mac_notifications package..."
pip install -e .

# Create data directories
echo "Creating data directories..."
mkdir -p data/logs
mkdir -p data/backups

# Initialize database
echo "Initializing database..."
python -m mac_notifications.database.migrations init

echo "Installation complete!"
echo "To start the daemon: ./scripts/start_daemon.sh"
