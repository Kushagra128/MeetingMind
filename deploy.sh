#!/bin/bash

# MeetingMing Deployment Script
# This script helps deploy MeetingMing using Docker

set -e

echo "=========================================="
echo "MeetingMing Deployment Script"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✅ Docker and Docker Compose are installed"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    cp .env.example .env
    
    # Generate random secret keys
    SECRET_KEY=$(openssl rand -hex 32)
    JWT_SECRET_KEY=$(openssl rand -hex 32)
    
    # Update .env file with generated keys
    sed -i "s/your-super-secret-key-change-this-immediately/$SECRET_KEY/" .env
    sed -i "s/your-jwt-secret-key-change-this-immediately/$JWT_SECRET_KEY/" .env
    
    echo "✅ Created .env file with generated secret keys"
    echo "⚠️  Please review and update .env file with your configuration"
    echo ""
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data
mkdir -p backend/uploads
mkdir -p iot-meeting-minutes/recordings
mkdir -p logs
echo "✅ Directories created"
echo ""

# Ask user what to do
echo "What would you like to do?"
echo "1) Build and start containers"
echo "2) Stop containers"
echo "3) View logs"
echo "4) Rebuild containers (clean build)"
echo "5) Exit"
echo ""
read -p "Enter your choice (1-5): " choice

case $choice in
    1)
        echo ""
        echo "🚀 Building and starting containers..."
        docker-compose up -d --build
        echo ""
        echo "✅ Deployment complete!"
        echo ""
        echo "🌐 Access MeetingMing at: http://localhost"
        echo "📡 Backend API at: http://localhost:5000"
        echo ""
        echo "📊 View logs with: docker-compose logs -f"
        echo "🛑 Stop with: docker-compose down"
        ;;
    2)
        echo ""
        echo "🛑 Stopping containers..."
        docker-compose down
        echo "✅ Containers stopped"
        ;;
    3)
        echo ""
        echo "📊 Viewing logs (Ctrl+C to exit)..."
        docker-compose logs -f
        ;;
    4)
        echo ""
        echo "🔨 Rebuilding containers (this may take a while)..."
        docker-compose down
        docker-compose build --no-cache
        docker-compose up -d
        echo "✅ Rebuild complete!"
        ;;
    5)
        echo "👋 Goodbye!"
        exit 0
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac
