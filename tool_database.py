"""
Database integration tools for Portia AI
Provides authenticated database operations for PostgreSQL, MySQL, and other databases
"""

import os
import json
from typing import Dict, List, Any, Optional, Annotated
from datetime import datetime
from dotenv import load_dotenv

# Optional Portia imports with graceful fallback
try:
    from portia import tool, ToolRegistry
    PORTIA_AVAILABLE = True
except ImportError:
    PORTIA_AVAILABLE = False
    
    # Fallback decorator when Portia is not available
    def tool(func):
        """Fallback tool decorator"""
        func._is_tool = True
        return func
    
    class ToolRegistry:
        """Fallback tool registry"""
        def __init__(self, tools):
            self.tools = tools

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

@tool
def query_postgres_database(
    query: Annotated[str, "SQL query to execute on PostgreSQL database"],
    params: Annotated[Optional[List], "Query parameters for prepared statements"] = None
) -> Dict[str, Any]:
    """
    Execute a SQL query on a PostgreSQL database with authentication.
    Supports SELECT, INSERT, UPDATE, DELETE operations with security.
    """
    if not POSTGRES_AVAILABLE:
        return {
            "error": "PostgreSQL driver not available",
            "message": "Install psycopg2-binary: pip install psycopg2-binary",
            "status": "failed"
        }
    
    try:
        # Validate query type for security
        query_type = query.strip().upper().split()[0]
        if query_type not in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH']:
            return {
                "error": "Unsupported query type",
                "message": f"Query type '{query_type}' is not allowed",
                "status": "failed"
            }
        
        # Connect to PostgreSQL
        connection = psycopg2.connect(**db_config.postgres_config)
        cursor = connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        
        # Execute query with parameters
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Handle different query types
        if query_type == 'SELECT' or query_type == 'WITH':
            results = cursor.fetchall()
            # Convert RealDictRow to regular dict for JSON serialization
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

@tool
def query_mysql_database(
    query: Annotated[str, "SQL query to execute on MySQL database"],
    params: Annotated[Optional[List], "Query parameters for prepared statements"] = None
) -> Dict[str, Any]:
    """
    Execute a SQL query on a MySQL database with authentication.
    Supports SELECT, INSERT, UPDATE, DELETE operations with security.
    """
    if not MYSQL_AVAILABLE:
        return {
            "error": "MySQL driver not available",
            "message": "Install mysql-connector-python: pip install mysql-connector-python",
            "status": "failed"
        }
    
    try:
        # Validate query type for security
        query_type = query.strip().upper().split()[0]
        if query_type not in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH']:
            return {
                "error": "Unsupported query type",
                "message": f"Query type '{query_type}' is not allowed",
                "status": "failed"
            }
        
        # Connect to MySQL
        connection = mysql.connector.connect(**db_config.mysql_config)
        cursor = connection.cursor(dictionary=True)
        
        # Execute query with parameters
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Handle different query types
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

@tool
def query_sqlite_database(
    query: Annotated[str, "SQL query to execute on SQLite database"],
    params: Annotated[Optional[List], "Query parameters for prepared statements"] = None
) -> Dict[str, Any]:
    """
    Execute a SQL query on a SQLite database.
    Supports SELECT, INSERT, UPDATE, DELETE operations with security.
    """
    if not SQLITE_AVAILABLE:
        return {
            "error": "SQLite not available",
            "message": "SQLite should be available in Python standard library",
            "status": "failed"
        }
    
    try:
        # Validate query type for security
        query_type = query.strip().upper().split()[0]
        if query_type not in ['SELECT', 'INSERT', 'UPDATE', 'DELETE', 'WITH', 'CREATE', 'DROP', 'ALTER']:
            return {
                "error": "Unsupported query type",
                "message": f"Query type '{query_type}' is not allowed",
                "status": "failed"
            }
        
        # Connect to SQLite
        connection = sqlite3.connect(db_config.sqlite_config['database'])
        connection.row_factory = sqlite3.Row  # Enable dict-like access
        cursor = connection.cursor()
        
        # Execute query with parameters
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        # Handle different query types
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

@tool
def get_database_schema(
    database_type: Annotated[str, "Database type: 'postgres', 'mysql', or 'sqlite'"],
    table_name: Annotated[Optional[str], "Specific table name (optional)"] = None
) -> Dict[str, Any]:
    """
    Get database schema information for tables and columns.
    Helps understand database structure for query generation.
    """
    try:
        if database_type.lower() == 'postgres':
            if table_name:
                query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s
                ORDER BY ordinal_position
                """
                return query_postgres_database(query, [table_name])
            else:
                query = """
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
                """
                return query_postgres_database(query)
        
        elif database_type.lower() == 'mysql':
            if table_name:
                query = """
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = DATABASE()
                ORDER BY ordinal_position
                """
                return query_mysql_database(query, [table_name])
            else:
                query = """
                SELECT table_name, table_type
                FROM information_schema.tables 
                WHERE table_schema = DATABASE()
                ORDER BY table_name
                """
                return query_mysql_database(query)
        
        elif database_type.lower() == 'sqlite':
            if table_name:
                query = f"PRAGMA table_info({table_name})"
                return query_sqlite_database(query)
            else:
                query = "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
                return query_sqlite_database(query)
        
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

# Create database tool registry - Pass tool instances when Portia is available
if PORTIA_AVAILABLE:
    try:
        database_tools = ToolRegistry([
            query_postgres_database(),
            query_mysql_database(),
            query_sqlite_database(),
            get_database_schema()
        ])
    except Exception as e:
        print(f"Warning: Could not create Portia database tools: {e}")
        database_tools = None
else:
    database_tools = None

# Helper functions for non-Portia usage
def get_database_tools():
    """Get all database tools for manual registration"""
    return [
        query_postgres_database,
        query_mysql_database,
        query_sqlite_database,
        get_database_schema
    ]

def test_database_connection(database_type: str) -> Dict[str, Any]:
    """Test database connection and return status"""
    try:
        if database_type.lower() == 'postgres':
            return query_postgres_database("SELECT version() as version, current_database() as database")
        elif database_type.lower() == 'mysql':
            return query_mysql_database("SELECT version() as version, database() as database")
        elif database_type.lower() == 'sqlite':
            return query_sqlite_database("SELECT sqlite_version() as version")
        else:
            return {"error": "Unsupported database type", "status": "failed"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}
