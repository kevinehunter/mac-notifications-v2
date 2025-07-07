"""
Database module for the notification system

Provides models, connection management, repositories, and migrations.
"""

from .models import Notification, DaemonMetadata
from .connection import DatabaseConnection, get_db_connection
from .repositories import NotificationRepository, DaemonMetadataRepository
from .migrations import MigrationManager, run_migrations

__all__ = [
    'Notification',
    'DaemonMetadata',
    'DatabaseConnection',
    'get_db_connection',
    'NotificationRepository', 
    'DaemonMetadataRepository',
    'MigrationManager',
    'run_migrations',
]