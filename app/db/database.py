import psycopg2
from typing import Generator
from app.core.config import settings


def get_db() -> Generator:
    """Database dependency for FastAPI."""
    conn = psycopg2.connect(settings.DATABASE_URL)
    try:
        yield conn
    finally:
        conn.close()


class DatabaseManager:
    """Database manager for handling database operations."""
    
    @staticmethod
    def execute_query(db_conn, query: str, params: tuple = None):
        """Execute a query and return results."""
        cur = db_conn.cursor()
        if params:
            cur.execute(query, params)
        else:
            cur.execute(query)
        
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description] if cur.description else []
        cur.close()
        
        return rows, columns
    
    @staticmethod
    def execute_insert(db_conn, query: str, params: tuple):
        """Execute an insert/update query."""
        cur = db_conn.cursor()
        cur.execute(query, params)
        db_conn.commit()
        cur.close()
    
    @staticmethod
    def create_table_if_not_exists(db_conn, create_query: str):
        """Create table if it doesn't exist."""
        cur = db_conn.cursor()
        cur.execute(create_query)
        db_conn.commit()
        cur.close()
