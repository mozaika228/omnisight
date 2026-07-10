#!/bin/bash
# Start development environment

set -e

echo "🚀 Starting OmniSight development environment..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed"
    exit 1
fi

echo "📦 Starting services with Docker Compose..."
docker-compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

echo "✅ Services started!"
echo ""
echo "URLs:"
echo "  API:        http://localhost:8000"
echo "  Frontend:   http://localhost:3000"
echo "  Qdrant:     http://localhost:6333"
echo "  Postgres:   localhost:5432"
echo "  Redis:      localhost:6379"
echo "  MinIO:      http://localhost:9001"
echo ""
echo "🔑 Default credentials:"
echo "  MinIO:      omnisight / omnisight_dev_password"
echo "  Postgres:   omnisight / omnisight_dev_password"
echo ""
