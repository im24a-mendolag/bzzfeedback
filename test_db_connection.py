#!/usr/bin/env python3
"""
Test script to verify database connection configuration
Run this to test your database connection before deployment
"""

import os
from config import DB_CONFIG

def test_db_config():
    """Test and display database configuration"""
    print("🔍 Database Configuration Test")
    print("=" * 50)
    
    # Check environment variables
    print("Environment Variables:")
    print(f"  MYSQL_URL: {'✅ Set' if os.getenv('MYSQL_URL') else '❌ Not set'}")
    print(f"  DATABASE_URL: {'✅ Set' if os.getenv('DATABASE_URL') else '❌ Not set'}")
    print(f"  MYSQL_HOST: {'✅ Set' if os.getenv('MYSQL_HOST') else '❌ Not set'}")
    print()
    
    # Display parsed configuration
    print("Parsed Database Configuration:")
    print(f"  Host: {DB_CONFIG['host']}")
    print(f"  Port: {DB_CONFIG['port']}")
    print(f"  User: {DB_CONFIG['user']}")
    print(f"  Password: {'***' if DB_CONFIG['password'] else '❌ Empty'}")
    print(f"  Database: {DB_CONFIG['database']}")
    print()
    
    # Test connection
    try:
        from app.db import MySQLPool
        MySQLPool.init_pool()
        conn = MySQLPool.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 as test")
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        print("✅ Database Connection: SUCCESS")
        print(f"  Test query result: {result}")
        
    except Exception as e:
        print("❌ Database Connection: FAILED")
        print(f"  Error: {e}")
        print()
        print("💡 Troubleshooting:")
        print("  - Check if MySQL service is running")
        print("  - Verify connection credentials")
        print("  - Ensure database exists")
        print("  - Check network connectivity")

if __name__ == "__main__":
    test_db_config()
