"""
Test Enhanced Search Feature
"""

import pytest
from datetime import datetime, timedelta

from mac_notifications.src.features.enhanced_search import EnhancedSearch, parse_search_query


class TestEnhancedSearch:
    """Test enhanced search functionality"""
    
    def test_parse_natural_language_query(self):
        """Test natural language query parsing"""
        search = EnhancedSearch()
        
        # Test time-based query
        params = search.parse_natural_language_query("notifications from today")
        assert params['time_range'] is not None
        assert params['time_range'][0].date() == datetime.now().date()
        
        # Test app-based query
        params = search.parse_natural_language_query("messages from teams")
        assert 'com.microsoft.teams' in params['apps']
        
        # Test priority query
        params = search.parse_natural_language_query("critical notifications")
        assert params['priority_filter'] == 'CRITICAL'
        
        # Test exclusion query
        params = search.parse_natural_language_query("security alerts but not vehicles")
        assert 'vehicle' in params['exclude_keywords']
        
        # Test combined query
        params = search.parse_natural_language_query("important messages from yesterday")
        assert params['priority_filter'] == 'important'
        assert params['time_range'] is not None
    
    def test_security_camera_shortcuts(self):
        """Test security camera specific shortcuts"""
        search = EnhancedSearch()
        
        # Test stranger detection shortcut
        params = search.parse_natural_language_query("strangers")
        assert 'stranger' in params['keywords']
        assert 'com.security.batterycam' in params['apps']
        
        # Test security without vehicles
        params = search.parse_natural_language_query("security alerts no vehicles")
        assert 'com.security.batterycam' in params['apps']
        assert 'vehicle' in params['exclude_keywords']
    
    def test_time_range_parsing(self):
        """Test various time range formats"""
        search = EnhancedSearch()
        
        # Test relative times
        test_cases = [
            ("last week", 7),
            ("this week", 7),
            ("yesterday", 1),
            ("last month", 30),
        ]
        
        for query, expected_days in test_cases:
            params = search.parse_natural_language_query(f"notifications from {query}")
            assert params['time_range'] is not None
            start, end = params['time_range']
            # Check that time range is approximately correct
            duration = (end - start).days
            assert abs(duration - expected_days) <= 1
    
    def test_app_aliases(self):
        """Test app name aliases"""
        search = EnhancedSearch()
        
        # Test various app aliases
        test_cases = [
            ("messages", ["com.apple.mobilesms", "com.apple.messages"]),
            ("mail", ["com.apple.mail"]),
            ("teams", ["com.microsoft.teams", "com.microsoft.teams2"]),
            ("security camera", ["com.security.batterycam"]),
            ("wallet", ["com.apple.passbook"]),
        ]
        
        for alias, expected_apps in test_cases:
            params = search.parse_natural_language_query(f"from {alias}")
            assert any(app in params['apps'] for app in expected_apps)
    
    def test_keyword_extraction(self):
        """Test keyword extraction from queries"""
        search = EnhancedSearch()
        
        # Test with stop words removed
        params = search.parse_natural_language_query("show me all the notifications about meetings")
        assert "meetings" in params['keywords']
        assert "show" not in params['keywords']
        assert "the" not in params['keywords']
        
        # Test with multiple keywords
        params = search.parse_natural_language_query("payment invoice deadline")
        assert all(word in params['keywords'] for word in ["payment", "invoice", "deadline"])
    
    def test_regex_pattern_extraction(self):
        """Test regex pattern extraction"""
        search = EnhancedSearch()
        
        # Test regex pattern
        params = search.parse_natural_language_query("notifications matching /error.*critical/")
        assert params['regex_pattern'] == 'error.*critical'
        
        # Test that regex is removed from keywords
        assert not any('error' in kw for kw in params['keywords'])
    
    def test_search_with_database(self, populated_db):
        """Test actual search execution with database"""
        search = EnhancedSearch()
        
        import sqlite3
        conn = sqlite3.connect(populated_db)
        
        # Search for urgent notifications
        results = search.search("urgent", conn, limit=10)
        assert 'notifications' in results
        assert 'total_found' in results
        assert 'parsed_params' in results
        
        # Check that urgent notifications are found
        urgent_found = False
        for notif in results['notifications']:
            if 'urgent' in str(notif).lower():
                urgent_found = True
                break
        assert urgent_found
        
        conn.close()
    
    def test_search_by_app(self, populated_db):
        """Test searching by app"""
        search = EnhancedSearch()
        
        import sqlite3
        conn = sqlite3.connect(populated_db)
        
        # Search for mail notifications
        results = search.search("from mail", conn, limit=10)
        
        # Check that only mail notifications are returned
        for notif in results['notifications']:
            assert 'mail' in notif['app_identifier'].lower()
        
        conn.close()
    
    def test_search_with_time_filter(self, populated_db):
        """Test searching with time filters"""
        search = EnhancedSearch()
        
        import sqlite3
        conn = sqlite3.connect(populated_db)
        
        # Search for recent notifications
        results = search.search("notifications from last 2 hours", conn, limit=10)
        
        # Check that results are recent
        two_hours_ago = datetime.now() - timedelta(hours=2)
        for notif in results['notifications']:
            delivered_time = datetime.strptime(notif['delivered_time'], '%Y-%m-%d %H:%M:%S')
            assert delivered_time >= two_hours_ago
        
        conn.close()
    
    def test_search_with_priority_filter(self, populated_db):
        """Test searching with priority filters"""
        search = EnhancedSearch()
        
        import sqlite3
        conn = sqlite3.connect(populated_db)
        
        # Search for critical notifications
        results = search.search("critical notifications", conn, limit=10)
        
        # Check that results are critical priority
        for notif in results['notifications']:
            assert notif.get('priority_level') == 'CRITICAL'
        
        conn.close()
    
    def test_search_with_exclusions(self, populated_db):
        """Test searching with exclusions"""
        search = EnhancedSearch()
        
        import sqlite3
        conn = sqlite3.connect(populated_db)
        
        # Search excluding certain keywords
        results = search.search("notifications but not motion", conn, limit=50)
        
        # Check that excluded terms are not in results
        for notif in results['notifications']:
            text = f"{notif.get('title', '')} {notif.get('body', '')}".lower()
            assert 'motion' not in text
        
        conn.close()
    
    def test_search_grouping(self, populated_db):
        """Test search results grouping"""
        search = EnhancedSearch()
        
        import sqlite3
        conn = sqlite3.connect(populated_db)
        
        # Search with grouping by app
        results = search.search("all notifications group by app", conn, limit=100)
        
        assert 'groups' in results
        assert results['grouped_by'] == 'app'
        
        # Check that groups are properly formed
        for group_key, group_data in results['groups'].items():
            assert 'count' in group_data
            assert 'notifications' in group_data
            assert 'priority_breakdown' in group_data
        
        conn.close()


class TestSearchSuggestions:
    """Test search suggestion functionality"""
    
    def test_time_suggestions(self):
        """Test time-based search suggestions"""
        search = EnhancedSearch()
        
        suggestions = search.get_search_suggestions("tod", None)
        assert any("today" in s for s in suggestions)
        
        suggestions = search.get_search_suggestions("yest", None)
        assert any("yesterday" in s for s in suggestions)
    
    def test_priority_suggestions(self):
        """Test priority-based search suggestions"""
        search = EnhancedSearch()
        
        suggestions = search.get_search_suggestions("crit", None)
        assert any("critical" in s for s in suggestions)
        
        suggestions = search.get_search_suggestions("imp", None)
        assert any("important" in s for s in suggestions)
    
    def test_app_suggestions(self):
        """Test app-based search suggestions"""
        search = EnhancedSearch()
        
        suggestions = search.get_search_suggestions("mess", None)
        assert any("messages" in s.lower() for s in suggestions)
        
        suggestions = search.get_search_suggestions("tea", None)
        assert any("teams" in s.lower() for s in suggestions)
