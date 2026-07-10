#!/bin/bash
# View logs from services

set -e

if [ -z "$1" ]; then
    echo "🔍 Showing logs from all services..."
    docker-compose logs -f
else
    echo "🔍 Showing logs from $1..."
    docker-compose logs -f "$1"
fi
