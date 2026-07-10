#!/usr/bin/env python
"""Initialize database schema and seed data."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("Database initialization script")
print("Run migrations with: alembic upgrade head")
