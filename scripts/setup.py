#!/usr/bin/env python3
"""Quick setup script for development environment."""

import os
import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a shell command with status output."""
    print(f"⏳ {description}...")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {description} complete")
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        return False
    return True

def main():
    """Set up development environment."""
    print("🚀 OmniSight Development Setup\n")

    project_root = Path(__file__).parent.parent

    # Check Python version
    if sys.version_info < (3, 10):
        print("❌ Python 3.10+ is required")
        sys.exit(1)

    # Create .env file if it doesn't exist
    env_file = project_root / ".env"
    if not env_file.exists():
        example_env = project_root / ".env.example"
        if example_env.exists():
            print("📝 Creating .env from .env.example...")
            import shutil
            shutil.copy(example_env, env_file)
        else:
            print("⚠️  .env.example not found")

    # Create pre-commit hook
    run_command("pre-commit install", "Installing pre-commit hooks")

    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("1. Edit .env if needed")
    print("2. Run: docker-compose up -d")
    print("3. Visit: http://localhost:3000")

if __name__ == "__main__":
    main()
