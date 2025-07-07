#!/usr/bin/env python3
"""
Main MCP Server implementation for Mac Notifications
"""

import json
import logging
import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
import subprocess
import sys
from pathlib import Path

# MCP imports
from mcp.server import Server
import mcp.server.stdio
import mcp.types as types

# Import configuration
from ..config.settings import Settings

# Import database models and repositories
from ..database.models import Notification
from ..database.connection import get_db_connection
from ..database.repositories import NotificationRepository, DaemonMetadataRepository

# Import features
from ..features.templates import NotificationTemplates
from ..features.priority_scoring import PriorityScorer
from ..features.enhanced_search import EnhancedSearch
from ..features.grouping import NotificationGrouper
from ..features.batch_actions import BatchActions
from ..features.smart_summaries import SmartSummaryGenerator
from ..features.analytics import NotificationAnalytics

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NotificationMCPServer:
    """MCP Server for accessing notifications from the daemon database"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize the MCP server
        
        Args:
            db_path: Path to the notifications database. If None, uses settings default.
        """
        self.settings = Settings.load_from_env()
        self.db_path = db_path or str(self.settings.DEFAULT_DB_PATH)
        self.daemon_process = None
        
        # Initialize database connection and repositories
        self.db_connection = get_db_connection(self.db_path)
        self.notification_repo = NotificationRepository(self.db_connection)
        self.metadata_repo = DaemonMetadataRepository(self.db_connection)
        
        # Initialize feature components
        self.templates = NotificationTemplates()
        self.priority_scorer = PriorityScorer()
        self.search_engine = EnhancedSearch()
        self.grouper = NotificationGrouper()
        self.batch_actions = BatchActions(self.db_path)
        self.summary_generator = SmartSummaryGenerator(self.db_path)
        self.analytics = NotificationAnalytics(self.db_path)
        
    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def _check_daemon_status(self) -> Dict[str, Any]:
        """Check if the daemon database exists and get its status"""
        if not os.path.exists(self.db_path):
            return {
                "database_exists": False,
                "daemon_running": False,
                "message": "Notification database not found. Start the daemon first."
            }
        
        try:
            # Use metadata repository
            last_update_str = self.metadata_repo.get('last_update')
            
            if not last_update_str:
                return {
                    "database_exists": True,
                    "daemon_running": False,
                    "message": "Database exists but no updates recorded"
                }
            
            last_update = datetime.fromisoformat(last_update_str)
            time_since_update = (datetime.now() - last_update).total_seconds()
            
            # Consider daemon running if updated within configured interval
            daemon_running = time_since_update < self.settings.DAEMON_UPDATE_INTERVAL
            
            return {
                "database_exists": True,
                "daemon_running": daemon_running,
                "last_update": last_update_str,
                "seconds_since_update": int(time_since_update),
                "message": "Daemon is running" if daemon_running else "Daemon appears to be stopped"
            }
            
        except Exception as e:
            return {
                "database_exists": True,
                "daemon_running": False,
                "error": str(e),
                "message": "Error checking daemon status"
            }
    
    def get_recent_notifications(self, limit: int = 10, priority_filter: Optional[str] = None, 
                               format_type: str = 'terminal', use_templates: bool = True,
                               sort_by: str = 'priority') -> Dict[str, Any]:
        """Get recent notifications from the database with optional priority filtering and formatting"""
        status = self._check_daemon_status()
        
        if not status["database_exists"]:
            return {
                "error": "Database not found",
                "message": "Please start the notification daemon first",
                "daemon_status": status
            }
        
        try:
            # Get notifications using repository
            if priority_filter == 'important':
                notifications = self.notification_repo.get_important(limit)
            elif priority_filter:
                notifications = self.notification_repo.get_by_priority(priority_filter, limit)
            else:
                notifications = self.notification_repo.get_recent(limit)
            
            # Convert to MCP format
            mcp_notifications = []
            formatted_notifications = []
            
            for notification in notifications:
                mcp_notif = notification.to_mcp_format()
                mcp_notifications.append(mcp_notif)
                
                # Format using templates if requested
                if use_templates:
                    template_output = self.templates.format_notification(
                        mcp_notif, 
                        use_color=False,  # No color in JSON responses
                        format_type=format_type
                    )
                    formatted_notifications.append(template_output)
            
            # Get statistics
            stats = self.notification_repo.get_statistics()
            
            result = {
                "total_stored": stats.get('total', 0),
                "showing": len(mcp_notifications),
                "notifications": mcp_notifications,
                "daemon_status": status
            }
            
            if formatted_notifications:
                result["formatted_output"] = "\n\n".join(formatted_notifications)
            
            if 'by_priority' in stats:
                result["priority_breakdown"] = stats['by_priority']
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting notifications: {e}")
            return {
                "error": str(e),
                "daemon_status": status
            }
    
    def get_priority_notifications(self, format_type: str = 'terminal') -> Dict[str, Any]:
        """Get high priority notifications with formatting"""
        return self.get_recent_notifications(limit=20, priority_filter='important', 
                                           format_type=format_type, use_templates=True)
    
    def get_formatted_notifications(self, limit: int = 10, priority_filter: str = None,
                                  format_type: str = 'terminal', sort_by: str = 'priority') -> str:
        """Get notifications formatted as HTML, Markdown, or Terminal output"""
        result = self.get_recent_notifications(limit, priority_filter, format_type, use_templates=True, sort_by=sort_by)
        
        if 'error' in result:
            return f"Error: {result['error']}"
        
        notifications = result.get('notifications', [])
        
        if format_type == 'html':
            return self.templates.format_notification_list(notifications, format_type='html')
        elif format_type == 'markdown':
            return self.templates.format_notification_list(notifications, format_type='markdown')
        else:
            return self.templates.format_notification_list(notifications, format_type='terminal', use_color=True)
    
    def search_notifications(self, keyword: str = None, app: str = None) -> Dict[str, Any]:
        """Search notifications by keyword or app"""
        status = self._check_daemon_status()
        
        if not status["database_exists"]:
            return {
                "error": "Database not found",
                "message": "Please start the notification daemon first",
                "daemon_status": status
            }
        
        try:
            # Use repository for search
            notifications = self.notification_repo.search(keyword, app)
            
            # Convert to MCP format
            mcp_notifications = [n.to_mcp_format() for n in notifications]
            
            result = {
                "total_found": len(mcp_notifications),
                "notifications": mcp_notifications,
                "daemon_status": status
            }
            
            if keyword:
                result["search_term"] = keyword
            if app:
                result["app_filter"] = app
                
            return result
            
        except Exception as e:
            logger.error(f"Error searching notifications: {e}")
            return {
                "error": str(e),
                "daemon_status": status
            }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get notification statistics including priority breakdown"""
        status = self._check_daemon_status()
        
        if not status["database_exists"]:
            return {
                "error": "Database not found",
                "message": "Please start the notification daemon first",
                "daemon_status": status
            }
        
        try:
            # Get statistics from repository
            stats = self.notification_repo.get_statistics()
            
            # Get metadata
            metadata = self.metadata_repo.get_all()
            
            result = {
                "total": stats.get('total', 0),
                "total_apps": len(stats.get('by_app', {})),
                "by_app": stats.get('by_app', {}),
                "date_range": stats.get('date_range', {}),
                "last_update": metadata.get("last_update", "Unknown"),
                "last_rec_id": metadata.get("last_rec_id", "Unknown"),
                "daemon_status": status
            }
            
            # Add priority breakdown if available
            if 'by_priority' in stats:
                result["priority_breakdown"] = stats['by_priority']
            
            # Get top priority notifications using repository
            high_priority = self.notification_repo.get_by_priority('HIGH', limit=10)
            critical = self.notification_repo.get_by_priority('CRITICAL', limit=10)
            
            top_priority = []
            for notif in (critical + high_priority)[:10]:
                top_priority.append({
                    'app': notif.app_identifier,
                    'title': notif.title or 'No title',
                    'score': notif.priority_score,
                    'level': notif.priority_level,
                    'time': notif.delivered_time
                })
            
            if top_priority:
                result["top_priority_notifications"] = top_priority
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {
                "error": str(e),
                "daemon_status": status
            }
    
    def start_daemon(self) -> Dict[str, Any]:
        """Start the notification daemon as a subprocess"""
        try:
            # Check if daemon is already running
            status = self._check_daemon_status()
            if status.get("daemon_running"):
                return {
                    "success": True,
                    "message": "Daemon is already running",
                    "status": status
                }
            
            # Kill any existing daemon processes first
            logger.info("Checking for existing daemon processes...")
            self._kill_existing_daemons()
            
            # Remove any stale PID file
            pid_file = os.path.join(os.path.dirname(self.db_path), "notification_daemon.pid")
            if os.path.exists(pid_file):
                os.remove(pid_file)
                logger.info("Removed stale PID file")
            
            # Start the daemon with the new module
            daemon_path = Path(__file__).parent.parent / "daemon" / "notification_daemon.py"
            
            self.daemon_process = subprocess.Popen(
                [sys.executable, str(daemon_path), "--db", self.db_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait a moment for it to start
            import time
            time.sleep(2)
            
            # Check if it's running
            if self.daemon_process.poll() is None:
                return {
                    "success": True,
                    "message": "Daemon started successfully",
                    "pid": self.daemon_process.pid
                }
            else:
                stdout, stderr = self.daemon_process.communicate()
                return {
                    "success": False,
                    "message": "Daemon failed to start",
                    "stdout": stdout.decode(),
                    "stderr": stderr.decode()
                }
                
        except Exception as e:
            return {
                "success": False,
                "message": f"Error starting daemon: {str(e)}"
            }
    
    def stop_daemon(self) -> Dict[str, Any]:
        """Stop the notification daemon"""
        try:
            if self.daemon_process and self.daemon_process.poll() is None:
                self.daemon_process.terminate()
                self.daemon_process.wait(timeout=5)
                return {
                    "success": True,
                    "message": "Daemon stopped"
                }
            else:
                return {
                    "success": False,
                    "message": "Daemon is not running"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"Error stopping daemon: {str(e)}"
            }
    
    def _kill_existing_daemons(self):
        """Kill any existing daemon processes"""
        try:
            import psutil
            killed_count = 0
            daemon_names = ['notification_daemon.py', 'notification_daemon_v2.py']
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = proc.info.get('cmdline')
                    if cmdline and any(daemon_name in ' '.join(cmdline) for daemon_name in daemon_names):
                        pid = proc.info['pid']
                        logger.info(f"Found existing daemon process PID {pid}, terminating...")
                        proc.terminate()
                        try:
                            proc.wait(timeout=5)
                        except psutil.TimeoutExpired:
                            logger.warning(f"Force killing PID {pid}")
                            proc.kill()
                            proc.wait()
                        killed_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            if killed_count > 0:
                logger.info(f"Killed {killed_count} existing daemon process(es)")
                # Wait for database lock to release
                import time
                time.sleep(2)
                
        except ImportError:
            logger.warning("psutil not available, cannot check for existing daemons")
            # Try to kill using the stored process if available
            if self.daemon_process:
                try:
                    self.daemon_process.terminate()
                    self.daemon_process.wait(timeout=5)
                except:
                    pass
    
    def _get_notification_ids_for_batch(self, selection_type: str, selection_value: Any) -> List[int]:
        """Get notification IDs based on selection criteria"""
        if selection_type == "ids":
            # Direct list of IDs
            return selection_value if isinstance(selection_value, list) else [selection_value]
        
        elif selection_type == "app":
            # Select by app identifier
            return self.batch_actions.select_by_app(selection_value)
        
        elif selection_type == "app_pattern":
            # Select by app pattern
            return self.batch_actions.select_by_app(selection_value, pattern=True)
        
        elif selection_type == "priority":
            # Select by priority level
            return self.batch_actions.select_by_priority(selection_value)
        
        elif selection_type == "older_than":
            # Parse time string (e.g., "7d", "24h")
            import re
            match = re.match(r'(\d+)([hdwm])', selection_value.lower())
            if match:
                value, unit = match.groups()
                value = int(value)
                if unit == 'h':
                    days = value / 24
                elif unit == 'd':
                    days = value
                elif unit == 'w':
                    days = value * 7
                elif unit == 'm':
                    days = value * 30
                else:
                    days = 7  # Default
                return self.batch_actions.select_by_time_range(older_than_days=int(days))
        
        elif selection_type == "search":
            # Use enhanced search to get IDs
            with self._get_connection() as conn:
                search_results = self.search_engine.search(selection_value, conn, limit=1000)
                return [n.get('rec_id', n.get('id')) for n in search_results.get('notifications', [])]
        
        else:
            raise ValueError(f"Unknown selection type: {selection_type}")
    
    # Placeholder methods for features to be migrated
    def enhanced_search(self, query: str, limit: int = 50, format_type: str = 'terminal') -> Dict[str, Any]:
        """Execute enhanced natural language search"""
        status = self._check_daemon_status()
        
        if not status["database_exists"]:
            return {
                "error": "Database not found",
                "message": "Please start the notification daemon first",
                "daemon_status": status
            }
        
        try:
            # Use the enhanced search engine
            with self._get_connection() as conn:
                result = self.search_engine.search(query, conn, limit)
            
            # Add daemon status
            result["daemon_status"] = status
            
            # Format output if requested
            if format_type in ["terminal", "html", "markdown"] and result.get("notifications"):
                formatted_output = self.templates.format_notification_list(
                    result["notifications"], 
                    format_type=format_type,
                    use_color=(format_type == "terminal")
                )
                result["formatted_output"] = formatted_output
            
            return result
            
        except Exception as e:
            logger.error(f"Error in enhanced search: {e}")
            return {
                "error": str(e),
                "daemon_status": status
            }
    
    def get_grouped_notifications(self, hours: int = 4, time_window: int = 30, 
                                 min_group_size: int = 2, format_type: str = 'terminal') -> Dict[str, Any]:
        """Get notifications grouped by similarity"""
        status = self._check_daemon_status()
        
        if not status["database_exists"]:
            return {
                "error": "Database not found",
                "message": "Please start the notification daemon first",
                "daemon_status": status
            }
        
        try:
            # Get recent notifications
            cutoff_time = datetime.now() - timedelta(hours=hours)
            notifications = self.notification_repo.get_since(cutoff_time.strftime('%Y-%m-%d %H:%M:%S'))
            
            # Convert to dict format for grouper
            notif_dicts = [n.to_mcp_format() for n in notifications]
            
            # Configure grouper
            self.grouper.config['time_window_minutes'] = time_window
            self.grouper.config['min_group_size'] = min_group_size
            
            # Group notifications
            groups = self.grouper.group_notifications(notif_dicts, time_window)
            
            result = {
                "total_notifications": len(notif_dicts),
                "groups_found": len(groups),
                "groups": groups,
                "daemon_status": status
            }
            
            # Format output if requested
            if format_type in ["terminal", "html", "markdown"]:
                from ..features.grouping import generate_grouping_report
                formatted_output = generate_grouping_report(groups)
                result["formatted_output"] = formatted_output
            
            return result
            
        except Exception as e:
            logger.error(f"Error grouping notifications: {e}")
            return {
                "error": str(e),
                "daemon_status": status
            }
    
    def batch_mark_read(self, selection_type: str, selection_value: Any, dry_run: bool = False) -> Dict[str, Any]:
        """Mark notifications as read in batch"""
        try:
            # Get notification IDs based on selection
            notification_ids = self._get_notification_ids_for_batch(selection_type, selection_value)
            
            if not notification_ids:
                return {
                    "success": True,
                    "affected_count": 0,
                    "message": "No notifications matched the selection criteria"
                }
            
            # Use batch actions
            result = self.batch_actions.mark_as_read(notification_ids, dry_run)
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error in batch mark read: {e}")
            return {
                "success": False,
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }
    
    def batch_mark_unread(self, selection_type: str, selection_value: Any, dry_run: bool = False) -> Dict[str, Any]:
        """Mark notifications as unread in batch"""
        try:
            notification_ids = self._get_notification_ids_for_batch(selection_type, selection_value)
            if not notification_ids:
                return {
                    "success": True,
                    "affected_count": 0,
                    "message": "No notifications matched the selection criteria"
                }
            
            result = self.batch_actions.mark_as_unread(notification_ids, dry_run)
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error in batch mark unread: {e}")
            return {
                "success": False,
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }
    
    def batch_archive(self, selection_type: str, selection_value: Any, dry_run: bool = False) -> Dict[str, Any]:
        """Archive notifications in batch"""
        try:
            notification_ids = self._get_notification_ids_for_batch(selection_type, selection_value)
            if not notification_ids:
                return {
                    "success": True,
                    "affected_count": 0,
                    "message": "No notifications matched the selection criteria"
                }
            
            result = self.batch_actions.archive_notifications(notification_ids, dry_run)
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error in batch archive: {e}")
            return {
                "success": False,
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }
    
    def batch_delete(self, selection_type: str, selection_value: Any, confirm: bool = False, dry_run: bool = False) -> Dict[str, Any]:
        """Delete notifications in batch"""
        if not confirm and not dry_run:
            return {
                "success": False,
                "error": "Deletion requires confirmation. Set confirm=True to proceed.",
                "daemon_status": self._check_daemon_status()
            }
        
        try:
            notification_ids = self._get_notification_ids_for_batch(selection_type, selection_value)
            if not notification_ids:
                return {
                    "success": True,
                    "deleted_count": 0,
                    "message": "No notifications matched the selection criteria"
                }
            
            result = self.batch_actions.delete_notifications(notification_ids, dry_run)
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error in batch delete: {e}")
            return {
                "success": False,
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }
    
    def batch_update_priority(self, selection_type: str, selection_value: Any, new_priority: str, dry_run: bool = False) -> Dict[str, Any]:
        """Update priority for notifications in batch"""
        # Convert priority string to number
        priority_map = {"CRITICAL": 1, "HIGH": 2, "MEDIUM": 3, "LOW": 4}
        priority_num = priority_map.get(new_priority.upper())
        
        if not priority_num:
            return {
                "success": False,
                "error": f"Invalid priority level: {new_priority}. Must be CRITICAL, HIGH, MEDIUM, or LOW.",
                "daemon_status": self._check_daemon_status()
            }
        
        try:
            notification_ids = self._get_notification_ids_for_batch(selection_type, selection_value)
            if not notification_ids:
                return {
                    "success": True,
                    "affected_count": 0,
                    "message": "No notifications matched the selection criteria"
                }
            
            result = self.batch_actions.update_priority(notification_ids, priority_num, dry_run)
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error in batch update priority: {e}")
            return {
                "success": False,
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }
    
    def get_smart_summary(self, time_range: str = "1h", detail_level: str = "standard", 
                         focus_apps: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate a smart summary of notifications"""
        try:
            result = self.summary_generator.generate_summary(
                time_range=time_range,
                detail_level=detail_level,
                focus_apps=focus_apps
            )
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error generating smart summary: {e}")
            return {
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }
    
    def get_hourly_digest(self) -> Dict[str, Any]:
        """Get a quick hourly digest"""
        return self.get_smart_summary(time_range="1h", detail_level="standard")
    
    def get_daily_digest(self) -> Dict[str, Any]:
        """Get comprehensive daily digest"""
        return self.get_smart_summary(time_range="24h", detail_level="detailed")
    
    def get_executive_brief(self) -> Dict[str, Any]:
        """Get ultra-brief executive summary"""
        return self.get_smart_summary(time_range="4h", detail_level="brief")
    
    def get_analytics_dashboard(self, days: int = 7, output_format: str = "html") -> Dict[str, Any]:
        """Generate analytics dashboard"""
        try:
            result = self.analytics.get_analytics_dashboard(days, output_format)
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error generating analytics dashboard: {e}")
            return {
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }
    
    def get_notification_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get key notification metrics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            result = self.analytics.get_key_metrics(start_date, end_date)
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error getting notification metrics: {e}")
            return {
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }
    
    def get_hourly_heatmap(self, days: int = 7) -> Dict[str, Any]:
        """Get hourly notification heatmap data"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            result = self.analytics.get_hourly_pattern(start_date, end_date)
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error getting hourly heatmap: {e}")
            return {
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }
    
    def get_app_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get per-app analytics"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            result = self.analytics.get_app_analytics(start_date, end_date)
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error getting app analytics: {e}")
            return {
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }
    
    def get_productivity_report(self, days: int = 7) -> Dict[str, Any]:
        """Get productivity metrics and focus time analysis"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            result = self.analytics.get_productivity_metrics(start_date, end_date)
            result["daemon_status"] = self._check_daemon_status()
            return result
            
        except Exception as e:
            logger.error(f"Error getting productivity report: {e}")
            return {
                "error": str(e),
                "daemon_status": self._check_daemon_status()
            }


# Create global server instance
notification_server = NotificationMCPServer()
server = Server("notification-mcp-server")


async def main():
    """Main function to run the MCP server"""
    logger.info(f"Starting Notification MCP Server v{notification_server.settings.MCP_SERVER_VERSION}...")
    logger.info(f"Database path: {notification_server.db_path}")
    
    # Check daemon status
    status = notification_server._check_daemon_status()
    logger.info(f"Daemon status: {status['message']}")
    
    # Import and register all handlers
    from .handlers import register_all_handlers
    register_all_handlers(server, notification_server)
    
    # Run the MCP server
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
