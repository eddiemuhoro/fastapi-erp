"""
Improved database layer with connection pooling and better error handling
"""
import mysql.connector
from mysql.connector import pooling
import os
import logging
from contextlib import contextmanager
from typing import List, Dict, Any, Optional

from app.config import settings
from app.exceptions import DatabaseError

logger = logging.getLogger(__name__)

# Connection pool configuration
pool_config = {
    'pool_name': 'wholesale_pool',
    'pool_size': settings.mysql_pool_size,
    'pool_reset_session': True,
    'host': settings.mysql_host,
    'port': settings.mysql_port,
    'user': settings.mysql_user,
    'password': settings.mysql_password,
    'database': settings.mysql_database,
    'autocommit': True,
    'charset': 'utf8mb4',
    'collation': 'utf8mb4_unicode_ci'
}

# Global connection pool
_connection_pool: Optional[pooling.MySQLConnectionPool] = None

def get_connection_pool() -> pooling.MySQLConnectionPool:
    """Get or create connection pool"""
    global _connection_pool
    
    if _connection_pool is None:
        try:
            _connection_pool = pooling.MySQLConnectionPool(**pool_config)
            logger.info("Database connection pool created successfully")
        except Exception as e:
            logger.error(f"Failed to create connection pool: {e}")
            raise DatabaseError(f"Database connection failed: {str(e)}")
    
    return _connection_pool

def get_db_connection():
    """Get a connection from the pool"""
    try:
        pool = get_connection_pool()
        return pool.get_connection()
    except Exception as e:
        logger.error(f"Failed to get database connection: {e}")
        raise DatabaseError(f"Database connection failed: {str(e)}")

@contextmanager
def get_db_cursor():
    """Context manager for database operations with better error handling"""
    conn = None
    cursor = None
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        yield cursor
    except mysql.connector.Error as e:
        logger.error(f"Database error: {e}")
        if conn:
            conn.rollback()
        raise DatabaseError(f"Database operation failed: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        if conn:
            conn.rollback()
        raise DatabaseError(f"Unexpected database error: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def execute_query(query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """Execute a SELECT query and return all results"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            logger.debug(f"Query executed successfully, returned {len(results)} rows")
            return results
    except Exception as e:
        logger.error(f"Query execution failed: {query[:100]}... Error: {e}")
        raise

def execute_single_query(query: str, params: Optional[tuple] = None) -> Optional[Dict[str, Any]]:
    """Execute a SELECT query and return single result"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(query, params or ())
            result = cursor.fetchone()
            logger.debug(f"Single query executed successfully")
            return result
    except Exception as e:
        logger.error(f"Single query execution failed: {query[:100]}... Error: {e}")
        raise

def execute_write_query(query: str, params: Optional[tuple] = None) -> int:
    """Execute INSERT/UPDATE/DELETE query and return affected rows"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute(query, params or ())
            affected_rows = cursor.rowcount
            logger.debug(f"Write query executed successfully, affected {affected_rows} rows")
            return affected_rows
    except Exception as e:
        logger.error(f"Write query execution failed: {query[:100]}... Error: {e}")
        raise

def test_connection() -> bool:
    """Test database connection"""
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            return result is not None
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False
