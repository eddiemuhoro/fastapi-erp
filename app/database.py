import mysql.connector
import os
from contextlib import contextmanager

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST', '26.147.247.74'),
        user=os.environ.get('MYSQL_USER', 'root'),
        password=os.environ.get('MYSQL_PASSWORD', '123*/'),
        database=os.environ.get('MYSQL_DATABASE', 'kipusa_cyber')
    )

@contextmanager
def get_db_cursor():
    """Context manager for database operations"""
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        yield cursor
    finally:
        cursor.close()
        conn.close()

def execute_query(query: str, params=None):
    """Execute a SELECT query and return all results"""
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchall()

def execute_single_query(query: str, params=None):
    """Execute a SELECT query and return single result"""
    with get_db_cursor() as cursor:
        cursor.execute(query, params or ())
        return cursor.fetchone()
