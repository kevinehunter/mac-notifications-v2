"""
Integration tests for the notification system
"""

import pytest
import asyncio
from datetime import datetime, timedelta

from mac_notifications.src.mcp_server.server import NotificationMCPServer
from mac_notifications.src.daemon.notification_daemon import NotificationDaemon


class TestEndToEnd:
    """Test complete flow from daemon to MCP server"""
    
    def test_notification_flow(self, populated_db):
        """Test complete notification flow"""
        # Create MCP server
        server = NotificationMCPServer(populated_db)
        
        # Get recent notifications
        result = server.get_recent_notifications(limit=5)
        
        assert 'notifications' in result
        assert 'daemon_status' in result
        assert len(result['notifications']) <= 5
        
        # Check that notifications have expected fields
        if result['notifications']:
            notif = result['notifications'][0]
            assert 'id' in notif
            assert 'app_identifier' in notif
            assert 'delivered_time' in notif
            assert 'priority_score' in notif
            assert 'priority_level' in notif
    
    def test_priority_filtering(self, populated_db):
        """Test priority-based filtering"""
        server = NotificationMCPServer(populated_db)
        
        # Get critical notifications
        result = server.get_recent_notifications(
            limit=10, 
            priority_filter='CRITICAL'
        )
        
        # Check all returned notifications are critical
        for notif in result['notifications']:
            assert notif['priority_level'] == 'CRITICAL'
    
    def test_search_integration(self, populated_db):
        """Test search functionality"""
        server = NotificationMCPServer(populated_db)
        
        # Search for urgent notifications
        result = server.enhanced_search("urgent", limit=10)
        
        assert not result.get('error')
        assert 'notifications' in result
        assert 'parsed_params' in result
    
    def test_grouping_integration(self, populated_db):
        """Test notification grouping"""
        server = NotificationMCPServer(populated_db)
        
        # Get grouped notifications
        result = server.get_grouped_notifications(
            hours=24, 
            time_window=30, 
            min_group_size=2
        )
        
        assert not result.get('error')
        assert 'groups' in result
        assert 'total_notifications' in result
    
    def test_batch_operations(self, populated_db):
        """Test batch operations"""
        server = NotificationMCPServer(populated_db)
        
        # Test marking as read (dry run)
        result = server.batch_mark_read(
            selection_type='priority',
            selection_value='LOW',
            dry_run=True
        )
        
        assert result['success']
        assert 'would_affect' in result or 'affected_count' in result
    
    def test_smart_summary(self, populated_db):
        """Test smart summary generation"""
        server = NotificationMCPServer(populated_db)
        
        # Get hourly digest
        result = server.get_hourly_digest()
        
        assert not result.get('error')
        assert 'summary' in result
        assert 'statistics' in result
        assert 'recommendations' in result
        
        # Check summary content
        assert isinstance(result['summary'], str)
        assert len(result['summary']) > 0
    
    def test_analytics_dashboard(self, populated_db):
        """Test analytics dashboard generation"""
        server = NotificationMCPServer(populated_db)
        
        # Get analytics for last 7 days
        result = server.get_analytics_dashboard(days=7, output_format='json')
        
        assert not result.get('error')
        assert 'metrics' in result
        assert 'hourly_pattern' in result
        assert 'app_analytics' in result
        assert 'productivity' in result
        
        # Check metrics
        metrics = result['metrics']
        assert 'total_notifications' in metrics
        assert 'avg_per_hour' in metrics
        assert metrics['total_notifications'] >= 0


class TestDatabaseIntegration:
    """Test database operations"""
    
    def test_repository_operations(self, db_connection, sample_notifications):
        """Test repository pattern operations"""
        from mac_notifications.src.database.repositories import NotificationRepository
        
        repo = NotificationRepository(db_connection)
        
        # Insert a notification
        notif_data = sample_notifications[0]
        
        # Test get_recent
        recent = repo.get_recent(limit=10)
        assert isinstance(recent, list)
        
        # Test search
        results = repo.search("urgent")
        assert isinstance(results, list)
        
        # Test statistics
        stats = repo.get_statistics()
        assert 'total' in stats
        assert 'by_app' in stats
    
    def test_metadata_repository(self, db_connection):
        """Test daemon metadata operations"""
        from mac_notifications.src.database.repositories import DaemonMetadataRepository
        
        repo = DaemonMetadataRepository(db_connection)
        
        # Set a value
        repo.set('test_key', 'test_value')
        
        # Get the value
        value = repo.get('test_key')
        assert value == 'test_value'
        
        # Update last update time
        repo.update_last_update()
        last_update = repo.get('last_update')
        assert last_update is not None
        
        # Verify it's a recent timestamp
        update_time = datetime.fromisoformat(last_update)
        assert (datetime.now() - update_time).total_seconds() < 5


class TestFeatureIntegration:
    """Test integration of all features"""
    
    def test_priority_scoring_integration(self, populated_db):
        """Test priority scoring is applied to notifications"""
        server = NotificationMCPServer(populated_db)
        
        # Get notifications and check they have priority info
        result = server.get_recent_notifications(limit=10)
        
        for notif in result['notifications']:
            assert 'priority_score' in notif
            assert 'priority_level' in notif
            assert notif['priority_level'] in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
            assert 0 <= notif['priority_score'] <= 100
    
    def test_template_formatting(self, populated_db):
        """Test template formatting works"""
        server = NotificationMCPServer(populated_db)
        
        # Get formatted notifications
        result = server.get_recent_notifications(
            limit=5,
            format_type='terminal',
            use_templates=True
        )
        
        assert 'formatted_output' in result
        assert isinstance(result['formatted_output'], str)
        assert len(result['formatted_output']) > 0
    
    def test_search_and_batch_integration(self, populated_db):
        """Test search results can be used for batch operations"""
        server = NotificationMCPServer(populated_db)
        
        # Search for low priority notifications
        search_result = server.enhanced_search("priority:low", limit=100)
        
        if search_result.get('notifications'):
            # Use search results for batch operation (dry run)
            batch_result = server.batch_mark_read(
                selection_type='search',
                selection_value='priority:low',
                dry_run=True
            )
            
            assert batch_result['success']
            assert 'would_affect' in batch_result or 'affected_count' in batch_result
    
    def test_grouping_and_summary_integration(self, populated_db):
        """Test grouping works with summaries"""
        server = NotificationMCPServer(populated_db)
        
        # Get grouped notifications
        grouped = server.get_grouped_notifications(hours=24)
        
        # Get summary for same period
        summary = server.get_smart_summary(time_range="24h")
        
        # Both should have data about the same notifications
        assert grouped['total_notifications'] == summary['statistics']['total_notifications']


class TestPerformance:
    """Performance tests"""
    
    @pytest.mark.performance
    def test_search_performance(self, populated_db):
        """Test search completes in reasonable time"""
        import time
        server = NotificationMCPServer(populated_db)
        
        start = time.time()
        result = server.enhanced_search("notifications from last week", limit=1000)
        duration = time.time() - start
        
        assert duration < 1.0  # Should complete within 1 second
        assert not result.get('error')
    
    @pytest.mark.performance
    def test_analytics_performance(self, populated_db):
        """Test analytics generation performance"""
        import time
        server = NotificationMCPServer(populated_db)
        
        start = time.time()
        result = server.get_analytics_dashboard(days=30, output_format='json')
        duration = time.time() - start
        
        assert duration < 3.0  # Should complete within 3 seconds
        assert not result.get('error')
    
    @pytest.mark.performance
    def test_batch_operation_performance(self, populated_db):
        """Test batch operations complete efficiently"""
        import time
        server = NotificationMCPServer(populated_db)
        
        start = time.time()
        result = server.batch_mark_read(
            selection_type='older_than',
            selection_value='7d',
            dry_run=True
        )
        duration = time.time() - start
        
        assert duration < 0.5  # Should be very fast for dry run
        assert result['success']