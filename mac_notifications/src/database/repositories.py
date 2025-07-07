"""
Repository pattern for database operations
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any, Tuple

from .connection import DatabaseConnection
from .models import Notification, DaemonMetadata


class NotificationRepository:
    """Handle all notification-related database operations"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Initialize the repository
        
        Args:
            db_connection: Database connection manager
        """
        self.db = db_connection
    
    def get_recent(self, limit: int = 10, offset: int = 0) -> List[Notification]:
        """Get recent notifications
        
        Args:
            limit: Maximum number of notifications to return
            offset: Number of notifications to skip
            
        Returns:
            List of Notification objects
        """
        query = """
            SELECT * FROM notifications 
            ORDER BY delivered_time DESC, rec_id DESC
            LIMIT ? OFFSET ?
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (limit, offset))
            return [Notification.from_db_row(dict(row)) for row in cursor.fetchall()]
    
    def get_by_id(self, rec_id: int) -> Optional[Notification]:
        """Get a notification by its record ID
        
        Args:
            rec_id: Record ID
            
        Returns:
            Notification object or None if not found
        """
        query = "SELECT * FROM notifications WHERE rec_id = ?"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (rec_id,))
            row = cursor.fetchone()
            return Notification.from_db_row(dict(row)) if row else None
    
    def get_by_priority(self, priority_level: str, limit: int = 50) -> List[Notification]:
        """Get notifications by priority level
        
        Args:
            priority_level: Priority level (CRITICAL, HIGH, MEDIUM, LOW)
            limit: Maximum number of notifications
            
        Returns:
            List of Notification objects
        """
        query = """
            SELECT * FROM notifications 
            WHERE priority_level = ?
            ORDER BY priority_score DESC, delivered_time DESC
            LIMIT ?
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (priority_level, limit))
            return [Notification.from_db_row(dict(row)) for row in cursor.fetchall()]
    
    def get_important(self, limit: int = 20) -> List[Notification]:
        """Get important notifications (CRITICAL and HIGH priority)
        
        Args:
            limit: Maximum number of notifications
            
        Returns:
            List of Notification objects
        """
        query = """
            SELECT * FROM notifications 
            WHERE priority_level IN ('CRITICAL', 'HIGH')
            ORDER BY priority_score DESC, delivered_time DESC
            LIMIT ?
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (limit,))
            return [Notification.from_db_row(dict(row)) for row in cursor.fetchall()]
    
    def search(self, keyword: str, app: Optional[str] = None, limit: int = 50) -> List[Notification]:
        """Search notifications by keyword and/or app
        
        Args:
            keyword: Keyword to search for
            app: Optional app identifier filter
            limit: Maximum number of results
            
        Returns:
            List of Notification objects
        """
        query = """
            SELECT * FROM notifications 
            WHERE 1=1
        """
        params = []
        
        if keyword:
            query += """
                AND (
                    LOWER(title) LIKE ? 
                    OR LOWER(subtitle) LIKE ?
                    OR LOWER(body) LIKE ?
                    OR LOWER(app_identifier) LIKE ?
                )
            """
            keyword_pattern = f"%{keyword.lower()}%"
            params.extend([keyword_pattern] * 4)
        
        if app:
            query += " AND LOWER(app_identifier) LIKE ?"
            params.append(f"%{app.lower()}%")
        
        query += " ORDER BY delivered_time DESC LIMIT ?"
        params.append(limit)
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, params)
            return [Notification.from_db_row(dict(row)) for row in cursor.fetchall()]
    
    def get_since(self, since_time: str) -> List[Notification]:
        """Get notifications since a specific time
        
        Args:
            since_time: Time string in format 'YYYY-MM-DD HH:MM:SS'
            
        Returns:
            List of Notification objects
        """
        query = """
            SELECT * FROM notifications 
            WHERE datetime(delivered_time) > datetime(?)
            ORDER BY delivered_time DESC
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (since_time,))
            return [Notification.from_db_row(dict(row)) for row in cursor.fetchall()]
    
    def get_by_time_range(self, start_time: datetime, end_time: datetime) -> List[Notification]:
        """Get notifications within a time range
        
        Args:
            start_time: Start of time range
            end_time: End of time range
            
        Returns:
            List of Notification objects
        """
        query = """
            SELECT * FROM notifications 
            WHERE datetime(delivered_time) BETWEEN datetime(?) AND datetime(?)
            ORDER BY delivered_time DESC
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (
                start_time.strftime('%Y-%m-%d %H:%M:%S'),
                end_time.strftime('%Y-%m-%d %H:%M:%S')
            ))
            return [Notification.from_db_row(dict(row)) for row in cursor.fetchall()]
    
    def update_priority(self, rec_id: int, priority_score: float, 
                       priority_level: str, priority_factors: List[str]) -> bool:
        """Update priority information for a notification
        
        Args:
            rec_id: Record ID
            priority_score: New priority score
            priority_level: New priority level
            priority_factors: List of priority factors
            
        Returns:
            bool: True if update successful
        """
        query = """
            UPDATE notifications 
            SET priority_score = ?, priority_level = ?, priority_factors = ?
            WHERE rec_id = ?
        """
        
        try:
            with self.db.get_cursor() as cursor:
                cursor.execute(query, (
                    priority_score,
                    priority_level,
                    json.dumps(priority_factors),
                    rec_id
                ))
                return cursor.rowcount > 0
        except Exception:
            return False
    
    def mark_as_read(self, rec_ids: List[int]) -> int:
        """Mark notifications as read
        
        Args:
            rec_ids: List of record IDs to mark as read
            
        Returns:
            int: Number of notifications updated
        """
        if not rec_ids:
            return 0
        
        placeholders = ','.join(['?' for _ in rec_ids])
        query = f"UPDATE notifications SET is_read = 1 WHERE rec_id IN ({placeholders})"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, rec_ids)
            return cursor.rowcount
    
    def mark_as_unread(self, rec_ids: List[int]) -> int:
        """Mark notifications as unread
        
        Args:
            rec_ids: List of record IDs to mark as unread
            
        Returns:
            int: Number of notifications updated
        """
        if not rec_ids:
            return 0
        
        placeholders = ','.join(['?' for _ in rec_ids])
        query = f"UPDATE notifications SET is_read = 0 WHERE rec_id IN ({placeholders})"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, rec_ids)
            return cursor.rowcount
    
    def archive(self, rec_ids: List[int]) -> int:
        """Archive notifications
        
        Args:
            rec_ids: List of record IDs to archive
            
        Returns:
            int: Number of notifications archived
        """
        if not rec_ids:
            return 0
        
        placeholders = ','.join(['?' for _ in rec_ids])
        query = f"UPDATE notifications SET is_archived = 1 WHERE rec_id IN ({placeholders})"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, rec_ids)
            return cursor.rowcount
    
    def delete(self, rec_ids: List[int]) -> int:
        """Delete notifications
        
        Args:
            rec_ids: List of record IDs to delete
            
        Returns:
            int: Number of notifications deleted
        """
        if not rec_ids:
            return 0
        
        placeholders = ','.join(['?' for _ in rec_ids])
        query = f"DELETE FROM notifications WHERE rec_id IN ({placeholders})"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, rec_ids)
            return cursor.rowcount
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get notification statistics
        
        Returns:
            Dictionary with various statistics
        """
        stats = {}
        
        with self.db.get_cursor() as cursor:
            # Total count
            cursor.execute("SELECT COUNT(*) FROM notifications")
            stats['total'] = cursor.fetchone()[0]
            
            # By app
            cursor.execute("""
                SELECT app_identifier, COUNT(*) as count 
                FROM notifications 
                GROUP BY app_identifier 
                ORDER BY count DESC
                LIMIT 15
            """)
            stats['by_app'] = dict(cursor.fetchall())
            
            # By priority (if available)
            cursor.execute("PRAGMA table_info(notifications)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'priority_level' in columns:
                cursor.execute("""
                    SELECT priority_level, COUNT(*) 
                    FROM notifications 
                    GROUP BY priority_level
                """)
                stats['by_priority'] = dict(cursor.fetchall())
            
            # Date range
            cursor.execute("""
                SELECT MIN(delivered_time), MAX(delivered_time) 
                FROM notifications
            """)
            date_range = cursor.fetchone()
            stats['date_range'] = {
                'oldest': date_range[0] if date_range else None,
                'newest': date_range[1] if date_range else None
            }
        
        return stats
    
    def cleanup_old(self, days: int = 30) -> int:
        """Delete notifications older than specified days
        
        Args:
            days: Number of days to keep
            
        Returns:
            int: Number of notifications deleted
        """
        cutoff_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d %H:%M:%S')
        query = "DELETE FROM notifications WHERE datetime(delivered_time) < datetime(?)"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (cutoff_date,))
            return cursor.rowcount


class DaemonMetadataRepository:
    """Handle daemon metadata operations"""
    
    def __init__(self, db_connection: DatabaseConnection):
        """Initialize the repository
        
        Args:
            db_connection: Database connection manager
        """
        self.db = db_connection
    
    def get(self, key: str) -> Optional[str]:
        """Get a metadata value by key
        
        Args:
            key: Metadata key
            
        Returns:
            str: Value or None if not found
        """
        query = "SELECT value FROM daemon_metadata WHERE key = ?"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (key,))
            row = cursor.fetchone()
            return row['value'] if row else None
    
    def set(self, key: str, value: str) -> None:
        """Set a metadata value
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        query = """
            INSERT OR REPLACE INTO daemon_metadata (key, value, updated_at)
            VALUES (?, ?, datetime('now'))
        """
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query, (key, value))
    
    def get_all(self) -> Dict[str, str]:
        """Get all metadata as a dictionary
        
        Returns:
            Dict mapping keys to values
        """
        query = "SELECT key, value FROM daemon_metadata"
        
        with self.db.get_cursor() as cursor:
            cursor.execute(query)
            return dict(cursor.fetchall())
    
    def update_last_update(self) -> None:
        """Update the last_update timestamp to current time"""
        self.set('last_update', datetime.now().isoformat())
    
    def update_last_rec_id(self, rec_id: int) -> None:
        """Update the last processed record ID
        
        Args:
            rec_id: Last processed record ID
        """
        self.set('last_rec_id', str(rec_id))