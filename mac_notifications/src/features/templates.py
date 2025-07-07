#!/usr/bin/env python3
"""
Notification Templates Module
Provides standardized templates for different notification types based on priority and category
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import re
import logging


class NotificationTemplates:
    """Format notifications using category-specific templates"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Define emoji and color codes for different categories
        self.category_icons = {
            'financial': '💳',
            'security': '🔐',
            'medical': '⚕️',
            'work': '💼',
            'urgency': '🚨',
            'communication': '💬',
            'general': '📬'
        }
        
        # ANSI color codes for terminal output
        self.priority_colors = {
            'CRITICAL': '\033[91m',  # Red
            'HIGH': '\033[93m',      # Yellow
            'MEDIUM': '\033[94m',    # Blue
            'LOW': '\033[92m',       # Green
            'UNKNOWN': '\033[90m',   # Gray
            'RESET': '\033[0m'       # Reset
        }
        
        # HTML color codes
        self.html_colors = {
            'CRITICAL': '#dc3545',
            'HIGH': '#ffc107',
            'MEDIUM': '#17a2b8',
            'LOW': '#28a745',
            'UNKNOWN': '#6c757d'
        }
    
    def format_notification(self, notification: Dict[str, Any], 
                          use_color: bool = True, 
                          format_type: str = 'terminal') -> str:
        """
        Format a notification using appropriate template
        
        Args:
            notification: Notification dict with priority info
            use_color: Whether to include ANSI color codes
            format_type: 'terminal', 'html', or 'markdown'
        """
        if format_type == 'terminal':
            return self._format_terminal(notification, use_color)
        elif format_type == 'html':
            return self._format_html(notification)
        elif format_type == 'markdown':
            return self._format_markdown(notification)
        else:
            return self._format_terminal(notification, False)
    
    def _determine_category(self, notification: Dict[str, Any]) -> str:
        """Determine notification category from priority factors"""
        factors = notification.get('priority_factors', [])
        
        # Parse factors as strings if they're JSON
        if factors and isinstance(factors[0], str):
            try:
                import json
                factors = json.loads(factors[0]) if factors[0].startswith('[') else factors
            except:
                pass
        
        # Check factors for category keywords
        for factor in factors:
            factor_str = str(factor).lower()
            if 'financial:' in factor_str or 'amount:' in factor_str:
                return 'financial'
            elif 'security:' in factor_str:
                return 'security'
            elif 'medical:' in factor_str:
                return 'medical'
            elif 'work:' in factor_str:
                return 'work'
            elif 'urgency:' in factor_str:
                return 'urgency'
            elif 'communication:' in factor_str:
                return 'communication'
        
        # Check app identifier
        app_id = notification.get('app_identifier', '').lower()
        if 'passbook' in app_id or 'wallet' in app_id:
            return 'financial'
        elif 'security' in app_id or 'camera' in app_id:
            return 'security'
        elif 'teams' in app_id or 'outlook' in app_id or 'slack' in app_id:
            return 'work'
        elif 'mobilesms' in app_id or 'mail' in app_id:
            return 'communication'
        
        return 'general'
    
    def _format_time(self, time_str: str) -> str:
        """Format time string for display"""
        try:
            # Handle both datetime objects and strings
            if isinstance(time_str, datetime):
                dt = time_str
            else:
                # Try different formats
                for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S.%f']:
                    try:
                        dt = datetime.strptime(time_str.split('.')[0], fmt.split('.')[0])
                        break
                    except:
                        continue
                else:
                    return time_str
            
            now = datetime.now()
            
            # If today, show time only
            if dt.date() == now.date():
                return dt.strftime('%I:%M %p')
            # If yesterday
            elif (now - dt).days == 1:
                return f"Yesterday {dt.strftime('%I:%M %p')}"
            # If this week
            elif (now - dt).days < 7:
                return dt.strftime('%a %I:%M %p')
            # Otherwise show date
            else:
                return dt.strftime('%b %d, %I:%M %p')
        except Exception as e:
            self.logger.debug(f"Error formatting time: {e}")
            return str(time_str)
    
    def _extract_amount(self, text: str) -> Optional[str]:
        """Extract monetary amount from text"""
        if not text:
            return None
        pattern = r'\$[\d,]+\.?\d*'
        matches = re.findall(pattern, str(text))
        return matches[0] if matches else None
    
    def _truncate_text(self, text: str, max_length: int = 200) -> str:
        """Truncate text with ellipsis if needed"""
        if not text:
            return ""
        text = str(text)
        return text[:max_length] + '...' if len(text) > max_length else text
    
    def _format_terminal(self, notification: Dict[str, Any], use_color: bool) -> str:
        """Format notification for terminal output"""
        category = self._determine_category(notification)
        priority_level = notification.get('priority_level', 'UNKNOWN')
        
        # Get color codes
        color = self.priority_colors.get(priority_level, '') if use_color else ''
        reset = self.priority_colors['RESET'] if use_color else ''
        
        # Get icon
        icon = self.category_icons.get(category, '📬')
        
        # Extract fields
        title = notification.get('title', 'Notification')
        subtitle = notification.get('subtitle', '')
        body = notification.get('body', '')
        time = self._format_time(notification.get('delivered_time', ''))
        score = notification.get('priority_score', 0)
        app = notification.get('app_identifier', '').split('.')[-1]
        
        # Format based on priority level
        if priority_level == 'CRITICAL':
            template = f"""{color}
{icon} 🚨 CRITICAL: {title.upper()}
{'━' * 40}
From: {app} | Time: {time}
{subtitle}
{self._truncate_text(body, 200)}
{'━' * 40}
⚡ IMMEDIATE ACTION REQUIRED ⚡{reset}
"""
        elif priority_level == 'HIGH':
            template = f"""{color}
{icon} HIGH PRIORITY: {title}
{'─' * 30}
{app} • {time}
{subtitle}
{self._truncate_text(body, 150)}
{'─' * 30}{reset}
"""
        elif priority_level == 'MEDIUM':
            template = f"""{color}{icon} {title}
   {subtitle if subtitle else app} • {time}
   {self._truncate_text(body, 100) if body else ''}{reset}
"""
        else:  # LOW or UNKNOWN
            template = f"{color}{icon} {title} - {time}{reset}"
        
        return template.strip()
    
    def _format_html(self, notification: Dict[str, Any]) -> str:
        """Format notification as HTML"""
        category = self._determine_category(notification)
        priority_level = notification.get('priority_level', 'UNKNOWN')
        
        icon = self.category_icons.get(category, '📬')
        color = self.html_colors.get(priority_level, '#6c757d')
        
        title = notification.get('title', 'Notification')
        body = notification.get('body', '')
        subtitle = notification.get('subtitle', '')
        time = self._format_time(notification.get('delivered_time', ''))
        score = notification.get('priority_score', 0)
        app = notification.get('app_identifier', '').split('.')[-1]
        
        # Escape HTML
        from html import escape
        title = escape(str(title))
        body = escape(str(body))
        subtitle = escape(str(subtitle))
        
        html = f"""
<div style="border-left: 4px solid {color}; padding: 12px; margin: 10px 0; background-color: #f8f9fa; border-radius: 4px;">
    <div style="display: flex; align-items: center; margin-bottom: 8px;">
        <span style="font-size: 24px; margin-right: 10px;">{icon}</span>
        <strong style="color: {color}; font-size: 16px; flex-grow: 1;">{title}</strong>
        <span style="color: #6c757d; font-size: 12px;">{time}</span>
    </div>
    {f'<div style="color: #666; font-size: 14px; margin-bottom: 5px;">{subtitle}</div>' if subtitle else ''}
    {f'<div style="font-size: 14px; color: #333; margin-bottom: 8px;">{self._truncate_text(body, 200)}</div>' if body else ''}
    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
        <span style="font-size: 12px; color: #999;">
            <strong>{app}</strong>
        </span>
        <span style="font-size: 12px;">
            Priority: <span style="color: {color}; font-weight: bold;">{priority_level}</span> 
            (Score: {score:.1f})
        </span>
    </div>
</div>
"""
        return html
    
    def _format_markdown(self, notification: Dict[str, Any]) -> str:
        """Format notification as Markdown"""
        category = self._determine_category(notification)
        priority_level = notification.get('priority_level', 'UNKNOWN')
        
        icon = self.category_icons.get(category, '📬')
        
        title = notification.get('title', 'Notification')
        body = notification.get('body', '')
        subtitle = notification.get('subtitle', '')
        time = self._format_time(notification.get('delivered_time', ''))
        score = notification.get('priority_score', 0)
        app = notification.get('app_identifier', '').split('.')[-1]
        
        # Priority indicator
        priority_markers = {
            'CRITICAL': '🔴',
            'HIGH': '🟡',
            'MEDIUM': '🔵',
            'LOW': '🟢',
            'UNKNOWN': '⚪'
        }
        marker = priority_markers.get(priority_level, '⚪')
        
        md = f"""### {marker} {icon} {title}

**App:** {app} | **Time:** {time}  
**Priority:** {priority_level} (Score: {score:.1f})  
"""
        
        if subtitle:
            md += f"\n*{subtitle}*\n"
        
        if body:
            md += f"\n{self._truncate_text(body, 200)}\n"
        
        md += "\n---\n"
        
        return md
    
    def format_notification_list(self, notifications: List[Dict[str, Any]], 
                               format_type: str = 'terminal',
                               use_color: bool = True) -> str:
        """Format a list of notifications"""
        if not notifications:
            return "No notifications to display."
        
        if format_type == 'terminal':
            output = []
            for notif in notifications:
                output.append(self.format_notification(notif, use_color, format_type))
            return '\n\n'.join(output)
        
        elif format_type == 'html':
            html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background-color: #f5f5f5; 
            padding: 20px;
            line-height: 1.6;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background-color: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 { 
            color: #333; 
            margin-bottom: 30px;
        }
        .stats {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📬 Notifications</h1>
        <div class="stats">
            Total: {count} notifications
        </div>
""".format(count=len(notifications))
            
            for notif in notifications:
                html += self.format_notification(notif, False, format_type)
            
            html += """
    </div>
</body>
</html>
"""
            return html
        
        elif format_type == 'markdown':
            md = f"# 📬 Notifications\n\n**Total:** {len(notifications)} notifications\n\n"
            for notif in notifications:
                md += self.format_notification(notif, False, format_type)
            return md
        
        else:
            return self.format_notification_list(notifications, 'terminal', False)


# Convenience functions for backward compatibility
def format_notification(notification: Dict[str, Any], 
                       use_color: bool = True,
                       format_type: str = 'terminal') -> str:
    """Format a single notification"""
    templates = NotificationTemplates()
    return templates.format_notification(notification, use_color, format_type)


def format_notification_list(notifications: List[Dict[str, Any]],
                           format_type: str = 'terminal',
                           use_color: bool = True) -> str:
    """Format a list of notifications"""
    templates = NotificationTemplates()
    return templates.format_notification_list(notifications, format_type, use_color)
