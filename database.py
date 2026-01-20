"""
Database connection and utility functions.
"""
import psycopg2
from psycopg2.extras import execute_batch
from contextlib import contextmanager
import logging
from typing import List, Dict, Any

from config import DB_CONFIG

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Handles PostgreSQL database connections and operations."""
    
    def __init__(self):
        self.config = DB_CONFIG
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = None
        try:
            conn = psycopg2.connect(**self.config)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute a SELECT query and return results as list of dicts."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                if cur.description:
                    columns = [desc[0] for desc in cur.description]
                    return [dict(zip(columns, row)) for row in cur.fetchall()]
                return []
    
    def execute_many(self, query: str, data: List[tuple]) -> int:
        """Execute batch insert/update operations."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                execute_batch(cur, query, data, page_size=100)
                return cur.rowcount
    
    def execute_script(self, script: str):
        """Execute a SQL script (e.g., for schema creation)."""
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(script)
                logger.info("SQL script executed successfully")


# Singleton instance
db = DatabaseConnection()
