"""
Direct function calls for tools without Portia wrapper
This module provides direct access to tool functions for API endpoints
"""

import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from dotenv import load_dotenv

# Database connection imports with optional fallbacks
try:
    import psycopg2
    import psycopg2.extras
    POSTGRES_AVAILABLE = True
except ImportError:
    POSTGRES_AVAILABLE = False

try:
    import mysql.connector
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False

try:
    import sqlite3
    SQLITE_AVAILABLE = True
except ImportError:
    SQLITE_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# Load environment variables
load_dotenv()

class DatabaseConfig:
    """Database configuration manager"""
    
    def __init__(self):
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'database': os.getenv('POSTGRES_DB', 'workbench'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', '')
        }
        
        self.mysql_config = {
            'host': os.getenv('MYSQL_HOST', 'localhost'),
            'port': os.getenv('MYSQL_PORT', '3306'),
            'database': os.getenv('MYSQL_DB', 'workbench'),
            'user': os.getenv('MYSQL_USER', 'root'),
            'password': os.getenv('MYSQL_PASSWORD', '')
        }
        
        self.sqlite_config = {
            'database': os.getenv('SQLITE_DB', 'workbench.db')
        }

db_config = DatabaseConfig()

def direct_query_postgres_database(query: str, params: Optional[List] = None) -> Dict[str, Any]:
    """Execute a SQL query on a PostgreSQL database"""
    if not POSTGRES_AVAILABLE:
        return {
            "error": "PostgreSQL driver not available",
            "message": "Install psycopg2-binary: pip install psycopg2-binary",
            "status": "failed"
        }
    
    try:
        query_type = query.strip().upper().split()[0]
        if query_type not in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH']:
            return {
                "error": "Unsupported query type",
                "message": f"Query type '{query_type}' is not allowed",
                "status": "failed"
            }
        
        connection = psycopg2.connect(**db_config.postgres_config)
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query_type == 'SELECT' or query_type == 'WITH':
            results = cursor.fetchall()
            results = [dict(row) for row in results]
        else:
            connection.commit()
            results = {"affected_rows": cursor.rowcount}
        
        cursor.close()
        connection.close()
        
        return {
            "status": "success",
            "data": results,
            "query_type": query_type,
            "timestamp": datetime.now().isoformat(),
            "database": "PostgreSQL"
        }
        
    except psycopg2.Error as e:
        return {
            "error": "Database error",
            "message": str(e),
            "status": "failed",
            "database": "PostgreSQL"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "status": "failed",
            "database": "PostgreSQL"
        }

def direct_query_mysql_database(query: str, params: Optional[List] = None) -> Dict[str, Any]:
    """Execute a SQL query on a MySQL database"""
    if not MYSQL_AVAILABLE:
        return {
            "error": "MySQL driver not available",
            "message": "Install mysql-connector-python: pip install mysql-connector-python",
            "status": "failed"
        }
    
    try:
        query_type = query.strip().upper().split()[0]
        if query_type not in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH']:
            return {
                "error": "Unsupported query type",
                "message": f"Query type '{query_type}' is not allowed",
                "status": "failed"
            }
        
        connection = mysql.connector.connect(**db_config.mysql_config)
        cursor = connection.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query_type == 'SELECT' or query_type == 'WITH':
            results = cursor.fetchall()
        else:
            connection.commit()
            results = {"affected_rows": cursor.rowcount}
        
        cursor.close()
        connection.close()
        
        return {
            "status": "success",
            "data": results,
            "query_type": query_type,
            "timestamp": datetime.now().isoformat(),
            "database": "MySQL"
        }
        
    except mysql.connector.Error as e:
        return {
            "error": "Database error",
            "message": str(e),
            "status": "failed",
            "database": "MySQL"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "status": "failed",
            "database": "MySQL"
        }

def direct_query_sqlite_database(query: str, params: Optional[List] = None) -> Dict[str, Any]:
    """Execute a SQL query on a SQLite database"""
    if not SQLITE_AVAILABLE:
        return {
            "error": "SQLite not available",
            "message": "SQLite should be available in Python standard library",
            "status": "failed"
        }
    
    try:
        query_type = query.strip().upper().split()[0]
        if query_type not in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH', 'CREATE', 'DROP', 'ALTER']:
            return {
                "error": "Unsupported query type",
                "message": f"Query type '{query_type}' is not allowed",
                "status": "failed"
            }
        
        connection = sqlite3.connect(db_config.sqlite_config['database'])
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if query_type in ['SELECT', 'WITH']:
            results = [dict(row) for row in cursor.fetchall()]
        else:
            connection.commit()
            results = {"affected_rows": cursor.rowcount}
        
        cursor.close()
        connection.close()
        
        return {
            "status": "success",
            "data": results,
            "query_type": query_type,
            "timestamp": datetime.now().isoformat(),
            "database": "SQLite"
        }
        
    except sqlite3.Error as e:
        return {
            "error": "Database error",
            "message": str(e),
            "status": "failed",
            "database": "SQLite"
        }
    except Exception as e:
        return {
            "error": "Unexpected error",
            "message": str(e),
            "status": "failed",
            "database": "SQLite"
        }

def direct_get_database_schema(database_type: str, table_name: Optional[str] = None) -> Dict[str, Any]:
    """Get database schema information"""
    try:
        if database_type.lower() == 'postgres':
            if table_name:
                query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
                """
                return direct_query_postgres_database(query, [table_name])
            else:
                query = """
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
                return direct_query_postgres_database(query)
        
        elif database_type.lower() == 'mysql':
            if table_name:
                query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = DATABASE()
                ORDER BY ordinal_position
                """
                return direct_query_mysql_database(query, [table_name])
            else:
                query = """
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                ORDER BY table_name
                """
                return direct_query_mysql_database(query)
        
        elif database_type.lower() == 'sqlite':
            if table_name:
                query = f"PRAGMA table_info({table_name})"
                return direct_query_sqlite_database(query)
            else:
                query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                return direct_query_sqlite_database(query)
        
        else:
            return {
                "error": "Unsupported database type",
                "message": f"Database type '{database_type}' is not supported",
                "status": "failed"
            }
    
    except Exception as e:
        return {
            "error": "Schema query failed",
            "message": str(e),
            "status": "failed"
        }

# Test connection functions
def direct_test_database_connection(database_type: str) -> Dict[str, Any]:
    """Test database connection and return status"""
    try:
        if database_type.lower() == 'postgres':
            return direct_query_postgres_database("SELECT version() as version, current_database() as database")
        elif database_type.lower() == 'mysql':
            return direct_query_mysql_database("SELECT version() as version, database() as database")
        elif database_type.lower() == 'sqlite':
            return direct_query_sqlite_database("SELECT sqlite_version() as version")
        else:
            return {"error": "Unsupported database type", "status": "failed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}
