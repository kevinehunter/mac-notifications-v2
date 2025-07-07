#!/usr/bin/env python3
"""
Feature #7: Notification Grouping & Threading
Groups related notifications to reduce clutter and improve overview
"""

import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
import json
from difflib import SequenceMatcher


class NotificationGrouper:
    """Groups related notifications intelligently"""
    
    def __init__(self):
        # Grouping configuration
        self.config = {
            'time_window_minutes': 15,  # Group notifications within 15 min windows
            'min_group_size': 2,        # Minimum notifications to form a group
            'similarity_threshold': 0.85, # How similar messages need to be (0-1)
            'group_by_app': True,       # Always separate by app
            'group_by_thread': True,    # Use thread info when available
        }
        
        # Patterns for extracting variable parts
        self.variable_patterns = [
            (r'\$[\d,]+\.?\d*', '[AMOUNT]'),  # Dollar amounts
            (r'\d{1,2}:\d{2}\s*[AP]M', '[TIME]'),  # Times
            (r'\d{1,2}/\d{1,2}/\d{2,4}', '[DATE]'),  # Dates
            (r'#\d+', '[NUMBER]'),  # Reference numbers
            (r'\b\d+\b', '[COUNT]'),  # Generic numbers
        ]
        
        # Security camera patterns
        self.camera_patterns = {
            'vehicle': re.compile(r'vehicle.*detected|car.*detected', re.I),
            'stranger': re.compile(r'stranger.*detected', re.I),
            'motion': re.compile(r'motion.*detected', re.I),
            'person': re.compile(r'person.*detected', re.I),
        }
        
    def normalize_message(self, text: str) -> str:
        """Normalize message by replacing variable parts"""
        if not text:
            return ""
            
        normalized = text
        for pattern, replacement in self.variable_patterns:
            normalized = re.sub(pattern, replacement, normalized)
        return normalized.strip()
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts (0-1)"""
        # Normalize both texts
        norm1 = self.normalize_message(text1)
        norm2 = self.normalize_message(text2)
        
        # Use SequenceMatcher for similarity
        return SequenceMatcher(None, norm1, norm2).ratio()
    
    def detect_camera_type(self, notification: Dict[str, Any]) -> Optional[str]:
        """Detect type of security camera notification"""
        text = f"{notification.get('title', '')} {notification.get('body', '')}"
        
        for detection_type, pattern in self.camera_patterns.items():
            if pattern.search(text):
                return detection_type
        return None
    
    def extract_camera_location(self, notification: Dict[str, Any]) -> Optional[str]:
        """Extract camera location from notification"""
        body = notification.get('body', '')
        
        # Common patterns: "Backyard:", "Garage AI #1:", etc.
        match = re.match(r'^([^:]+):', body)
        if match:
            return match.group(1).strip()
        return None
    
    def create_group_key(self, notification: Dict[str, Any]) -> str:
        """Create a grouping key for a notification"""
        parts = []
        
        # Always group by app
        app = notification.get('app_identifier', 'unknown')
        parts.append(app)
        
        # Special handling for security cameras
        if 'com.security.batterycam' in app:
            camera_type = self.detect_camera_type(notification)
            camera_location = self.extract_camera_location(notification)
            
            if camera_type:
                parts.append(f"camera_{camera_type}")
            if camera_location:
                parts.append(camera_location.lower().replace(' ', '_'))
        else:
            # Use thread for other apps
            thread = notification.get('thread', '')
            if thread:
                parts.append(thread)
            
            # Use normalized title for grouping similar notifications
            title = notification.get('title', '')
            if title:
                parts.append(self.normalize_message(title))
        
        return '|'.join(parts)
    
    def group_notifications(self, notifications: List[Dict[str, Any]], 
                          time_window_minutes: Optional[int] = None) -> Dict[str, Dict[str, Any]]:
        """Group notifications by similarity and time windows"""
        if time_window_minutes is None:
            time_window_minutes = self.config['time_window_minutes']
        
        # Sort by time
        sorted_notifs = sorted(notifications, 
                             key=lambda x: x.get('delivered_time', ''))
        
        groups = defaultdict(lambda: {
            'notifications': [],
            'count': 0,
            'first_time': None,
            'last_time': None,
            'group_type': None,
            'summary': None,
        })
        
        # Process each notification
        for notif in sorted_notifs:
            group_key = self.create_group_key(notif)
            group = groups[group_key]
            
            # Check time window
            notif_time = datetime.strptime(notif['delivered_time'], '%Y-%m-%d %H:%M:%S')
            
            if group['notifications']:
                last_time = datetime.strptime(group['last_time'], '%Y-%m-%d %H:%M:%S')
                time_diff = (notif_time - last_time).total_seconds() / 60
                
                # Create new group if outside time window
                if time_diff > time_window_minutes:
                    # Add timestamp to make unique key
                    group_key = f"{group_key}|{notif_time.strftime('%Y%m%d%H%M')}"
                    group = groups[group_key]
            
            # Add to group
            group['notifications'].append(notif)
            group['count'] += 1
            
            if not group['first_time']:
                group['first_time'] = notif['delivered_time']
            group['last_time'] = notif['delivered_time']
            
            # Determine group type
            if 'com.security.batterycam' in notif.get('app_identifier', ''):
                group['group_type'] = 'security_camera'
                group['camera_type'] = self.detect_camera_type(notif)
                group['camera_location'] = self.extract_camera_location(notif)
            elif 'mobilesms' in notif.get('app_identifier', ''):
                group['group_type'] = 'message'
            elif 'mail' in notif.get('app_identifier', ''):
                group['group_type'] = 'email'
            else:
                group['group_type'] = 'general'
        
        # Generate summaries and filter small groups
        final_groups = {}
        for key, group in groups.items():
            if group['count'] >= self.config['min_group_size']:
                group['summary'] = self.generate_group_summary(group)
                final_groups[key] = group
        
        return final_groups
    
    def generate_group_summary(self, group: Dict[str, Any]) -> str:
        """Generate intelligent summary for a notification group"""
        count = group['count']
        group_type = group['group_type']
        notifications = group['notifications']
        
        # Time range
        first_time = datetime.strptime(group['first_time'], '%Y-%m-%d %H:%M:%S')
        last_time = datetime.strptime(group['last_time'], '%Y-%m-%d %H:%M:%S')
        time_range = f"{first_time.strftime('%-I:%M %p')} - {last_time.strftime('%-I:%M %p')}"
        
        if group_type == 'security_camera':
            camera_location = group.get('camera_location', 'Camera')
            camera_type = group.get('camera_type', 'activity')
            
            # Check for priority items
            has_stranger = any('stranger' in n.get('body', '').lower() for n in notifications)
            
            if has_stranger:
                summary = f"{camera_location}: {count} detections including STRANGER ⚠️ ({time_range})"
            else:
                summary = f"{camera_location}: {count} {camera_type} detections ({time_range})"
                
        elif group_type == 'message':
            sender = notifications[0].get('title', 'Unknown')
            summary = f"{sender}: {count} messages"
            
        elif group_type == 'email':
            sender = notifications[0].get('title', 'Unknown')
            subject = notifications[0].get('subtitle', '')
            if subject:
                summary = f"{sender}: {subject} ({count} emails)"
            else:
                summary = f"{sender}: {count} emails"
        else:
            app = notifications[0].get('app_identifier', '').split('.')[-1]
            summary = f"{app}: {count} notifications ({time_range})"
        
        return summary
    
    def get_group_statistics(self, group: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed statistics for a notification group"""
        notifications = group['notifications']
        
        stats = {
            'total_count': group['count'],
            'time_span_minutes': 0,
            'priority_breakdown': defaultdict(int),
            'unique_titles': set(),
            'average_priority_score': 0,
        }
        
        # Calculate time span
        if group['first_time'] and group['last_time']:
            first = datetime.strptime(group['first_time'], '%Y-%m-%d %H:%M:%S')
            last = datetime.strptime(group['last_time'], '%Y-%m-%d %H:%M:%S')
            stats['time_span_minutes'] = int((last - first).total_seconds() / 60)
        
        # Analyze notifications
        total_score = 0
        for notif in notifications:
            # Priority breakdown
            priority = notif.get('priority_level', 'UNKNOWN')
            stats['priority_breakdown'][priority] += 1
            
            # Unique titles
            title = notif.get('title', '')
            if title:
                stats['unique_titles'].add(title)
            
            # Average score
            score = notif.get('priority_score', 0)
            total_score += score
        
        if notifications:
            stats['average_priority_score'] = round(total_score / len(notifications), 2)
        
        stats['priority_breakdown'] = dict(stats['priority_breakdown'])
        stats['unique_titles'] = list(stats['unique_titles'])
        
        return stats
    
    def collapse_groups(self, groups: Dict[str, Dict[str, Any]], 
                       max_expanded: int = 5) -> Dict[str, Dict[str, Any]]:
        """Determine which groups should be collapsed vs expanded"""
        # Sort groups by importance (priority score, recency, size)
        sorted_groups = sorted(groups.items(), 
                             key=lambda x: (
                                 -max(n.get('priority_score', 0) for n in x[1]['notifications']),
                                 x[1]['last_time'],
                                 -x[1]['count']
                             ))
        
        # Mark groups for collapse/expand
        for i, (key, group) in enumerate(sorted_groups):
            group['collapsed'] = i >= max_expanded
            
        return dict(sorted_groups)


# Standalone functions for easy integration

def group_notifications(notifications: List[Dict[str, Any]], 
                       time_window_minutes: int = 15,
                       min_group_size: int = 2) -> Dict[str, Dict[str, Any]]:
    """Group notifications with sensible defaults"""
    grouper = NotificationGrouper()
    grouper.config['time_window_minutes'] = time_window_minutes
    grouper.config['min_group_size'] = min_group_size
    
    return grouper.group_notifications(notifications, time_window_minutes)


def generate_grouping_report(groups: Dict[str, Dict[str, Any]]) -> str:
    """Generate a formatted report of notification groups"""
    if not groups:
        return "No notification groups found."
    
    grouper = NotificationGrouper()
    report_lines = [f"Found {len(groups)} notification groups:\n"]
    
    for key, group in groups.items():
        stats = grouper.get_group_statistics(group)
        
        report_lines.append(f"📦 {group['summary']}")
        report_lines.append(f"   Total: {stats['total_count']} notifications")
        report_lines.append(f"   Time span: {stats['time_span_minutes']} minutes")
        report_lines.append(f"   Avg priority: {stats['average_priority_score']}")
        
        if stats['priority_breakdown']:
            priority_str = ", ".join(f"{k}: {v}" for k, v in stats['priority_breakdown'].items())
            report_lines.append(f"   Priority: {priority_str}")
        
        report_lines.append("")
    
    return "\n".join(report_lines)