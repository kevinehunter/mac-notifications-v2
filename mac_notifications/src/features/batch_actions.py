"""
Batch Actions Module - Feature #8
Provides batch operations on notifications including mark as read/unread,
delete, archive, and priority updates.
"""

import sqlite3
import time
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Union
import json
import uuid


class BatchActions:
    """Handles batch operations on notifications"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _generate_batch_id(self) -> str:
        """Generate a unique batch operation ID"""
        return f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    # Core Batch Operations
    
    def mark_as_read(self, notification_ids: List[int], dry_run: bool = False) -> Dict:
        """Mark notifications as read"""
        if not notification_ids:
            return {"success": True, "affected_count": 0, "ids": []}
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Get current state for potential undo
            placeholders = ','.join('?' * len(notification_ids))
            cursor.execute(
                f"SELECT id, is_read FROM notifications WHERE id IN ({placeholders})",
                notification_ids
            )
            current_state = cursor.fetchall()
            
            if dry_run:
                unread_count = sum(1 for row in current_state if not row['is_read'])
                return {
                    "success": True,
                    "dry_run": True,
                    "would_affect": unread_count,
                    "ids": [row['id'] for row in current_state if not row['is_read']]
                }
            
            # Perform the update
            batch_id = self._generate_batch_id()
            cursor.execute(
                f"""UPDATE notifications 
                    SET is_read = 1, batch_id = ? 
                    WHERE id IN ({placeholders}) AND is_read = 0""",
                [batch_id] + notification_ids
            )
            
            affected_count = cursor.rowcount
            conn.commit()
            
            return {
                "success": True,
                "affected_count": affected_count,
                "batch_id": batch_id,
                "ids": [row['id'] for row in current_state if not row['is_read']]
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def mark_as_unread(self, notification_ids: List[int], dry_run: bool = False) -> Dict:
        """Mark notifications as unread"""
        if not notification_ids:
            return {"success": True, "affected_count": 0, "ids": []}
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            placeholders = ','.join('?' * len(notification_ids))
            cursor.execute(
                f"SELECT id, is_read FROM notifications WHERE id IN ({placeholders})",
                notification_ids
            )
            current_state = cursor.fetchall()
            
            if dry_run:
                read_count = sum(1 for row in current_state if row['is_read'])
                return {
                    "success": True,
                    "dry_run": True,
                    "would_affect": read_count,
                    "ids": [row['id'] for row in current_state if row['is_read']]
                }
            
            batch_id = self._generate_batch_id()
            cursor.execute(
                f"""UPDATE notifications 
                    SET is_read = 0, batch_id = ? 
                    WHERE id IN ({placeholders}) AND is_read = 1""",
                [batch_id] + notification_ids
            )
            
            affected_count = cursor.rowcount
            conn.commit()
            
            return {
                "success": True,
                "affected_count": affected_count,
                "batch_id": batch_id,
                "ids": [row['id'] for row in current_state if row['is_read']]
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def archive_notifications(self, notification_ids: List[int], dry_run: bool = False) -> Dict:
        """Archive notifications"""
        if not notification_ids:
            return {"success": True, "affected_count": 0, "ids": []}
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if archive columns exist
            cursor.execute("PRAGMA table_info(notifications)")
            columns = [col[1] for col in cursor.fetchall()]
            has_archive_fields = 'archived' in columns
            
            if not has_archive_fields:
                # Add archive fields if they don't exist
                cursor.execute("ALTER TABLE notifications ADD COLUMN archived INTEGER DEFAULT 0")
                cursor.execute("ALTER TABLE notifications ADD COLUMN archived_at REAL")
                cursor.execute("ALTER TABLE notifications ADD COLUMN batch_id TEXT")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_archived ON notifications(archived)")
                conn.commit()
            
            placeholders = ','.join('?' * len(notification_ids))
            
            if dry_run:
                cursor.execute(
                    f"SELECT COUNT(*) as count FROM notifications WHERE id IN ({placeholders}) AND (archived IS NULL OR archived = 0)",
                    notification_ids
                )
                count = cursor.fetchone()['count']
                return {
                    "success": True,
                    "dry_run": True,
                    "would_archive": count,
                    "ids": notification_ids[:count]  # Approximate
                }
            
            batch_id = self._generate_batch_id()
            archived_at = time.time()
            
            cursor.execute(
                f"""UPDATE notifications 
                    SET archived = 1, archived_at = ?, batch_id = ? 
                    WHERE id IN ({placeholders}) AND (archived IS NULL OR archived = 0)""",
                [archived_at, batch_id] + notification_ids
            )
            
            affected_count = cursor.rowcount
            conn.commit()
            
            return {
                "success": True,
                "affected_count": affected_count,
                "batch_id": batch_id,
                "archived_at": datetime.fromtimestamp(archived_at).isoformat()
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def delete_notifications(self, notification_ids: List[int], dry_run: bool = False) -> Dict:
        """Delete notifications permanently"""
        if not notification_ids:
            return {"success": True, "deleted_count": 0, "ids": []}
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            placeholders = ','.join('?' * len(notification_ids))
            
            # Get info about notifications to be deleted
            cursor.execute(
                f"SELECT id, title, app_identifier FROM notifications WHERE id IN ({placeholders})",
                notification_ids
            )
            to_delete = cursor.fetchall()
            
            if dry_run:
                return {
                    "success": True,
                    "dry_run": True,
                    "would_delete": len(to_delete),
                    "ids": [row['id'] for row in to_delete],
                    "preview": [
                        {"id": row['id'], "title": row['title'], "app": row['app_identifier']}
                        for row in to_delete[:5]  # Show first 5
                    ]
                }
            
            # Perform deletion
            cursor.execute(
                f"DELETE FROM notifications WHERE id IN ({placeholders})",
                notification_ids
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            
            return {
                "success": True,
                "deleted_count": deleted_count,
                "ids": [row['id'] for row in to_delete]
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    def update_priority(self, notification_ids: List[int], new_priority: int, dry_run: bool = False) -> Dict:
        """Update priority for notifications"""
        if not notification_ids or new_priority not in [1, 2, 3, 4]:
            return {"success": False, "error": "Invalid priority level. Must be 1-4."}
            
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            placeholders = ','.join('?' * len(notification_ids))
            
            if dry_run:
                cursor.execute(
                    f"SELECT COUNT(*) as count FROM notifications WHERE id IN ({placeholders}) AND priority != ?",
                    notification_ids + [new_priority]
                )
                count = cursor.fetchone()['count']
                return {
                    "success": True,
                    "dry_run": True,
                    "would_update": count,
                    "new_priority": new_priority
                }
            
            batch_id = self._generate_batch_id()
            cursor.execute(
                f"""UPDATE notifications 
                    SET priority = ?, batch_id = ? 
                    WHERE id IN ({placeholders}) AND priority != ?""",
                [new_priority, batch_id] + notification_ids + [new_priority]
            )
            
            affected_count = cursor.rowcount
            conn.commit()
            
            priority_names = {1: "CRITICAL", 2: "HIGH", 3: "MEDIUM", 4: "LOW"}
            
            return {
                "success": True,
                "affected_count": affected_count,
                "batch_id": batch_id,
                "new_priority": priority_names[new_priority]
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "error": str(e)}
        finally:
            conn.close()
    
    # Selection Methods
    
    def select_by_time_range(self, start_time: Optional[float] = None, end_time: Optional[float] = None, 
                            older_than_days: Optional[int] = None) -> List[int]:
        """Select notifications by time range"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if older_than_days:
                cutoff_time = time.time() - (older_than_days * 86400)
                cursor.execute(
                    "SELECT id FROM notifications WHERE timestamp < ? AND (archived IS NULL OR archived = 0)",
                    (cutoff_time,)
                )
            else:
                conditions = []
                params = []
                
                if start_time:
                    conditions.append("timestamp >= ?")
                    params.append(start_time)
                if end_time:
                    conditions.append("timestamp <= ?")
                    params.append(end_time)
                
                conditions.append("(archived IS NULL OR archived = 0)")
                
                query = f"SELECT id FROM notifications WHERE {' AND '.join(conditions)}"
                cursor.execute(query, params)
            
            return [row['id'] for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def select_by_app(self, app_identifier: str, pattern: bool = False) -> List[int]:
        """Select notifications by app"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            if pattern:
                cursor.execute(
                    "SELECT id FROM notifications WHERE LOWER(app_identifier) LIKE LOWER(?) AND (archived IS NULL OR archived = 0)",
                    (f"%{app_identifier}%",)
                )
            else:
                cursor.execute(
                    "SELECT id FROM notifications WHERE LOWER(app_identifier) = LOWER(?) AND (archived IS NULL OR archived = 0)",
                    (app_identifier,)
                )
            
            return [row['id'] for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def select_by_priority(self, priority: Union[int, str]) -> List[int]:
        """Select notifications by priority"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Convert string priority to number
            if isinstance(priority, str):
                priority_map = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
                priority = priority_map.get(priority.upper(), 3)
            
            cursor.execute(
                "SELECT id FROM notifications WHERE priority = ? AND (archived IS NULL OR archived = 0)",
                (priority,)
            )
            
            return [row['id'] for row in cursor.fetchall()]
            
        finally:
            conn.close()
    
    def select_by_search(self, search_params: Dict) -> List[int]:
        """Select notifications based on search parameters"""
        # This would integrate with the enhanced search module
        # For now, return empty list
        return []
    
    def select_by_group(self, group_notifications: List[Dict]) -> List[int]:
        """Extract notification IDs from a group"""
        ids = []
        for notification in group_notifications:
            if isinstance(notification, dict) and 'id' in notification:
                ids.append(notification['id'])
        return ids
    
    # Utility Methods
    
    def get_batch_info(self, batch_id: str) -> Dict:
        """Get information about a batch operation"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT COUNT(*) as count, MIN(timestamp) as min_time, MAX(timestamp) as max_time FROM notifications WHERE batch_id = ?",
                (batch_id,)
            )
            
            result = cursor.fetchone()
            
            return {
                "batch_id": batch_id,
                "affected_count": result['count'],
                "time_range": {
                    "start": datetime.fromtimestamp(result['min_time']).isoformat() if result['min_time'] else None,
                    "end": datetime.fromtimestamp(result['max_time']).isoformat() if result['max_time'] else None
                }
            }
            
        finally:
            conn.close()
    
    def undo_batch(self, batch_id: str) -> Dict:
        """Undo a batch operation (limited support)"""
        # This is a placeholder for future undo functionality
        # Would need to store operation history for full undo support
        return {"success": False, "error": "Undo not yet implemented"}