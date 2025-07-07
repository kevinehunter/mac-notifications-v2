#!/usr/bin/env python3
"""
Smart Summaries & Digests Module

Provides AI-powered summaries of notifications to help users quickly 
understand what they've missed without scrolling through individual items.
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from collections import defaultdict, Counter
import re
from pathlib import Path

from ..database.models import Notification


class SmartSummaryGenerator:
    """Generates intelligent summaries of notifications."""
    
    def __init__(self, db_path: str = "notifications.db"):
        self.db_path = db_path
        
        # Important patterns to detect
        self.financial_keywords = {
            'payment', 'invoice', 'bill', 'charge', 'transaction', 
            'balance', 'due', 'overdraft', 'credit', 'debit'
        }
        
        self.urgent_keywords = {
            'urgent', 'asap', 'emergency', 'critical', 'immediately',
            'deadline', 'expir', 'due', 'final', 'warning'
        }
        
        self.person_patterns = [
            r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b',  # Full names
            r'\b[A-Z][a-z]+\b(?:\s+(?:said|says|asked|wants))',  # First name + verb
        ]
        
    def generate_summary(
        self, 
        time_range: str = "1h",
        detail_level: str = "standard",
        focus_apps: Optional[List[str]] = None,
        since_timestamp: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate a smart summary of notifications.
        
        Args:
            time_range: Time range like "1h", "24h", "7d"
            detail_level: "brief", "standard", or "detailed"
            focus_apps: Optional list of apps to focus on
            since_timestamp: Optional timestamp to get notifications since
            
        Returns:
            Dictionary containing the summary
        """
        # Get notifications for the time period
        notifications = self._fetch_notifications(time_range, focus_apps, since_timestamp)
        
        if not notifications:
            return self._empty_summary(time_range)
            
        # Calculate time boundaries
        start_time, end_time = self._calculate_time_range(notifications, time_range, since_timestamp)
        
        # Generate statistics
        stats = self._calculate_statistics(notifications, start_time, end_time)
        
        # Extract critical items
        critical_items = self._extract_critical_items(notifications)
        
        # Detect conversations
        conversations = self._detect_conversations(notifications)
        
        # Group notifications intelligently
        grouped = self._group_notifications_simple(notifications)
        
        # Detect patterns
        patterns = self._detect_patterns(notifications, grouped)
        
        # Generate natural language summary
        if detail_level == "brief":
            summary_text = self._generate_brief_summary(
                stats, critical_items, conversations, grouped
            )
        elif detail_level == "detailed":
            summary_text = self._generate_detailed_summary(
                stats, critical_items, conversations, grouped, patterns
            )
        else:  # standard
            summary_text = self._generate_standard_summary(
                stats, critical_items, conversations, grouped
            )
            
        # Generate recommendations
        recommendations = self._generate_recommendations(
            stats, critical_items, conversations, grouped, patterns
        )
        
        return {
            "summary_period": {
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "duration_hours": (end_time - start_time).total_seconds() / 3600,
                "time_range": time_range
            },
            "statistics": stats,
            "critical_items": critical_items,
            "key_conversations": conversations,
            "grouped_notifications": grouped,
            "patterns": patterns,
            "summary": summary_text,
            "recommendations": recommendations,
            "detail_level": detail_level,
            "generated_at": datetime.now().isoformat()
        }
        
    def _fetch_notifications(
        self, 
        time_range: str,
        focus_apps: Optional[List[str]] = None,
        since_timestamp: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """Fetch notifications from database."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        # Build query
        query = """
            SELECT * FROM notifications 
            WHERE 1=1
        """
        
        params = []
        
        # Add time filter
        if since_timestamp:
            query += " AND delivered_time > datetime(?, 'unixepoch')"
            params.append(since_timestamp)
        else:
            # Parse time range
            time_delta = self._parse_time_range(time_range)
            cutoff = datetime.now() - time_delta
            query += " AND delivered_time > ?"
            params.append(cutoff.strftime('%Y-%m-%d %H:%M:%S'))
            
        # Add app filter
        if focus_apps:
            placeholders = ','.join(['?' for _ in focus_apps])
            query += f" AND app_identifier IN ({placeholders})"
            params.extend(focus_apps)
            
        # Check if archived column exists
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(notifications)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'archived' in columns:
            query += " AND (archived IS NULL OR archived = 0)"
            
        query += " ORDER BY delivered_time DESC"
        
        cursor = conn.execute(query, params)
        notifications = []
        for row in cursor.fetchall():
            notif = dict(row)
            # Ensure required fields
            notif['priority_level'] = notif.get('priority_level', 'MEDIUM')
            notif['is_read'] = notif.get('is_read', 0)
            notifications.append(notif)
        
        conn.close()
        
        return notifications
        
    def _parse_time_range(self, time_range: str) -> timedelta:
        """Parse time range string into timedelta."""
        match = re.match(r'(\d+)([hdwm])', time_range.lower())
        if not match:
            return timedelta(hours=1)  # Default to 1 hour
            
        value, unit = match.groups()
        value = int(value)
        
        if unit == 'h':
            return timedelta(hours=value)
        elif unit == 'd':
            return timedelta(days=value)
        elif unit == 'w':
            return timedelta(weeks=value)
        elif unit == 'm':
            return timedelta(days=value * 30)  # Approximate
        else:
            return timedelta(hours=1)
            
    def _calculate_time_range(
        self, 
        notifications: List[Dict[str, Any]],
        time_range: str,
        since_timestamp: Optional[float]
    ) -> Tuple[datetime, datetime]:
        """Calculate actual time range of notifications."""
        if notifications:
            # Parse delivered_time strings
            times = []
            for n in notifications:
                try:
                    dt = datetime.strptime(n['delivered_time'], '%Y-%m-%d %H:%M:%S')
                    times.append(dt)
                except:
                    pass
            
            if times:
                return min(times), max(times)
        
        # Default range
        end = datetime.now()
        if since_timestamp:
            start = datetime.fromtimestamp(since_timestamp)
        else:
            delta = self._parse_time_range(time_range)
            start = end - delta
        return start, end
            
    def _calculate_statistics(
        self, 
        notifications: List[Dict[str, Any]],
        start_time: datetime,
        end_time: datetime
    ) -> Dict[str, Any]:
        """Calculate summary statistics."""
        total = len(notifications)
        duration_hours = max((end_time - start_time).total_seconds() / 3600, 0.1)
        
        # Count by priority
        priority_counts = Counter(n['priority_level'] for n in notifications)
        
        # Count by app
        app_counts = Counter(n['app_identifier'] for n in notifications)
        top_apps = [
            self._humanize_app_name(app) 
            for app, _ in app_counts.most_common(3)
        ]
        
        # Calculate rate
        rate = total / duration_hours
        
        # Count unread
        unread = sum(1 for n in notifications if not n.get('is_read', 0))
        
        return {
            "total_notifications": total,
            "unread_count": unread,
            "by_priority": {
                "CRITICAL": priority_counts.get('CRITICAL', 0),
                "HIGH": priority_counts.get('HIGH', 0),
                "MEDIUM": priority_counts.get('MEDIUM', 0),
                "LOW": priority_counts.get('LOW', 0)
            },
            "by_app": dict(app_counts),
            "top_apps": top_apps,
            "notification_rate": f"{rate:.1f}/hour",
            "duration_hours": duration_hours
        }
        
    def _extract_critical_items(
        self, 
        notifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract critical and high priority items."""
        critical_items = []
        
        for notif in notifications:
            if notif.get('priority_level', 'MEDIUM') in ['CRITICAL', 'HIGH']:
                # Check for financial/urgent keywords
                text = f"{notif.get('title', '')} {notif.get('subtitle', '')} {notif.get('body', '')}"
                is_financial = any(kw in text.lower() for kw in self.financial_keywords)
                is_urgent = any(kw in text.lower() for kw in self.urgent_keywords)
                
                # Parse time
                try:
                    dt = datetime.strptime(notif['delivered_time'], '%Y-%m-%d %H:%M:%S')
                    time_str = dt.strftime('%Y-%m-%d %H:%M')
                except:
                    time_str = notif['delivered_time']
                
                critical_items.append({
                    "id": notif.get('id', notif.get('rec_id')),
                    "app": self._humanize_app_name(notif['app_identifier']),
                    "title": notif.get('title', ''),
                    "subtitle": notif.get('subtitle', ''),
                    "summary": self._summarize_notification(notif),
                    "priority": notif.get('priority_level', 'HIGH'),
                    "score": notif.get('priority_score', 0),
                    "time": time_str,
                    "is_financial": is_financial,
                    "is_urgent": is_urgent,
                    "is_read": bool(notif.get('is_read', False))
                })
                
        # Sort by priority score
        critical_items.sort(key=lambda x: x['score'], reverse=True)
        return critical_items[:10]  # Limit to top 10
        
    def _detect_conversations(
        self, 
        notifications: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect and summarize conversations."""
        conversations = defaultdict(list)
        
        # Group by app and person/thread
        for notif in notifications:
            if notif['app_identifier'] in ['com.apple.mobilesms', 'com.apple.MobileSMS', 
                                           'com.microsoft.teams', 'com.microsoft.teams2',
                                           'com.slack.slack', 'com.whatsapp']:
                # Try to extract person name
                person = self._extract_person_name(notif)
                if person:
                    key = (notif['app_identifier'], person)
                    conversations[key].append(notif)
                    
        # Summarize each conversation
        summaries = []
        for (app, person), messages in conversations.items():
            if len(messages) >= 2:  # Only include if multiple messages
                latest = max(messages, key=lambda m: m['delivered_time'])
                unread = sum(1 for m in messages if not m.get('is_read', False))
                
                # Parse latest time
                try:
                    dt = datetime.strptime(latest['delivered_time'], '%Y-%m-%d %H:%M:%S')
                    latest_time = dt.strftime('%H:%M')
                except:
                    latest_time = "recent"
                
                summaries.append({
                    "app": self._humanize_app_name(app),
                    "person": person,
                    "message_count": len(messages),
                    "unread_count": unread,
                    "latest_time": latest_time,
                    "summary": self._summarize_conversation(messages),
                    "needs_response": unread > 0 and self._needs_response(messages)
                })
                
        # Sort by unread count and recency
        summaries.sort(key=lambda x: (x['unread_count'], x['message_count']), reverse=True)
        return summaries[:5]  # Top 5 conversations
        
    def _group_notifications_simple(
        self, 
        notifications: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Simple grouping of notifications by app and type."""
        groups = defaultdict(list)
        
        # Group by app
        for notif in notifications:
            app = notif['app_identifier']
            groups[app].append(notif)
            
        # Convert to summary format
        grouped = {}
        for app, notifs in groups.items():
            if len(notifs) < 2:
                continue
                
            app_name = self._humanize_app_name(app)
            
            # Get time range
            times = []
            for n in notifs:
                try:
                    dt = datetime.strptime(n['delivered_time'], '%Y-%m-%d %H:%M:%S')
                    times.append(dt)
                except:
                    pass
                    
            if times:
                start_time = min(times).strftime('%H:%M')
                end_time = max(times).strftime('%H:%M')
            else:
                start_time = end_time = "unknown"
            
            # Determine priority
            priorities = [n.get('priority_level', 'MEDIUM') for n in notifs]
            if 'CRITICAL' in priorities:
                group_priority = 'CRITICAL'
            elif 'HIGH' in priorities:
                group_priority = 'HIGH'
            elif 'MEDIUM' in priorities:
                group_priority = 'MEDIUM'
            else:
                group_priority = 'LOW'
                
            grouped[app_name] = {
                "app": app_name,
                "count": len(notifs),
                "summary": self._generate_group_summary(notifs),
                "pattern": None,
                "priority": group_priority,
                "time_span": {
                    "start": start_time,
                    "end": end_time
                }
            }
            
        return grouped
        
    def _detect_patterns(
        self, 
        notifications: List[Dict[str, Any]],
        grouped: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Detect interesting patterns in notifications."""
        patterns = []
        
        # Check for notification storms
        time_buckets = defaultdict(list)
        for notif in notifications:
            try:
                dt = datetime.strptime(notif['delivered_time'], '%Y-%m-%d %H:%M:%S')
                bucket = int(dt.timestamp() // 300)  # 5-minute buckets
                time_buckets[bucket].append(notif)
            except:
                pass
                
        for bucket, bucket_notifs in time_buckets.items():
            if len(bucket_notifs) > 20:
                time_str = datetime.fromtimestamp(bucket * 300).strftime('%H:%M')
                patterns.append(f"Notification storm: {len(bucket_notifs)} notifications around {time_str}")
                
        # Check for unusual activity
        if any(g['count'] > 50 for g in grouped.values()):
            patterns.append("Unusually high activity detected from some apps")
            
        # Check for financial notifications
        financial_count = sum(
            1 for notif in notifications 
            if any(kw in str(notif).lower() for kw in self.financial_keywords)
        )
        if financial_count > 3:
            patterns.append(f"Multiple financial notifications ({financial_count} total)")
            
        # Check for after-hours activity
        late_night = 0
        for notif in notifications:
            try:
                dt = datetime.strptime(notif['delivered_time'], '%Y-%m-%d %H:%M:%S')
                if 0 <= dt.hour < 6:
                    late_night += 1
            except:
                pass
                
        if late_night > 5:
            patterns.append(f"Late night activity: {late_night} notifications between midnight and 6 AM")
            
        return patterns
        
    def _generate_brief_summary(
        self,
        stats: Dict[str, Any],
        critical: List[Dict[str, Any]],
        conversations: List[Dict[str, Any]],
        grouped: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate brief executive summary."""
        lines = []
        
        # Critical items
        if critical:
            for item in critical[:2]:  # Top 2 only
                prefix = "CRITICAL" if item['priority'] == 'CRITICAL' else "HIGH"
                lines.append(f"{prefix}: {item['summary']}")
                
        # Key conversations
        if conversations:
            conv = conversations[0]
            if conv['needs_response']:
                lines.append(f"MESSAGES: {conv['unread_count']} unread from {conv['person']}")
                
        # Overall summary
        total = stats['total_notifications']
        duration = stats['duration_hours']
        if duration < 2:
            time_desc = "last hour"
        elif duration < 25:
            time_desc = f"last {int(duration)} hours"
        else:
            time_desc = f"last {int(duration/24)} days"
            
        lines.append(f"SUMMARY: {total} notifications in {time_desc}. {stats['unread_count']} unread.")
        
        # Quick action
        if critical:
            lines.append("ACTION: Check critical items above.")
        elif conversations and conversations[0]['needs_response']:
            lines.append(f"ACTION: Respond to {conversations[0]['person']}.")
            
        return "\n".join(lines)
        
    def _generate_standard_summary(
        self,
        stats: Dict[str, Any],
        critical: List[Dict[str, Any]],
        conversations: List[Dict[str, Any]],
        grouped: Dict[str, Dict[str, Any]]
    ) -> str:
        """Generate standard summary."""
        sections = []
        
        # Header
        duration = stats['duration_hours']
        if duration < 2:
            period = "Last Hour"
        elif duration < 25:
            period = f"Last {int(duration)} Hours"
        else:
            period = f"Last {int(duration/24)} Days"
            
        sections.append(f"=== Notification Summary: {period} ===\n")
        
        # Urgent items
        if critical:
            sections.append("**Urgent Items:**")
            for item in critical[:5]:
                time_str = item['time'].split()[1] if ' ' in item['time'] else item['time']
                marker = "💰" if item['is_financial'] else "🚨" if item['is_urgent'] else "•"
                sections.append(f"{marker} {item['app']}: {item['summary']} ({time_str})")
            sections.append("")
            
        # Conversations
        if conversations:
            sections.append("**Messages & Communications:**")
            for conv in conversations[:3]:
                status = "needs reply" if conv['needs_response'] else "read"
                sections.append(
                    f"• {conv['person']} ({conv['message_count']} messages, "
                    f"{conv['unread_count']} unread): {conv['summary']}"
                )
            sections.append("")
            
        # Routine activity
        routine_items = []
        for name, group in grouped.items():
            if group['priority'] == 'LOW' and group['count'] > 5:
                routine_items.append(f"• {group['app']}: {group['count']} {group['summary']}")
                
        if routine_items:
            sections.append("**Routine Activity:**")
            sections.extend(routine_items[:5])
            sections.append("")
            
        # Summary stats
        sections.append("**Summary:**")
        sections.append(f"• Total: {stats['total_notifications']} notifications ({stats['unread_count']} unread)")
        sections.append(f"• Rate: {stats['notification_rate']}")
        sections.append(f"• Top apps: {', '.join(stats['top_apps'])}")
        
        return "\n".join(sections)
        
    def _generate_detailed_summary(
        self,
        stats: Dict[str, Any],
        critical: List[Dict[str, Any]],
        conversations: List[Dict[str, Any]],
        grouped: Dict[str, Dict[str, Any]],
        patterns: List[str]
    ) -> str:
        """Generate detailed summary with patterns and insights."""
        # Start with standard summary
        summary = self._generate_standard_summary(stats, critical, conversations, grouped)
        
        # Add patterns section
        if patterns:
            summary += "\n\n**Patterns & Insights:**"
            for pattern in patterns:
                summary += f"\n• {pattern}"
                
        # Add detailed statistics
        summary += "\n\n**Detailed Statistics:**"
        summary += f"\n• Priority breakdown:"
        for level, count in stats['by_priority'].items():
            if count > 0:
                percentage = (count / stats['total_notifications']) * 100
                summary += f"\n  - {level}: {count} ({percentage:.1f}%)"
                
        # Add app breakdown for top apps
        summary += f"\n• Top applications:"
        app_counts = stats['by_app']
        for app, count in sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            percentage = (count / stats['total_notifications']) * 100
            summary += f"\n  - {self._humanize_app_name(app)}: {count} ({percentage:.1f}%)"
            
        return summary
        
    def _generate_recommendations(
        self,
        stats: Dict[str, Any],
        critical: List[Dict[str, Any]],
        conversations: List[Dict[str, Any]],
        grouped: Dict[str, Dict[str, Any]],
        patterns: List[str]
    ) -> List[str]:
        """Generate actionable recommendations."""
        recommendations = []
        
        # Critical items recommendations
        unhandled_critical = [c for c in critical if not c['is_read']]
        if unhandled_critical:
            if any(c['is_financial'] for c in unhandled_critical):
                recommendations.append("Review and process financial notifications immediately")
            else:
                recommendations.append(f"Address {len(unhandled_critical)} critical unread items")
                
        # Conversation recommendations
        needs_response = [c for c in conversations if c['needs_response']]
        if needs_response:
            people = [c['person'] for c in needs_response[:3]]
            recommendations.append(f"Respond to messages from: {', '.join(people)}")
            
        # Volume recommendations
        camera_groups = [g for name, g in grouped.items() if 'camera' in name.lower()]
        if camera_groups and sum(g['count'] for g in camera_groups) > 100:
            recommendations.append("Consider archiving old security camera notifications")
            
        # Pattern-based recommendations
        if any('storm' in p for p in patterns):
            recommendations.append("Investigate notification storms - may indicate an issue")
            
        if any('Late night' in p for p in patterns):
            recommendations.append("Review late night notifications - consider enabling Do Not Disturb")
            
        # High volume recommendations
        if stats['total_notifications'] > 200:
            low_priority = stats['by_priority']['LOW']
            if low_priority > 150:
                recommendations.append(f"Archive {low_priority} low-priority notifications to reduce clutter")
                
        # Unread recommendations
        if stats['unread_count'] > 50:
            recommendations.append("Use batch actions to mark old notifications as read")
            
        return recommendations[:5]  # Limit to 5 most important
        
    def _empty_summary(self, time_range: str) -> Dict[str, Any]:
        """Return empty summary when no notifications found."""
        return {
            "summary_period": {
                "start": (datetime.now() - self._parse_time_range(time_range)).isoformat(),
                "end": datetime.now().isoformat(),
                "duration_hours": self._parse_time_range(time_range).total_seconds() / 3600,
                "time_range": time_range
            },
            "statistics": {
                "total_notifications": 0,
                "unread_count": 0,
                "by_priority": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
                "by_app": {},
                "top_apps": [],
                "notification_rate": "0/hour"
            },
            "critical_items": [],
            "key_conversations": [],
            "grouped_notifications": {},
            "patterns": [],
            "summary": "No notifications found for this time period.",
            "recommendations": [],
            "generated_at": datetime.now().isoformat()
        }
        
    def _humanize_app_name(self, app_id: str) -> str:
        """Convert app identifier to human-readable name."""
        app_names = {
            'com.apple.mobilesms': 'Messages',
            'com.apple.MobileSMS': 'Messages',
            'com.apple.mail': 'Mail',
            'com.microsoft.outlook': 'Outlook',
            'com.microsoft.teams': 'Teams',
            'com.microsoft.teams2': 'Teams',
            'com.apple.facetime': 'FaceTime',
            'com.security.batterycam': 'Security Camera',
            'com.apple.news': 'News',
            'com.apple.passbook': 'Wallet',
            'com.apple.scripteditor2': 'Script Editor',
            'com.slack.slack': 'Slack',
            'com.whatsapp': 'WhatsApp',
            'com.weather.twc': 'Weather',
            'com.apple.home': 'Home',
            'com.firewalla.firewalla': 'Firewalla',
            'com.flightyapp.flighty': 'Flighty',
            'com.eero.eero-ios': 'Eero'
        }
        return app_names.get(app_id, app_id.split('.')[-1].title())
        
    def _summarize_notification(self, notif: Dict[str, Any]) -> str:
        """Create concise summary of a single notification."""
        title = notif.get('title', '')
        subtitle = notif.get('subtitle', '')
        body = notif.get('body', '')
        
        # Prefer title + subtitle
        if title and subtitle:
            return f"{title}: {subtitle}"
        elif title:
            return title
        elif subtitle:
            return subtitle
        elif body:
            # Truncate long body
            return body[:100] + '...' if len(body) > 100 else body
        else:
            return "Notification"
            
    def _extract_person_name(self, notif: Dict[str, Any]) -> Optional[str]:
        """Try to extract person's name from notification."""
        # Check title first
        title = notif.get('title', '')
        
        # Direct name in title (common for Messages)
        if title and not any(c in title for c in [':', '@', '.com']):
            # Simple heuristic: if title is 1-3 words and starts with capital
            words = title.split()
            if 1 <= len(words) <= 3 and words[0][0].isupper():
                return title
                
        # Try regex patterns
        text = f"{title} {notif.get('subtitle', '')} {notif.get('body', '')}"
        for pattern in self.person_patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(0).strip()
                # Filter out false positives
                if name and len(name) < 30 and name[0].isupper():
                    return name.split()[0]  # Just first name
                    
        return None
        
    def _summarize_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Summarize a conversation thread."""
        # Look for question marks or specific keywords
        texts = [f"{m.get('subtitle', '')} {m.get('body', '')}" for m in messages]
        full_text = ' '.join(texts).lower()
        
        if '?' in full_text:
            if 'dinner' in full_text or 'lunch' in full_text:
                return "Making meal plans"
            elif 'when' in full_text or 'what time' in full_text:
                return "Scheduling discussion"
            else:
                return "Asking questions"
        elif any(word in full_text for word in ['meeting', 'call', 'zoom']):
            return "Work discussion"
        elif any(word in full_text for word in ['love', 'miss', 'family']):
            return "Personal chat"
        else:
            # Generic summary based on message count
            count = len(messages)
            if count > 10:
                return "Extended conversation"
            elif count > 5:
                return "Active discussion"
            else:
                return "Brief exchange"
                
    def _needs_response(self, messages: List[Dict[str, Any]]) -> bool:
        """Determine if conversation needs a response."""
        # Check if latest messages are unread and contain questions
        recent_unread = []
        for m in messages:
            if not m.get('is_read', False):
                try:
                    dt = datetime.strptime(m['delivered_time'], '%Y-%m-%d %H:%M:%S')
                    if (datetime.now() - dt).total_seconds() < 3600:
                        recent_unread.append(m)
                except:
                    pass
        
        if not recent_unread:
            return False
            
        # Check for question marks or question words
        for msg in recent_unread:
            text = f"{msg.get('subtitle', '')} {msg.get('body', '')}".lower()
            if '?' in text or any(q in text for q in ['when', 'where', 'what', 'how', 'why', 'can you', 'will you', 'are you']):
                return True
                
        return False
        
    def _generate_group_summary(self, notifications: List[Dict[str, Any]]) -> str:
        """Generate summary for a group of notifications."""
        # Check notification types
        titles = [n.get('title', '') for n in notifications if n.get('title')]
        
        if not titles:
            return "notifications"
            
        # Find common patterns
        if all('update' in t.lower() for t in titles):
            return "update notifications"
        elif all('new' in t.lower() for t in titles):
            return "new items"
        elif all('reminder' in t.lower() for t in titles):
            return "reminders"
        else:
            # Use most common words
            words = Counter()
            for title in titles:
                words.update(word.lower() for word in title.split() 
                           if len(word) > 3 and word.isalpha())
            if words:
                common = words.most_common(1)[0][0]
                return f"{common} notifications"
            else:
                return "notifications"


# Convenience functions for common use cases
def get_hourly_digest(db_path: str = "notifications.db") -> Dict[str, Any]:
    """Get a quick hourly digest."""
    generator = SmartSummaryGenerator(db_path)
    return generator.generate_summary(time_range="1h", detail_level="standard")


def get_daily_digest(db_path: str = "notifications.db") -> Dict[str, Any]:
    """Get comprehensive daily digest."""
    generator = SmartSummaryGenerator(db_path)
    return generator.generate_summary(time_range="24h", detail_level="detailed")


def get_executive_brief(db_path: str = "notifications.db") -> Dict[str, Any]:
    """Get ultra-brief executive summary."""
    generator = SmartSummaryGenerator(db_path)
    return generator.generate_summary(time_range="4h", detail_level="brief")
