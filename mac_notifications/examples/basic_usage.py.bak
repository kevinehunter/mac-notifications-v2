#!/usr/bin/env python3
"""
Basic usage examples for the Mac Notifications system
"""

from mac_notifications.src.mcp_server.server import NotificationMCPServer


def example_get_recent_notifications():
    """Example: Get recent notifications"""
    print("=== Getting Recent Notifications ===")
    
    # Create server instance
    server = NotificationMCPServer()
    
    # Get last 10 notifications
    result = server.get_recent_notifications(limit=10)
    
    print(f"Total notifications stored: {result['total_stored']}")
    print(f"Showing: {result['showing']}")
    print()
    
    # Display each notification
    for notif in result['notifications']:
        print(f"[{notif['priority_level']}] {notif['app_identifier'].split('.')[-1]}")
        print(f"  {notif.get('title', 'No title')}")
        if notif.get('body'):
            print(f"  {notif['body'][:100]}...")
        print(f"  Time: {notif['delivered_time']}")
        print()


def example_get_priority_notifications():
    """Example: Get only high priority notifications"""
    print("=== Getting High Priority Notifications ===")
    
    server = NotificationMCPServer()
    
    # Get critical and high priority notifications
    result = server.get_priority_notifications()
    
    print(f"Found {len(result['notifications'])} high priority items:")
    print()
    
    for notif in result['notifications']:
        marker = "🚨" if notif['priority_level'] == 'CRITICAL' else "⚠️"
        print(f"{marker} [{notif['priority_score']}] {notif.get('title', 'No title')}")


def example_search_notifications():
    """Example: Search notifications"""
    print("=== Searching Notifications ===")
    
    server = NotificationMCPServer()
    
    # Search examples
    search_queries = [
        "urgent",
        "from messages",
        "critical notifications from today",
        "security alerts but not vehicles"
    ]
    
    for query in search_queries:
        print(f"\nSearching for: '{query}'")
        result = server.enhanced_search(query, limit=5)
        
        if 'error' in result:
            print(f"  Error: {result['error']}")
        else:
            print(f"  Found {result['total_found']} matches")
            print(f"  Parsed as: {result['parsed_params']}")


def example_get_statistics():
    """Example: Get notification statistics"""
    print("=== Notification Statistics ===")
    
    server = NotificationMCPServer()
    stats = server.get_statistics()
    
    print(f"Total notifications: {stats['total']}")
    print(f"Total apps: {stats['total_apps']}")
    print()
    
    print("Top apps:")
    for app, count in list(stats['by_app'].items())[:5]:
        app_name = app.split('.')[-1]
        print(f"  {app_name}: {count}")
    
    if 'priority_breakdown' in stats:
        print("\nPriority breakdown:")
        for level, count in stats['priority_breakdown'].items():
            print(f"  {level}: {count}")


def example_formatted_output():
    """Example: Get formatted notification output"""
    print("=== Formatted Output Examples ===")
    
    server = NotificationMCPServer()
    
    # Terminal format
    print("\n--- Terminal Format ---")
    terminal_output = server.get_formatted_notifications(
        limit=3, 
        format_type='terminal'
    )
    print(terminal_output)
    
    # Markdown format
    print("\n--- Markdown Format ---")
    markdown_output = server.get_formatted_notifications(
        limit=3,
        format_type='markdown'
    )
    print(markdown_output)


def main():
    """Run all examples"""
    print("Mac Notifications - Basic Usage Examples")
    print("=" * 50)
    
    examples = [
        example_get_recent_notifications,
        example_get_priority_notifications,
        example_search_notifications,
        example_get_statistics,
        example_formatted_output
    ]
    
    for example in examples:
        try:
            example()
            print("\n" + "-" * 50 + "\n")
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            print("\n" + "-" * 50 + "\n")


if __name__ == "__main__":
    main()
