#!/usr/bin/env python3
"""
Unified Notification Monitoring Daemon
Consolidates all daemon functionality with improved architecture
"""

import sqlite3
import os
import plistlib
import json
import time
import logging
import shutil
import tempfile
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import signal
import sys
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from contextlib import contextmanager

# Configuration defaults
DEFAULT_UPDATE_INTERVAL = 10
DEFAULT_CLEANUP_DAYS = 30
DEFAULT_DB_NAME = "notifications.db"
MACOS_DB_PATH = os.path.expanduser("~/Library/Group Containers/group.com.apple.usernoted/db2/db")


@dataclass
class NotificationData:
    """Data class for notification structure"""
    rec_id: int
    app_identifier: str
    delivered_time: str
    title: str = ""
    subtitle: str = ""
    body: str = ""
    category: str = ""
    thread: str = ""
    priority_score: float = 0.0
    priority_level: str = "UNKNOWN"
    priority_factors: List[str] = None
    raw_data: bytes = None
    is_read: bool = False
    is_archived: bool = False
    
    def __post_init__(self):
        if self.priority_factors is None:
            self.priority_factors = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for database storage"""
        data = asdict(self)
        # Convert priority_factors list to JSON string
        data['priority_factors'] = json.dumps(data['priority_factors'])
        return data


class DatabaseManager:
    """Handles all database operations"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialize the database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Create main notifications table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    rec_id INTEGER UNIQUE,
                    app_identifier TEXT,
                    delivered_time TEXT,
                    title TEXT,
                    subtitle TEXT,
                    body TEXT,
                    category TEXT,
                    thread TEXT,
                    priority_score REAL DEFAULT 0,
                    priority_level TEXT DEFAULT 'UNKNOWN',
                    priority_factors TEXT DEFAULT '[]',
                    is_read BOOLEAN DEFAULT FALSE,
                    is_archived BOOLEAN DEFAULT FALSE,
                    raw_data BLOB,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            indexes = [
                'CREATE INDEX IF NOT EXISTS idx_rec_id ON notifications(rec_id)',
                'CREATE INDEX IF NOT EXISTS idx_delivered_time ON notifications(delivered_time)',
                'CREATE INDEX IF NOT EXISTS idx_app_identifier ON notifications(app_identifier)',
                'CREATE INDEX IF NOT EXISTS idx_priority_score ON notifications(priority_score DESC)',
                'CREATE INDEX IF NOT EXISTS idx_priority_level ON notifications(priority_level)',
                'CREATE INDEX IF NOT EXISTS idx_is_archived ON notifications(is_archived)',
            ]
            
            for index in indexes:
                cursor.execute(index)
            
            # Create metadata table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS daemon_metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create schema version
            cursor.execute('''
                INSERT OR IGNORE INTO daemon_metadata (key, value) 
                VALUES ('schema_version', '2.0')
            ''')
            
            conn.commit()
    
    def get_last_rec_id(self) -> int:
        """Get the last processed record ID"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT value FROM daemon_metadata WHERE key = 'last_rec_id'")
            row = cursor.fetchone()
            return int(row['value']) if row else 0
    
    def save_notifications(self, notifications: List[NotificationData]) -> int:
        """Save notifications to database"""
        if not notifications:
            return 0
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            saved_count = 0
            
            for notif in notifications:
                data = notif.to_dict()
                try:
                    cursor.execute('''
                        INSERT OR REPLACE INTO notifications 
                        (rec_id, app_identifier, delivered_time, title, subtitle, body, 
                         category, thread, priority_score, priority_level, priority_factors, 
                         is_read, is_archived, raw_data, updated_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (
                        data['rec_id'], data['app_identifier'], data['delivered_time'],
                        data['title'], data['subtitle'], data['body'],
                        data['category'], data['thread'],
                        data['priority_score'], data['priority_level'], data['priority_factors'],
                        data['is_read'], data['is_archived'], data['raw_data']
                    ))
                    saved_count += 1
                except sqlite3.Error as e:
                    logging.error(f"Error saving notification {notif.rec_id}: {e}")
            
            # Update last_rec_id
            if notifications:
                max_rec_id = max(n.rec_id for n in notifications)
                cursor.execute('''
                    INSERT OR REPLACE INTO daemon_metadata (key, value, updated_at)
                    VALUES ('last_rec_id', ?, CURRENT_TIMESTAMP)
                ''', (max_rec_id,))
                
                cursor.execute('''
                    INSERT OR REPLACE INTO daemon_metadata (key, value, updated_at)
                    VALUES ('last_update', ?, CURRENT_TIMESTAMP)
                ''', (datetime.now().isoformat(),))
            
            conn.commit()
            return saved_count
    
    def cleanup_old_notifications(self, days: int) -> int:
        """Remove notifications older than specified days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            cursor.execute('''
                DELETE FROM notifications 
                WHERE delivered_time < ? AND is_archived = FALSE
            ''', (cutoff_date,))
            
            deleted = cursor.rowcount
            if deleted > 0:
                conn.commit()
                cursor.execute("VACUUM")
            
            return deleted
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            stats = {}
            
            # Total notifications
            cursor.execute("SELECT COUNT(*) FROM notifications")
            stats['total_notifications'] = cursor.fetchone()[0]
            
            # By priority
            cursor.execute('''
                SELECT priority_level, COUNT(*) 
                FROM notifications 
                GROUP BY priority_level
            ''')
            stats['by_priority'] = dict(cursor.fetchall())
            
            # Top apps
            cursor.execute('''
                SELECT app_identifier, COUNT(*) as count 
                FROM notifications 
                GROUP BY app_identifier 
                ORDER BY count DESC 
                LIMIT 10
            ''')
            stats['top_apps'] = dict(cursor.fetchall())
            
            # Date range
            cursor.execute('''
                SELECT MIN(delivered_time), MAX(delivered_time) 
                FROM notifications
            ''')
            date_range = cursor.fetchone()
            stats['date_range'] = {
                'oldest': date_range[0],
                'newest': date_range[1]
            }
            
            # Metadata
            cursor.execute("SELECT key, value FROM daemon_metadata")
            stats['metadata'] = dict(cursor.fetchall())
            
            return stats


class NotificationExtractor:
    """Handles extraction of notifications from macOS database"""
    
    def __init__(self, macos_db_path: str = MACOS_DB_PATH):
        self.macos_db_path = macos_db_path
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def extract_notifications(self, last_rec_id: int, limit: int = 100) -> List[NotificationData]:
        """Extract new notifications from macOS database"""
        if not os.path.exists(self.macos_db_path):
            self.logger.warning(f"macOS notification database not found at {self.macos_db_path}")
            return []
        
        # Create temporary copy for safe access
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_db = os.path.join(temp_dir, "notifications.db")
            
            try:
                # Copy database files
                shutil.copy2(self.macos_db_path, temp_db)
                
                # Copy WAL file if exists
                wal_path = self.macos_db_path + "-wal"
                if os.path.exists(wal_path):
                    shutil.copy2(wal_path, temp_db + "-wal")
                
                # Extract notifications
                return self._query_notifications(temp_db, last_rec_id, limit)
                
            except Exception as e:
                self.logger.error(f"Error extracting notifications: {e}")
                return []
    
    def _query_notifications(self, db_path: str, last_rec_id: int, limit: int) -> List[NotificationData]:
        """Query notifications from database"""
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        notifications = []
        
        try:
            query = '''
            SELECT 
                rec.rec_id,
                app.identifier,
                datetime(rec.delivered_date + 978307200, 'unixepoch', 'localtime') as delivered_time,
                rec.data
            FROM record rec
            LEFT JOIN app ON rec.app_id = app.app_id
            WHERE rec.delivered_date IS NOT NULL
                AND rec.rec_id > ?
            ORDER BY rec.rec_id ASC
            LIMIT ?
            '''
            
            cursor.execute(query, (last_rec_id, limit))
            
            for row in cursor.fetchall():
                rec_id, app_identifier, delivered_time, data = row
                
                # Parse notification content
                content = self._parse_notification_content(data)
                
                notification = NotificationData(
                    rec_id=rec_id,
                    app_identifier=app_identifier or "Unknown",
                    delivered_time=delivered_time,
                    title=content.get("title", ""),
                    subtitle=content.get("subtitle", ""),
                    body=content.get("body", ""),
                    category=content.get("category", ""),
                    thread=content.get("thread", ""),
                    raw_data=data
                )
                
                notifications.append(notification)
                
        finally:
            conn.close()
        
        return notifications
    
    def _parse_notification_content(self, data: bytes) -> Dict[str, str]:
        """Parse notification content from binary plist data"""
        if not data:
            return {}
        
        result = {"title": "", "body": "", "subtitle": "", "category": "", "thread": ""}
        
        try:
            plist_data = plistlib.loads(data)
            
            # Handle different plist formats
            if 'req' in plist_data:
                req = plist_data['req']
                
                # Dictionary format (newer macOS versions)
                if isinstance(req, dict):
                    result["title"] = str(req.get('titl', '') or req.get('title', ''))
                    result["body"] = str(req.get('body', '') or req.get('mesg', ''))
                    result["subtitle"] = str(req.get('subt', '') or req.get('subtitle', ''))
                    result["category"] = str(req.get('cate', ''))
                    result["thread"] = str(req.get('thre', ''))
                    
                # Bytes format (older versions)
                elif isinstance(req, bytes):
                    try:
                        req_plist = plistlib.loads(req)
                        result["title"] = str(req_plist.get('titl', ''))
                        result["body"] = str(req_plist.get('body', ''))
                        result["subtitle"] = str(req_plist.get('subt', ''))
                        result["category"] = str(req_plist.get('cate', ''))
                        result["thread"] = str(req_plist.get('thre', ''))
                    except:
                        pass
                        
        except Exception as e:
            self.logger.debug(f"Error parsing notification: {e}")
        
        return result


class PriorityScorer:
    """Calculates priority scores for notifications"""
    
    # Priority keywords and their weights
    URGENT_KEYWORDS = {
        'urgent': 10, 'emergency': 10, 'critical': 10, 'important': 8,
        'asap': 8, 'immediately': 8, 'alert': 7, 'warning': 7,
        'deadline': 7, 'overdue': 7, 'security': 8, 'verify': 6,
        'confirm': 6, 'action required': 8, 'payment': 7, 'failed': 7
    }
    
    # App priority weights
    APP_PRIORITY = {
        'com.apple.mail': 5,
        'com.apple.MobileSMS': 6,
        'com.apple.iCal': 6,
        'com.apple.reminders': 7,
        'com.tinyspeck.slackmacgap': 5,
        'com.microsoft.teams': 5,
        'com.apple.security': 10,
        'com.apple.finance': 8
    }
    
    def calculate_priority(self, notification: NotificationData) -> Tuple[float, str, List[str]]:
        """Calculate priority score, level, and factors"""
        score = 0.0
        factors = []
        
        # Check content for urgent keywords
        content = f"{notification.title} {notification.subtitle} {notification.body}".lower()
        
        for keyword, weight in self.URGENT_KEYWORDS.items():
            if keyword in content:
                score += weight
                factors.append(f"Contains '{keyword}' (+{weight})")
        
        # App priority
        app_weight = self.APP_PRIORITY.get(notification.app_identifier, 0)
        if app_weight > 0:
            score += app_weight
            factors.append(f"App priority (+{app_weight})")
        
        # Time-based factors
        try:
            delivered = datetime.fromisoformat(notification.delivered_time)
            age_hours = (datetime.now() - delivered).total_seconds() / 3600
            
            if age_hours < 1:
                score += 3
                factors.append("Recent (< 1 hour) (+3)")
            elif age_hours < 4:
                score += 1
                factors.append("Recent (< 4 hours) (+1)")
        except:
            pass
        
        # Determine level
        if score >= 15:
            level = "CRITICAL"
        elif score >= 10:
            level = "HIGH"
        elif score >= 5:
            level = "MEDIUM"
        else:
            level = "LOW"
        
        return score, level, factors


class NotificationDaemon:
    """Main daemon class that orchestrates the notification monitoring"""
    
    def __init__(self, db_path: str, update_interval: int = DEFAULT_UPDATE_INTERVAL):
        self.db_path = db_path
        self.update_interval = update_interval
        self.running = False
        
        # Initialize components
        self.db_manager = DatabaseManager(db_path)
        self.extractor = NotificationExtractor()
        self.scorer = PriorityScorer()
        
        # Set up logging
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # PID file management
        self.pid_file = Path(db_path).parent / "notification_daemon.pid"
        self._write_pid_file()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
        self._cleanup_pid_file()
    
    def _write_pid_file(self):
        """Write current PID to file"""
        self.pid_file.write_text(str(os.getpid()))
    
    def _cleanup_pid_file(self):
        """Remove PID file"""
        if self.pid_file.exists():
            self.pid_file.unlink()
    
    def run(self):
        """Main daemon loop"""
        self.logger.info("Starting Notification Daemon v2.0")
        self.logger.info(f"Database: {self.db_path}")
        self.logger.info(f"Update interval: {self.update_interval}s")
        
        self.running = True
        update_count = 0
        
        while self.running:
            try:
                # Get last processed ID
                last_rec_id = self.db_manager.get_last_rec_id()
                
                # Extract new notifications
                notifications = self.extractor.extract_notifications(last_rec_id)
                
                # Calculate priorities
                for notif in notifications:
                    score, level, factors = self.scorer.calculate_priority(notif)
                    notif.priority_score = score
                    notif.priority_level = level
                    notif.priority_factors = factors
                
                # Save to database
                if notifications:
                    saved = self.db_manager.save_notifications(notifications)
                    self.logger.info(f"Saved {saved} new notifications")
                    
                    # Log high priority ones
                    high_priority = [n for n in notifications if n.priority_score >= 10]
                    for hp in high_priority:
                        self.logger.warning(
                            f"HIGH PRIORITY: {hp.app_identifier} - {hp.title} "
                            f"(Score: {hp.priority_score})"
                        )
                
                update_count += 1
                
                # Periodic cleanup (every 100 updates)
                if update_count % 100 == 0:
                    deleted = self.db_manager.cleanup_old_notifications(DEFAULT_CLEANUP_DAYS)
                    if deleted:
                        self.logger.info(f"Cleaned up {deleted} old notifications")
                
                # Status log (every minute)
                if update_count % 6 == 0:
                    stats = self.db_manager.get_statistics()
                    self.logger.info(
                        f"Status: {stats['total_notifications']} total, "
                        f"Priority: {stats.get('by_priority', {})}"
                    )
                
                # Sleep
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in daemon loop: {e}", exc_info=True)
                time.sleep(30)  # Wait longer on error
        
        self.logger.info("Daemon stopped")
        self._cleanup_pid_file()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get daemon statistics"""
        return self.db_manager.get_statistics()


def setup_logging(log_file: Optional[str] = None, log_level: str = "INFO"):
    """Configure logging"""
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Mac Notification Monitoring Daemon v2.0'
    )
    parser.add_argument(
        '--db', 
        default=DEFAULT_DB_NAME,
        help='Database file path'
    )
    parser.add_argument(
        '--interval', 
        type=int, 
        default=DEFAULT_UPDATE_INTERVAL,
        help='Update interval in seconds'
    )
    parser.add_argument(
        '--log-file',
        help='Log file path'
    )
    parser.add_argument(
        '--log-level',
        default='INFO',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    parser.add_argument(
        '--stats', 
        action='store_true',
        help='Show statistics and exit'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.log_file, args.log_level)
    
    # Create daemon
    daemon = NotificationDaemon(args.db, args.interval)
    
    if args.stats:
        # Show stats and exit
        stats = daemon.get_stats()
        print(json.dumps(stats, indent=2))
    else:
        # Run daemon
        daemon.run()


if __name__ == "__main__":
    main()
