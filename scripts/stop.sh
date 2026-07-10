#!/bin/bash
# Stop development environment

set -e

echo "🛑 Stopping OmniSight services..."
docker-compose down

echo "✅ Services stopped"
