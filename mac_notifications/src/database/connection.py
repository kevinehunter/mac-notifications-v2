"""
Database connection management for the notification system
"""

import sqlite3
from contextlib import contextmanager
from typing import Generator, Optional
from pathlib import Path
import logging

from ..config.settings import Settings

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """Manages database connections with proper resource handling"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the database connection manager
        
        Args:
            db_path: Path to the database file. If None, uses default from settings.
        """
        self.settings = Settings()
        self.db_path = db_path or str(self.settings.DEFAULT_DB_PATH)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Ensure the database file and directory exist"""
        db_path = Path(self.db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not db_path.exists():
            logger.info(f"Creating new database at {self.db_path}")
            # Create empty database
            conn = sqlite3.connect(self.db_path)
            conn.close()
    
    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager for database connections
        
        Yields:
            sqlite3.Connection: Database connection with row factory set
        """
        conn = None
        try:
            conn = sqlite3.connect(
                self.db_path,
                timeout=self.settings.DB_TIMEOUT
            )
            # Enable row factory for dict-like access
            conn.row_factory = sqlite3.Row
            
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            
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
    
    @contextmanager
    def get_cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager for database cursors
        
        Yields:
            sqlite3.Cursor: Database cursor
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            yield cursor
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a single query
        
        Args:
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            sqlite3.Cursor: Cursor with results
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            return cursor.execute(query, params)
    
    def executemany(self, query: str, params_list: list) -> None:
        """Execute a query with multiple parameter sets
        
        Args:
            query: SQL query to execute
            params_list: List of parameter tuples
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
    
    def table_exists(self, table_name: str) -> bool:
        """Check if a table exists in the database
        
        Args:
            table_name: Name of the table to check
            
        Returns:
            bool: True if table exists
        """
        with self.get_cursor() as cursor:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table_name,)
            )
            return cursor.fetchone() is not None
    
    def get_table_info(self, table_name: str) -> list:
        """Get information about table columns
        
        Args:
            table_name: Name of the table
            
        Returns:
            list: List of column information
        """
        with self.get_cursor() as cursor:
            cursor.execute(f"PRAGMA table_info({table_name})")
            return cursor.fetchall()


# Global connection instance
_db_connection: Optional[DatabaseConnection] = None


def get_db_connection(db_path: Optional[str] = None) -> DatabaseConnection:
    """Get or create the global database connection manager
    
    Args:
        db_path: Optional database path override
        
    Returns:
        DatabaseConnection: The connection manager instance
    """
    global _db_connection
    
    if _db_connection is None or (db_path and db_path != _db_connection.db_path):
        _db_connection = DatabaseConnection(db_path)
    
    return _db_connection