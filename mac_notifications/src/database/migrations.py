"""
Database migration system for schema updates
"""

import sqlite3
import logging
from typing import List, Callable
from datetime import datetime

from .connection import DatabaseConnection

logger = logging.getLogger(__name__)


class Migration:
    """Represents a single database migration"""
    
    def __init__(self, version: int, name: str, up: Callable, down: Callable = None):
        """Initialize a migration
        
        Args:
            version: Migration version number
            name: Descriptive name for the migration
            up: Function to apply the migration
            down: Optional function to rollback the migration
        """
        self.version = version
        self.name = name
        self.up = up
        self.down = down or (lambda conn: None)


class MigrationManager:
    """Handle database schema migrations"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Initialize the migration manager
        
        Args:
            db_connection: Database connection manager
        """
        self.db = db_connection
        self._ensure_migration_table()
        self.migrations = self._define_migrations()
    
    def _ensure_migration_table(self):
        """Ensure the migration tracking table exists"""
        with self.db.get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    version INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
    
    def _define_migrations(self) -> List[Migration]:
        """Define all database migrations"""
        return [
            Migration(
                version=1,
                name="initial_schema",
                up=self._migration_1_initial_schema
            ),
            Migration(
                version=2,
                name="add_priority_fields",
                up=self._migration_2_add_priority_fields
            ),
            Migration(
                version=3,
                name="add_read_archive_fields",
                up=self._migration_3_add_read_archive_fields
            ),
            Migration(
                version=4,
                name="add_indexes",
                up=self._migration_4_add_indexes
            ),
        ]
    
    def _migration_1_initial_schema(self, conn: sqlite3.Connection):
        """Create the initial database schema"""
        # Create notifications table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                rec_id INTEGER UNIQUE,
                app_identifier TEXT,
                delivered_time TIMESTAMP,
                title TEXT,
                subtitle TEXT,
                body TEXT,
                category TEXT,
                thread TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create daemon metadata table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS daemon_metadata (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
    
    def _migration_2_add_priority_fields(self, conn: sqlite3.Connection):
        """Add priority scoring fields"""
        # Check if columns already exist
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(notifications)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'priority_score' not in columns:
            conn.execute("ALTER TABLE notifications ADD COLUMN priority_score REAL DEFAULT 0")
        
        if 'priority_level' not in columns:
            conn.execute("ALTER TABLE notifications ADD COLUMN priority_level TEXT DEFAULT 'MEDIUM'")
        
        if 'priority_factors' not in columns:
            conn.execute("ALTER TABLE notifications ADD COLUMN priority_factors TEXT DEFAULT '[]'")
    
    def _migration_3_add_read_archive_fields(self, conn: sqlite3.Connection):
        """Add read and archive status fields"""
        # Check if columns already exist
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(notifications)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'is_read' not in columns:
            conn.execute("ALTER TABLE notifications ADD COLUMN is_read BOOLEAN DEFAULT 0")
        
        if 'is_archived' not in columns:
            conn.execute("ALTER TABLE notifications ADD COLUMN is_archived BOOLEAN DEFAULT 0")
    
    def _migration_4_add_indexes(self, conn: sqlite3.Connection):
        """Add performance indexes"""
        # Index for time-based queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_delivered_time 
            ON notifications(delivered_time DESC)
        """)
        
        # Index for app-based queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_app_identifier 
            ON notifications(app_identifier)
        """)
        
        # Index for priority queries
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_priority 
            ON notifications(priority_level, priority_score DESC)
        """)
        
        # Index for unread notifications
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_notifications_unread 
            ON notifications(is_read, delivered_time DESC)
        """)
    
    def get_current_version(self) -> int:
        """Get the current schema version
        
        Returns:
            int: Current version number, 0 if no migrations applied
        """
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT MAX(version) FROM schema_migrations")
            result = cursor.fetchone()
            return result[0] if result[0] is not None else 0
    
    def get_pending_migrations(self) -> List[Migration]:
        """Get list of migrations that haven't been applied yet
        
        Returns:
            List of pending Migration objects
        """
        current_version = self.get_current_version()
        return [m for m in self.migrations if m.version > current_version]
    
    def migrate_to_version(self, target_version: int) -> None:
        """Migrate to a specific version
        
        Args:
            target_version: Version to migrate to
        """
        current_version = self.get_current_version()
        
        if target_version == current_version:
            logger.info(f"Already at version {target_version}")
            return
        
        if target_version > current_version:
            # Migrate up
            for migration in self.migrations:
                if current_version < migration.version <= target_version:
                    self._apply_migration(migration)
        else:
            # Migrate down
            for migration in reversed(self.migrations):
                if target_version < migration.version <= current_version:
                    self._rollback_migration(migration)
    
    def migrate_to_latest(self) -> None:
        """Migrate to the latest version"""
        if self.migrations:
            latest_version = max(m.version for m in self.migrations)
            self.migrate_to_version(latest_version)
    
    def _apply_migration(self, migration: Migration) -> None:
        """Apply a single migration
        
        Args:
            migration: Migration to apply
        """
        logger.info(f"Applying migration {migration.version}: {migration.name}")
        
        try:
            with self.db.get_connection() as conn:
                # Apply the migration
                migration.up(conn)
                
                # Record that it was applied
                conn.execute(
                    "INSERT INTO schema_migrations (version, name) VALUES (?, ?)",
                    (migration.version, migration.name)
                )
                
            logger.info(f"Successfully applied migration {migration.version}")
        except Exception as e:
            logger.error(f"Failed to apply migration {migration.version}: {e}")
            raise
    
    def _rollback_migration(self, migration: Migration) -> None:
        """Rollback a single migration
        
        Args:
            migration: Migration to rollback
        """
        logger.info(f"Rolling back migration {migration.version}: {migration.name}")
        
        try:
            with self.db.get_connection() as conn:
                # Rollback the migration
                migration.down(conn)
                
                # Remove the record
                conn.execute(
                    "DELETE FROM schema_migrations WHERE version = ?",
                    (migration.version,)
                )
                
            logger.info(f"Successfully rolled back migration {migration.version}")
        except Exception as e:
            logger.error(f"Failed to rollback migration {migration.version}: {e}")
            raise
    
    def get_migration_status(self) -> List[dict]:
        """Get the status of all migrations
        
        Returns:
            List of migration status dictionaries
        """
        current_version = self.get_current_version()
        
        # Get applied migrations info
        applied = {}
        with self.db.get_cursor() as cursor:
            cursor.execute("SELECT version, applied_at FROM schema_migrations")
            for row in cursor.fetchall():
                applied[row['version']] = row['applied_at']
        
        # Build status list
        status = []
        for migration in self.migrations:
            status.append({
                'version': migration.version,
                'name': migration.name,
                'applied': migration.version in applied,
                'applied_at': applied.get(migration.version),
                'is_current': migration.version == current_version
            })
        
        return status


def run_migrations(db_path: str = None) -> None:
    """Convenience function to run all pending migrations
    
    Args:
        db_path: Optional database path
    """
    from .connection import get_db_connection
    
    db = get_db_connection(db_path)
    manager = MigrationManager(db)
    
    pending = manager.get_pending_migrations()
    if pending:
        logger.info(f"Found {len(pending)} pending migrations")
        manager.migrate_to_latest()
        logger.info("All migrations completed successfully")
    else:
        logger.info("No pending migrations")
