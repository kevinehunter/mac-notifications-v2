"""
MCP Server Handlers

Async handler functions for all MCP server tools.
"""

import mcp.types as types
from .core import CORE_HANDLERS
from .search import SEARCH_HANDLERS
from .batch import BATCH_HANDLERS
from .analytics import ANALYTICS_HANDLERS
from .summary import SUMMARY_HANDLERS


# Combine all handlers
ALL_HANDLERS = {
    **CORE_HANDLERS,
    **SEARCH_HANDLERS,
    **BATCH_HANDLERS,
    **ANALYTICS_HANDLERS,
    **SUMMARY_HANDLERS
}


def register_all_handlers(server, notification_server):
    """Register all handlers with the MCP server
    
    Args:
        server: The MCP server instance
        notification_server: The NotificationMCPServer instance
    """
    
    @server.call_tool()
    async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
        """Handle tool calls"""
        if name in ALL_HANDLERS:
            handler = ALL_HANDLERS[name]
            return await handler(notification_server, arguments)
        else:
            return [types.TextContent(type="text", text=f"❌ Unknown tool: {name}")]
    
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """List available tools"""
        from ..tools import TOOL_DEFINITIONS
        return TOOL_DEFINITIONS
