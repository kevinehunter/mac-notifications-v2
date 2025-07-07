"""
MCP Server for Mac Notifications

This module provides the Model Context Protocol server for accessing
and managing Mac notifications stored in the SQLite database.
"""

from .server import NotificationMCPServer, server, main

__all__ = ['NotificationMCPServer', 'server', 'main']