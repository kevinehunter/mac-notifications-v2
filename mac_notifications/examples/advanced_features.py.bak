#!/usr/bin/env python3
"""
Advanced feature examples for Mac Notifications
"""

from datetime import datetime, timedelta
from mac_notifications.src.mcp_server.server import NotificationMCPServer


def example_smart_summaries():
    """Example: Generate smart summaries"""
    print("=== Smart Summaries ===")
    
    server = NotificationMCPServer()
    
    # Get hourly digest
    print("\n--- Hourly Digest ---")
    hourly = server.get_hourly_digest()
    if 'summary' in hourly:
        print(hourly['summary'])
        print(f"\nTotal notifications: {hourly['statistics']['total_notifications']}")
        print(f"Unread: {hourly['statistics']['unread_count']}")
    
    # Get executive brief
    print("\n--- Executive Brief ---")
    brief = server.get_executive_brief()
    if 'summary' in brief:
        print(brief['summary'])
    
    # Get custom summary
    print("\n--- Custom Summary (Last 12 Hours) ---")
    custom = server.get_smart_summary(
        time_range="12h",
        detail_level="detailed"
    )
    
    if 'recommendations' in custom:
        print("\nRecommendations:")
        for rec in custom['recommendations']:
            print(f"• {rec}")


def example_grouping():
    """Example: Group similar notifications"""
    print("=== Notification Grouping ===")
    
    server = NotificationMCPServer()
    
    # Group notifications from last 4 hours
    result = server.get_grouped_notifications(
        hours=4,
        time_window=30,  # 30 minute windows
        min_group_size=2  # Minimum 2 notifications to form a group
    )
    
    if 'groups' in result:
        print(f"Found {result['groups_found']} groups from {result['total_notifications']} notifications")
        print()
        
        # Show first few groups
        for key, group in list(result['groups'].items())[:5]:
            print(f"Group: {group['summary']}")
            print(f"  Count: {group['count']}")
            print(f"  Time span: {group['time_span']['start']} - {group['time_span']['end']}")
            print()


def example_batch_operations():
    """Example: Batch operations on notifications"""
    print("=== Batch Operations ===")
    
    server = NotificationMCPServer()
    
    # Example 1: Mark all low priority as read (dry run)
    print("\n--- Batch Mark as Read (Dry Run) ---")
    result = server.batch_mark_read(
        selection_type='priority',
        selection_value='LOW',
        dry_run=True
    )
    
    if result['success']:
        count = result.get('would_affect', result.get('affected_count', 0))
        print(f"Would mark {count} notifications as read")
    
    # Example 2: Archive old notifications (dry run)
    print("\n--- Batch Archive (Dry Run) ---")
    result = server.batch_archive(
        selection_type='older_than',
        selection_value='7d',
        dry_run=True
    )
    
    if result['success']:
        count = result.get('would_archive', result.get('affected_count', 0))
        print(f"Would archive {count} notifications older than 7 days")
    
    # Example 3: Update priority for specific app (dry run)
    print("\n--- Batch Update Priority (Dry Run) ---")
    result = server.batch_update_priority(
        selection_type='app',
        selection_value='com.apple.news',
        new_priority='LOW',
        dry_run=True
    )
    
    if result['success']:
        count = result.get('would_update', result.get('affected_count', 0))
        print(f"Would update priority for {count} News app notifications")


def example_analytics():
    """Example: Analytics and insights"""
    print("=== Analytics Dashboard ===")
    
    server = NotificationMCPServer()
    
    # Get key metrics
    print("\n--- Key Metrics (Last 7 Days) ---")
    metrics = server.get_notification_metrics(days=7)
    
    if 'error' not in metrics:
        print(f"Total notifications: {metrics['total_notifications']}")
        print(f"Average per hour: {metrics['avg_per_hour']}")
        print(f"Peak hour: {metrics['peak_hour']} ({metrics['peak_hour_count']} notifications)")
        print(f"Critical rate: {metrics['critical_rate']}%")
    
    # Get app analytics
    print("\n--- App Analytics ---")
    app_analytics = server.get_app_analytics(days=7)
    
    if 'app_distribution' in app_analytics:
        print("Top 5 apps by notification count:")
        for app in app_analytics['top_interrupters']:
            print(f"  {app['readable_name']}: {app['count']} ({app['percentage']}%)")
    
    # Get productivity report
    print("\n--- Productivity Report ---")
    productivity = server.get_productivity_report(days=7)
    
    if 'error' not in productivity:
        print(f"Focus score: {productivity['focus_score']}/10")
        print(f"Average focus time: {productivity['avg_focus_time']} minutes")
        print(f"Best focus hours: {', '.join(productivity['best_focus_hours'])}")
        print(f"Assessment: {productivity['focus_assessment']}")


def example_advanced_search():
    """Example: Advanced search patterns"""
    print("=== Advanced Search Examples ===")
    
    server = NotificationMCPServer()
    
    # Complex queries
    queries = [
        {
            "query": "critical financial notifications from last week",
            "description": "Combining priority, keyword, and time"
        },
        {
            "query": "messages from teams but not from bot since yesterday",
            "description": "App filter with exclusion and time"
        },
        {
            "query": "security camera detections group by hour",
            "description": "Search with grouping"
        },
        {
            "query": "notifications between 9am and 5pm from mail",
            "description": "Time range with app filter"
        }
    ]
    
    for example in queries:
        print(f"\nQuery: '{example['query']}'")
        print(f"({example['description']})")
        
        result = server.enhanced_search(example['query'], limit=5)
        
        if 'error' not in result:
            print(f"Found: {result['total_found']} notifications")
            if 'groups' in result:
                print(f"Grouped into: {len(result['groups'])} groups")


def example_full_workflow():
    """Example: Complete notification management workflow"""
    print("=== Complete Workflow Example ===")
    
    server = NotificationMCPServer()
    
    # Step 1: Check morning summary
    print("\n1. Morning Summary")
    summary = server.get_daily_digest()
    if 'critical_items' in summary and summary['critical_items']:
        print(f"   You have {len(summary['critical_items'])} critical items to review")
    
    # Step 2: Handle critical items
    print("\n2. Review Critical Items")
    critical = server.get_recent_notifications(
        limit=10,
        priority_filter='CRITICAL'
    )
    print(f"   Found {len(critical['notifications'])} critical notifications")
    
    # Step 3: Clean up old notifications
    print("\n3. Cleanup Old Notifications")
    
    # Archive read notifications older than 3 days
    archive_result = server.batch_archive(
        selection_type='older_than',
        selection_value='3d',
        dry_run=True
    )
    
    if archive_result['success']:
        print(f"   Can archive {archive_result.get('would_archive', 0)} old notifications")
    
    # Step 4: Check productivity
    print("\n4. Productivity Check")
    analytics = server.get_analytics_dashboard(days=1, output_format='json')
    
    if 'productivity' in analytics:
        score = analytics['productivity']['focus_score']
        print(f"   Today's focus score: {score}/10")
    
    # Step 5: Get recommendations
    print("\n5. Recommendations")
    if 'recommendations' in analytics:
        for rec in analytics['recommendations'][:3]:
            print(f"   • {rec['recommendation']}")
            print(f"     Action: {rec['action']}")


def main():
    """Run all advanced examples"""
    print("Mac Notifications - Advanced Feature Examples")
    print("=" * 50)
    
    examples = [
        example_smart_summaries,
        example_grouping,
        example_batch_operations,
        example_analytics,
        example_advanced_search,
        example_full_workflow
    ]
    
    for example in examples:
        try:
            example()
            print("\n" + "=" * 50 + "\n")
        except Exception as e:
            print(f"Error in {example.__name__}: {e}")
            print("\n" + "=" * 50 + "\n")


if __name__ == "__main__":
    main()
