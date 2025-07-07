"""
Unit tests for feature modules
"""

import unittest
from datetime import datetime
from typing import Dict, Any

from mac_notifications.src.features.priority_scoring import PriorityScorer
from mac_notifications.src.features.templates import NotificationTemplates


class TestPriorityScoring(unittest.TestCase):
    """Test priority scoring feature"""
    
    def setUp(self):
        self.scorer = PriorityScorer()
    
    def test_scoring_rules(self):
        """Test that scoring rules are applied correctly"""
        # Test urgency rule
        notification = {
            'app_identifier': 'com.test',
            'delivered_time': datetime.now().isoformat(),
            'title': 'URGENT: Server down',
            'body': 'The production server is not responding'
        }
        
        result = self.scorer.calculate_priority(notification)
        
        self.assertGreater(result['score'], 10)
        self.assertEqual(result['level'], 'CRITICAL')
        self.assertTrue(any('urgency:urgent' in f for f in result['factors']))
    
    def test_financial_keywords(self):
        """Test financial keyword detection"""
        notification = {
            'app_identifier': 'com.apple.wallet',
            'delivered_time': datetime.now().isoformat(),
            'title': 'Payment Declined',
            'body': 'Your payment of $1,500 was declined due to insufficient funds'
        }
        
        result = self.scorer.calculate_priority(notification)
        
        self.assertTrue(any('financial:' in f for f in result['factors']))
        self.assertTrue(any('declined' in f for f in result['factors']))
        self.assertTrue(any('$1500' in str(result['factors']) for f in result['factors']))
    
    def test_time_decay(self):
        """Test that older notifications get lower scores"""
        from datetime import timedelta
        
        # Recent notification
        recent = {
            'app_identifier': 'com.test',
            'delivered_time': datetime.now().isoformat(),
            'title': 'Test',
            'body': 'Test message'
        }
        
        # Old notification (2 days old)
        old_time = (datetime.now() - timedelta(days=2)).isoformat()
        old = {
            'app_identifier': 'com.test',
            'delivered_time': old_time,
            'title': 'Test',
            'body': 'Test message'
        }
        
        recent_score = self.scorer.calculate_priority(recent)['score']
        old_score = self.scorer.calculate_priority(old)['score']
        
        self.assertGreater(recent_score, old_score)


class TestNotificationTemplates(unittest.TestCase):
    """Test notification templates"""
    
    def setUp(self):
        self.templates = NotificationTemplates()
    
    def test_terminal_formatting(self):
        """Test terminal output formatting"""
        notification = {
            'app_identifier': 'com.apple.mail',
            'delivered_time': '2024-01-01 10:00:00',
            'title': 'New Email',
            'subtitle': 'From John Doe',
            'body': 'Hello, this is a test email',
            'priority_level': 'HIGH',
            'priority_score': 12.5,
            'priority_factors': ['urgency:urgent(+10)', 'app_weight:com.apple.mail(x1.1)']
        }
        
        # Test with color
        output_color = self.templates.format_notification(notification, use_color=True, format_type='terminal')
        self.assertIn('New Email', output_color)
        self.assertIn('\033[', output_color)  # Contains ANSI codes
        
        # Test without color
        output_plain = self.templates.format_notification(notification, use_color=False, format_type='terminal')
        self.assertIn('New Email', output_plain)
        self.assertNotIn('\033[', output_plain)  # No ANSI codes
    
    def test_html_formatting(self):
        """Test HTML output formatting"""
        notification = {
            'app_identifier': 'com.apple.wallet',
            'delivered_time': '2024-01-01 10:00:00',
            'title': 'Payment Processed',
            'subtitle': '$50.00',
            'body': 'Your payment has been completed successfully',
            'priority_level': 'MEDIUM',
            'priority_score': 7.5,
            'priority_factors': ['financial:payment(+5)']
        }
        
        output = self.templates.format_notification(notification, format_type='html')
        
        self.assertIn('<div', output)
        self.assertIn('Payment Processed', output)
        self.assertIn('$50.00', output)
        self.assertIn('#17a2b8', output)  # Medium priority color
    
    def test_markdown_formatting(self):
        """Test Markdown output formatting"""
        notification = {
            'app_identifier': 'com.security.camera',
            'delivered_time': '2024-01-01 03:00:00',
            'title': 'Motion Detected',
            'body': 'Motion detected at front door',
            'priority_level': 'CRITICAL',
            'priority_score': 18.0,
            'priority_factors': ['security:motion(+3)', 'security_night(+5)']
        }
        
        output = self.templates.format_notification(notification, format_type='markdown')
        
        self.assertIn('###', output)  # Markdown header
        self.assertIn('🔴', output)  # Critical marker
        self.assertIn('**', output)  # Bold text
        self.assertIn('Motion Detected', output)
    
    def test_category_detection(self):
        """Test category detection from factors"""
        # Financial category
        notif1 = {
            'priority_factors': ['financial:payment(+5)', 'amount:$100(+2)']
        }
        category1 = self.templates._determine_category(notif1)
        self.assertEqual(category1, 'financial')
        
        # Security category
        notif2 = {
            'priority_factors': ['security:motion(+3)', 'security_night(+5)']
        }
        category2 = self.templates._determine_category(notif2)
        self.assertEqual(category2, 'security')
        
        # App-based detection
        notif3 = {
            'app_identifier': 'com.microsoft.teams',
            'priority_factors': []
        }
        category3 = self.templates._determine_category(notif3)
        self.assertEqual(category3, 'work')
    
    def test_notification_list_formatting(self):
        """Test formatting multiple notifications"""
        notifications = [
            {
                'app_identifier': 'com.apple.mail',
                'delivered_time': '2024-01-01 10:00:00',
                'title': 'Email 1',
                'priority_level': 'HIGH',
                'priority_score': 12.0
            },
            {
                'app_identifier': 'com.apple.messages',
                'delivered_time': '2024-01-01 11:00:00',
                'title': 'Message 1',
                'priority_level': 'MEDIUM',
                'priority_score': 8.0
            }
        ]
        
        # Terminal format
        terminal_output = self.templates.format_notification_list(notifications, 'terminal')
        self.assertIn('Email 1', terminal_output)
        self.assertIn('Message 1', terminal_output)
        
        # HTML format
        html_output = self.templates.format_notification_list(notifications, 'html')
        self.assertIn('<html>', html_output)
        self.assertIn('Total: 2 notifications', html_output)
        
        # Markdown format
        md_output = self.templates.format_notification_list(notifications, 'markdown')
        self.assertIn('# 📬 Notifications', md_output)
        self.assertIn('**Total:** 2 notifications', md_output)


if __name__ == '__main__':
    unittest.main()