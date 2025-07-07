#!/usr/bin/env python3
"""
Feature #3: Enhanced Search & Query
Provides advanced search capabilities including natural language processing,
regex support, date filtering, and complex boolean queries
"""

import re
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import json


class EnhancedSearch:
    """Advanced search engine for notifications"""
    
    def __init__(self):
        # Natural language time mappings
        self.time_mappings = {
            'today': lambda: datetime.now().replace(hour=0, minute=0, second=0, microsecond=0),
            'yesterday': lambda: (datetime.now() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0),
            'this week': lambda: datetime.now() - timedelta(days=datetime.now().weekday()),
            'last week': lambda: datetime.now() - timedelta(days=datetime.now().weekday() + 7),
            'this month': lambda: datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0),
            'last month': lambda: (datetime.now().replace(day=1) - timedelta(days=1)).replace(day=1, hour=0, minute=0, second=0, microsecond=0),
        }
        
        # Natural language to SQL operator mappings
        self.operator_mappings = {
            'and': 'AND',
            'or': 'OR',
            'not': 'NOT',
            'but not': 'AND NOT',
            'except': 'AND NOT',
            'without': 'AND NOT',
        }
        
        # App name aliases
        self.app_aliases = {
            'messages': ['com.apple.mobilesms', 'com.apple.messages'],
            'mail': ['com.apple.mail'],
            'outlook': ['com.microsoft.outlook'],
            'teams': ['com.microsoft.teams', 'com.microsoft.teams2'],
            'camera': ['com.security.batterycam'],
            'cameras': ['com.security.batterycam'],
            'security': ['com.security.batterycam', 'com.firewalla.firewalla'],
            'security camera': ['com.security.batterycam'],
            'security cameras': ['com.security.batterycam'],
            'firewalla': ['com.firewalla.firewalla'],
            'wallet': ['com.apple.passbook'],
            'news': ['com.apple.news'],
            'script': ['com.apple.scripteditor2'],
        }
        
        # Search field weights for ranking
        self.field_weights = {
            'title': 3.0,
            'subtitle': 2.0,
            'body': 1.0,
            'app_identifier': 1.5,
        }
    
    def parse_natural_language_query(self, query: str) -> Dict[str, Any]:
        """Parse natural language query into structured search parameters"""
        # Handle common security-specific queries
        query_lower = query.lower()
        
        # Shortcut for common security queries
        if query_lower == "strangers" or query_lower == "stranger detections":
            return {
                'keywords': ['stranger'],
                'apps': ['com.security.batterycam'],
                'time_range': None,
                'priority_filter': None,
                'exclude_keywords': [],
                'regex_pattern': None,
                'group_by': None,
                'sort_by': 'time',
            }
        elif query_lower == "security alerts no vehicles" or query_lower == "security no cars":
            return {
                'keywords': [],
                'apps': ['com.security.batterycam'],
                'time_range': None,
                'priority_filter': None,
                'exclude_keywords': ['vehicle', 'car'],
                'regex_pattern': None,
                'group_by': None,
                'sort_by': 'time',
            }
        
        # Continue with normal parsing
        params = {
            'keywords': [],
            'apps': [],
            'time_range': None,
            'priority_filter': None,
            'exclude_keywords': [],
            'regex_pattern': None,
            'group_by': None,
            'sort_by': 'relevance',
        }
        
        # Extract time range
        for time_phrase, time_func in self.time_mappings.items():
            if time_phrase in query_lower:
                if 'between' in query_lower and ' and ' in query_lower:
                    # Handle "between X and Y" format
                    match = re.search(r'between\s+(.+?)\s+and\s+(.+?)(?:\s|$)', query_lower)
                    if match:
                        start_str, end_str = match.groups()
                        params['time_range'] = self._parse_time_range(start_str, end_str)
                else:
                    # Simple time phrase
                    start_time = time_func()
                    if 'last' in time_phrase:
                        end_time = datetime.now()
                    else:
                        end_time = start_time + timedelta(days=1 if 'today' in time_phrase else 7)
                    params['time_range'] = (start_time, end_time)
                query_lower = query_lower.replace(time_phrase, '')
                break  # Only match first time phrase
        
        # Extract priority filter
        priority_patterns = {
            'critical': 'CRITICAL',
            'high priority': 'HIGH',
            'medium priority': 'MEDIUM',
            'low priority': 'LOW',
            'important': 'important',
            'urgent': 'CRITICAL',
        }
        
        for pattern, priority in priority_patterns.items():
            if pattern in query_lower:
                params['priority_filter'] = priority
                query_lower = query_lower.replace(pattern, '')
        
        # Extract app filters
        for alias, app_ids in self.app_aliases.items():
            if f'from {alias}' in query_lower or f'in {alias}' in query_lower:
                params['apps'].extend(app_ids)
                query_lower = re.sub(f'(from|in)\s+{alias}', '', query_lower)
        
        # Extract exclusions
        exclusion_patterns = ['but not', 'except', 'without', 'excluding']
        for pattern in exclusion_patterns:
            if pattern in query_lower:
                parts = query_lower.split(pattern)
                if len(parts) > 1:
                    exclude_part = parts[1].strip()
                    # Extract first word/phrase after exclusion
                    exclude_match = re.match(r'(\w+(?:\s+\w+)?)', exclude_part)
                    if exclude_match:
                        params['exclude_keywords'].append(exclude_match.group(1))
                    query_lower = parts[0].strip()
        
        # Extract grouping
        if 'group by' in query_lower:
            if 'app' in query_lower:
                params['group_by'] = 'app'
            elif 'hour' in query_lower:
                params['group_by'] = 'hour'
            elif 'day' in query_lower:
                params['group_by'] = 'day'
            query_lower = re.sub(r'group\s+by\s+\w+', '', query_lower)
        
        # Extract sorting
        if 'sort by time' in query_lower or 'newest first' in query_lower:
            params['sort_by'] = 'time'
        elif 'sort by priority' in query_lower:
            params['sort_by'] = 'priority'
        
        # Extract regex pattern if present
        regex_match = re.search(r'/(.+?)/', query)
        if regex_match:
            params['regex_pattern'] = regex_match.group(1)
            query_lower = query_lower.replace(f'/{regex_match.group(1)}/', '')
        
        # Remaining words are keywords
        keywords = query_lower.strip().split()
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'show', 'me', 'all', 'find', 'search', 'get', 'list'}
        params['keywords'] = [word for word in keywords if word not in stop_words and len(word) > 2]
        
        return params
    
    def _parse_time_range(self, start_str: str, end_str: str) -> Optional[Tuple[datetime, datetime]]:
        """Parse time range strings into datetime objects"""
        try:
            # Try various date formats
            formats = ['%Y-%m-%d', '%m/%d/%Y', '%d-%m-%Y', '%B %d', '%b %d']
            
            start_dt = None
            end_dt = None
            
            # Check for relative times
            if 'hour' in start_str:
                hours = int(re.search(r'(\d+)', start_str).group(1))
                start_dt = datetime.now() - timedelta(hours=hours)
            elif 'day' in start_str:
                days = int(re.search(r'(\d+)', start_str).group(1))
                start_dt = datetime.now() - timedelta(days=days)
            else:
                # Try parsing as date
                for fmt in formats:
                    try:
                        start_dt = datetime.strptime(start_str.strip(), fmt)
                        if '%Y' not in fmt:
                            start_dt = start_dt.replace(year=datetime.now().year)
                        break
                    except ValueError:
                        continue
            
            # Parse end time
            if 'now' in end_str or 'today' in end_str:
                end_dt = datetime.now()
            else:
                for fmt in formats:
                    try:
                        end_dt = datetime.strptime(end_str.strip(), fmt)
                        if '%Y' not in fmt:
                            end_dt = end_dt.replace(year=datetime.now().year)
                        break
                    except ValueError:
                        continue
            
            if start_dt and end_dt:
                return (start_dt, end_dt)
                
        except Exception:
            pass
        
        return None
    
    def build_sql_query(self, params: Dict[str, Any], has_priority: bool = True) -> Tuple[str, List[Any]]:
        """Build SQL query from parsed parameters"""
        # Base query
        if has_priority:
            query = '''
                SELECT 
                    id, rec_id, app_identifier, delivered_time,
                    title, subtitle, body, category, thread, created_at,
                    priority_score, priority_level, priority_factors
                FROM notifications
                WHERE 1=1
            '''
        else:
            query = '''
                SELECT 
                    id, rec_id, app_identifier, delivered_time,
                    title, subtitle, body, category, thread, created_at
                FROM notifications
                WHERE 1=1
            '''
        
        sql_params = []
        
        # Add time range filter
        if params['time_range']:
            start_time, end_time = params['time_range']
            query += ' AND datetime(delivered_time) BETWEEN datetime(?) AND datetime(?)'
            sql_params.extend([start_time.strftime('%Y-%m-%d %H:%M:%S'), 
                             end_time.strftime('%Y-%m-%d %H:%M:%S')])
        
        # Add priority filter
        if params['priority_filter'] and has_priority:
            if params['priority_filter'] == 'important':
                query += " AND priority_level IN ('CRITICAL', 'HIGH')"
            else:
                query += ' AND priority_level = ?'
                sql_params.append(params['priority_filter'])
        
        # Add app filter
        if params['apps']:
            placeholders = ','.join(['?' for _ in params['apps']])
            query += f' AND app_identifier IN ({placeholders})'
            sql_params.extend(params['apps'])
        
        # Add keyword search
        if params['keywords'] or params['regex_pattern']:
            if params['regex_pattern']:
                # Use regex
                query += '''
                    AND (
                        title REGEXP ? 
                        OR subtitle REGEXP ?
                        OR body REGEXP ?
                    )
                '''
                sql_params.extend([params['regex_pattern']] * 3)
            else:
                # Standard keyword search
                keyword_conditions = []
                for keyword in params['keywords']:
                    keyword_conditions.append('''
                        (
                            LOWER(title) LIKE ? 
                            OR LOWER(subtitle) LIKE ?
                            OR LOWER(body) LIKE ?
                        )
                    ''')
                    keyword_pattern = f'%{keyword}%'
                    sql_params.extend([keyword_pattern] * 3)
                
                if keyword_conditions:
                    query += ' AND (' + ' AND '.join(keyword_conditions) + ')'
        
        # Add exclusions
        if params['exclude_keywords']:
            for exclude in params['exclude_keywords']:
                query += '''
                    AND NOT (
                        LOWER(title) LIKE ? 
                        OR LOWER(subtitle) LIKE ?
                        OR LOWER(body) LIKE ?
                    )
                '''
                exclude_pattern = f'%{exclude}%'
                sql_params.extend([exclude_pattern] * 3)
        
        # Add sorting
        if params['sort_by'] == 'time':
            query += ' ORDER BY delivered_time DESC'
        elif params['sort_by'] == 'priority' and has_priority:
            query += ' ORDER BY priority_score DESC, delivered_time DESC'
        else:
            # Relevance sorting would require full-text search
            query += ' ORDER BY delivered_time DESC'
        
        return query, sql_params
    
    def search(self, query: str, conn: sqlite3.Connection, limit: int = 50) -> Dict[str, Any]:
        """Execute a natural language search query"""
        # Parse the query
        params = self.parse_natural_language_query(query)
        
        # Check if priority columns exist
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(notifications)")
        columns = [col[1] for col in cursor.fetchall()]
        has_priority = 'priority_score' in columns
        
        # Build SQL query
        sql_query, sql_params = self.build_sql_query(params, has_priority)
        sql_query += ' LIMIT ?'
        sql_params.append(limit)
        
        # Execute query
        cursor.execute(sql_query, sql_params)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        # Format results
        notifications = []
        for row in rows:
            notif = dict(zip(columns, row))
            formatted_notif = {
                "id": f"notif_{notif['rec_id']}",
                "rec_id": notif['rec_id'],
                "app_identifier": notif['app_identifier'],
                "delivered_time": notif['delivered_time'],
                "title": notif['title'] or "",
                "subtitle": notif['subtitle'] or "",
                "body": notif['body'] or "",
                "category": notif['category'] or "",
                "thread": notif['thread'] or "",
            }
            
            if has_priority:
                formatted_notif['priority_score'] = notif.get('priority_score', 0)
                formatted_notif['priority_level'] = notif.get('priority_level', 'UNKNOWN')
                formatted_notif['priority_factors'] = json.loads(notif.get('priority_factors', '[]'))
            
            notifications.append(formatted_notif)
        
        # Handle grouping if requested
        if params['group_by']:
            grouped_results = self._group_results(notifications, params['group_by'])
            return {
                'query': query,
                'parsed_params': self._serialize_params(params),
                'total_found': len(notifications),
                'grouped_by': params['group_by'],
                'groups': grouped_results
            }
        
        return {
            'query': query,
            'parsed_params': self._serialize_params(params),
            'total_found': len(notifications),
            'notifications': notifications
        }
    
    def _serialize_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize parameters for JSON output"""
        serialized = params.copy()
        if params['time_range']:
            start, end = params['time_range']
            serialized['time_range'] = {
                'start': start.strftime('%Y-%m-%d %H:%M:%S'),
                'end': end.strftime('%Y-%m-%d %H:%M:%S')
            }
        return serialized
    
    def _group_results(self, notifications: List[Dict[str, Any]], group_by: str) -> Dict[str, Any]:
        """Group search results by specified field"""
        groups = {}
        
        for notif in notifications:
            if group_by == 'app':
                key = notif['app_identifier'].split('.')[-1]
            elif group_by == 'hour':
                dt = datetime.strptime(notif['delivered_time'], '%Y-%m-%d %H:%M:%S')
                key = dt.strftime('%Y-%m-%d %H:00')
            elif group_by == 'day':
                dt = datetime.strptime(notif['delivered_time'], '%Y-%m-%d %H:%M:%S')
                key = dt.strftime('%Y-%m-%d')
            else:
                key = 'unknown'
            
            if key not in groups:
                groups[key] = {
                    'count': 0,
                    'notifications': [],
                    'priority_breakdown': {},
                    'time_range': {
                        'earliest': notif['delivered_time'],
                        'latest': notif['delivered_time']
                    }
                }
            
            groups[key]['count'] += 1
            
            # Update time range
            if notif['delivered_time'] < groups[key]['time_range']['earliest']:
                groups[key]['time_range']['earliest'] = notif['delivered_time']
            if notif['delivered_time'] > groups[key]['time_range']['latest']:
                groups[key]['time_range']['latest'] = notif['delivered_time']
            
            # Don't include full notifications in groups to avoid serialization issues
            # Just store summary info
            groups[key]['notifications'].append({
                'rec_id': notif['rec_id'],
                'time': notif['delivered_time'],
                'app': notif['app_identifier'].split('.')[-1],
                'title': notif.get('title', ''),
                'priority': notif.get('priority_level', 'UNKNOWN')
            })
            
            # Track priority breakdown
            if 'priority_level' in notif:
                level = notif['priority_level']
                groups[key]['priority_breakdown'][level] = groups[key]['priority_breakdown'].get(level, 0) + 1
        
        return groups
    
    def get_search_suggestions(self, partial_query: str, conn: sqlite3.Connection) -> List[str]:
        """Get search suggestions based on partial query"""
        suggestions = []
        
        # Add time-based suggestions
        if 'tod' in partial_query.lower():
            suggestions.append(partial_query + 'ay')
        elif 'yest' in partial_query.lower():
            suggestions.append(partial_query + 'erday')
        
        # Add priority suggestions
        if 'crit' in partial_query.lower():
            suggestions.append(partial_query + 'ical')
        elif 'imp' in partial_query.lower():
            suggestions.append(partial_query + 'ortant')
        
        # Add app suggestions
        for alias in self.app_aliases:
            if alias.startswith(partial_query.lower()):
                suggestions.append(f"from {alias}")
        
        return suggestions[:5]  # Limit to 5 suggestions


# Standalone functions for easy integration
def search_notifications(query: str, db_path: str, limit: int = 50) -> Dict[str, Any]:
    """Search notifications using natural language query"""
    search_engine = EnhancedSearch()
    conn = sqlite3.connect(db_path)
    
    try:
        results = search_engine.search(query, conn, limit)
        return results
    finally:
        conn.close()


def parse_search_query(query: str) -> Dict[str, Any]:
    """Parse a natural language query into search parameters"""
    search_engine = EnhancedSearch()
    return search_engine.parse_natural_language_query(query)
