"""
PostgreSQL database setup script

Run this to initialize the OmniSight database
"""

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import sys

def setup_database():
    """Create database and user"""
    
    # Connect to PostgreSQL
    try:
        conn = psycopg2.connect(
            host="localhost",
            user="postgres",
            password="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
    except psycopg2.OperationalError as e:
        print(f"❌ Cannot connect to PostgreSQL: {e}")
        print("Make sure PostgreSQL is running and you have the correct credentials")
        sys.exit(1)
    
    # Create database
    print("📦 Creating database 'omnisight'...")
    try:
        cursor.execute("CREATE DATABASE omnisight;")
        print("✅ Database created")
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print("⚠️  Database already exists")
        else:
            print(f"❌ Error creating database: {e}")
            sys.exit(1)
    
    # Create user
    print("👤 Creating user 'omnisight'...")
    try:
        cursor.execute("""
            CREATE USER omnisight WITH PASSWORD 'omnisight_dev_password';
        """)
        print("✅ User created")
    except psycopg2.Error as e:
        if "already exists" in str(e):
            print("⚠️  User already exists")
        else:
            print(f"❌ Error creating user: {e}")
    
    # Grant privileges
    print("🔑 Granting privileges...")
    cursor.execute("""
        ALTER ROLE omnisight SET client_encoding TO 'utf8';
        ALTER ROLE omnisight SET default_transaction_isolation TO 'read committed';
        ALTER ROLE omnisight SET default_transaction_deferrable TO on;
        ALTER ROLE omnisight SET default_transaction_readonly TO off;
        GRANT ALL PRIVILEGES ON DATABASE omnisight TO omnisight;
    """)
    print("✅ Privileges granted")
    
    cursor.close()
    conn.close()
    
    print("\n✅ Database setup complete!")
    print("Test connection: psql -U omnisight -d omnisight -c 'SELECT 1;'")

if __name__ == "__main__":
    setup_database()
