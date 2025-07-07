"""
Features Module

This module contains all the advanced features for the notification system.
"""

from .priority_scoring import PriorityScorer, calculate_priority_score
from .templates import NotificationTemplateEngine, format_notification
from .enhanced_search import EnhancedSearch, search_notifications, parse_search_query
from .grouping import NotificationGrouper, group_notifications, generate_grouping_report
from .batch_actions import BatchActions
from .smart_summaries import (
    SmartSummaryGenerator,
    get_hourly_digest,
    get_daily_digest,
    get_executive_brief
)
from .analytics import (
    NotificationAnalytics,
    generate_analytics_dashboard,
    get_notification_metrics,
    get_productivity_report
)

__all__ = [
    # Priority Scoring
    'PriorityScorer',
    'calculate_priority_score',
    
    # Templates
    'NotificationTemplateEngine',
    'format_notification',
    
    # Enhanced Search
    'EnhancedSearch',
    'search_notifications',
    'parse_search_query',
    
    # Grouping
    'NotificationGrouper',
    'group_notifications',
    'generate_grouping_report',
    
    # Batch Actions
    'BatchActions',
    
    # Smart Summaries
    'SmartSummaryGenerator',
    'get_hourly_digest',
    'get_daily_digest',
    'get_executive_brief',
    
    # Analytics
    'NotificationAnalytics',
    'generate_analytics_dashboard',
    'get_notification_metrics',
    'get_productivity_report',
]