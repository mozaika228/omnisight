#!/usr/bin/env python3
"""
Starter script to launch OmniSight services locally without Docker
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import List, Tuple

class ServiceManager:
    def __init__(self):
        self.processes = []
        self.services_config = [
            {
                "name": "FastAPI Backend",
                "cmd": [sys.executable, "-m", "uvicorn", "apps.api.main:app", "--reload", "--port", "8000"],
                "cwd": ".",
                "port": 8000,
                "env_vars": {"PYTHONUNBUFFERED": "1"}
            },
            {
                "name": "Next.js Frontend",
                "cmd": ["npm", "run", "dev"],
                "cwd": "./apps/web",
                "port": 3000,
                "env_vars": {"NEXT_PUBLIC_API_URL": "http://localhost:8000/api/v1"}
            }
        ]

    def check_services(self) -> bool:
        """Check if external services are running"""
        services = [
            ("PostgreSQL", "localhost", 5432),
            ("Redis", "localhost", 6379),
            ("Qdrant", "localhost", 6333),
        ]
        
        print("\n🔍 Checking external services...\n")
        
        all_available = True
        for name, host, port in services:
            if self._check_port(host, port):
                print(f"✅ {name} available on {host}:{port}")
            else:
                print(f"❌ {name} NOT available on {host}:{port}")
                all_available = False
        
        if not all_available:
            print("\n⚠️  Some services are not running. Start them first:")
            print("   - PostgreSQL: psql -U postgres")
            print("   - Redis: redis-server")
            print("   - Qdrant: qdrant.exe")
            print("\nOr download/install them:")
            print("   - https://www.postgresql.org/download/windows/")
            print("   - https://github.com/microsoftarchive/redis/releases")
            print("   - https://github.com/qdrant/qdrant/releases")
            return False
        
        return True

    @staticmethod
    def _check_port(host: str, port: int) -> bool:
        """Check if port is open"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0

    def check_venv(self) -> bool:
        """Check if virtual environment exists and is activated"""
        venv_path = Path("venv")
        if not venv_path.exists():
            print("❌ Virtual environment not found. Run:")
            print("   python -m venv venv")
            print("   .\\venv\\Scripts\\Activate.ps1  (Windows)")
            print("   source venv/bin/activate       (Linux/Mac)")
            return False
        print("✅ Virtual environment found")
        return True

    def start_services(self) -> None:
        """Start all services"""
        print("\n🚀 Starting OmniSight services...\n")
        
        # Show commands to run in separate terminals
        print("━" * 70)
        print("Start each service in a separate terminal:\n")
        
        print("📊 Required services (must be running):")
        print("   Terminal 1 (PostgreSQL):")
        print("   psql -U postgres\n")
        
        print("   Terminal 2 (Redis):")
        print("   redis-server\n")
        
        print("   Terminal 3 (Qdrant):")
        print("   qdrant.exe  (or download from GitHub)\n")
        
        print("📱 OmniSight services:")
        print("   Terminal 4 (Backend):")
        print("   .\\venv\\Scripts\\Activate.ps1")
        print("   uvicorn apps.api.main:app --reload --port 8000\n")
        
        print("   Terminal 5 (Frontend):")
        print("   cd apps\\web")
        print("   npm run dev\n")
        
        print("🌐 Access:")
        print("   Frontend:  http://localhost:3000")
        print("   API:       http://localhost:8000")
        print("   API Docs:  http://localhost:8000/docs")
        print("━" * 70)
        
        print("\n💡 Tip: Use this script to verify all services are connected:")
        print("   python -c \"from apps.api.config import settings; print(settings)\"")

if __name__ == "__main__":
    manager = ServiceManager()
    
    # Check venv
    if not manager.check_venv():
        sys.exit(1)
    
    # Check external services
    if not manager.check_services():
        print("\n⚠️  Continue anyway? (y/n): ", end="")
        if input().lower() != 'y':
            sys.exit(1)
    
    # Show instructions
    manager.start_services()
