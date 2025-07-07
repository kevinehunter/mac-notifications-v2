#!/usr/bin/env python3
"""
Test script to verify import paths are working correctly
"""

import sys
from pathlib import Path

# Add the mac_notifications directory to path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")

try:
    # Test config imports
    from src.config.settings import Settings
    print("✅ Config imports working")
except Exception as e:
    print(f"❌ Config imports failed: {e}")

try:
    # Test database imports
    from src.database.models import Notification, DaemonMetadata
    from src.database.connection import DatabaseConnection, get_db_connection
    from src.database.repositories import NotificationRepository, DaemonMetadataRepository
    from src.database.migrations import MigrationManager
    print("✅ Database imports working")
except Exception as e:
    print(f"❌ Database imports failed: {e}")

try:
    # Test feature imports
    from src.features.priority_scoring import PriorityScorer
    from src.features.templates import NotificationTemplates
    from src.features.enhanced_search import EnhancedSearch
    print("✅ Feature imports working")
except Exception as e:
    print(f"❌ Feature imports failed: {e}")

try:
    # Test daemon imports
    from src.daemon.notification_daemon import NotificationDaemon
    from src.daemon.daemon_manager import DaemonManager
    print("✅ Daemon imports working")
except Exception as e:
    print(f"❌ Daemon imports failed: {e}")

try:
    # Test MCP server imports
    from src.mcp_server.server import NotificationMCPServer, server
    print("✅ MCP server imports working")
except Exception as e:
    print(f"❌ MCP server imports failed: {e}")

print("\nAll import tests complete!")
