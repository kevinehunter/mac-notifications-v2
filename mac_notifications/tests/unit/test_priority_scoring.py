"""
Test Priority Scoring Feature
"""

import pytest
import json
from datetime import datetime, timedelta

from mac_notifications.src.features.priority_scoring import PriorityScorer, calculate_priority_score
from mac_notifications.src.database.models import Notification


class TestPriorityScoring:
    """Test priority scoring functionality"""
    
    def test_urgent_keywords(self):
        """Test that urgent keywords increase priority"""
        scorer = PriorityScorer()
        
        # Test urgent notification
        urgent_notif = {
            "title": "URGENT: Action Required",
            "body": "Please respond immediately to this request",
            "app_identifier": "com.microsoft.outlook",
            "delivered_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        score, level, factors = calculate_priority_score(urgent_notif)
        
        assert score > 70  # Should be high priority
        assert level in ["CRITICAL", "HIGH"]
        assert any("urgent" in f.lower() for f in factors)
    
    def test_financial_notifications(self):
        """Test financial notification scoring"""
        scorer = PriorityScorer()
        
        # Test fraud alert
        fraud_notif = {
            "title": "Fraud Alert",
            "body": "Suspicious transaction detected on your account",
            "app_identifier": "com.apple.passbook",
            "delivered_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        score, level, factors = calculate_priority_score(fraud_notif)
        
        assert score >= 80  # Should be very high priority
        assert level == "CRITICAL"
        assert "financial_app" in factors
        assert any("fraud" in f.lower() for f in factors)
    
    def test_security_camera_stranger(self):
        """Test security camera stranger detection"""
        scorer = PriorityScorer()
        
        # Test stranger detection
        stranger_notif = {
            "title": "",
            "body": "Garage AI #1: Stranger has been detected.",
            "app_identifier": "com.security.batterycam",
            "delivered_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        score, level, factors = calculate_priority_score(stranger_notif)
        
        assert score >= 85  # Stranger detection should be critical
        assert level == "CRITICAL"
        assert "security_stranger" in factors
    
    def test_security_camera_routine(self):
        """Test routine security camera notifications"""
        scorer = PriorityScorer()
        
        # Test vehicle detection
        vehicle_notif = {
            "title": "Motion Detected",
            "body": "Backyard: Vehicle detected",
            "app_identifier": "com.security.batterycam",
            "delivered_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        score, level, factors = calculate_priority_score(vehicle_notif)
        
        assert score < 50  # Routine motion should be low priority
        assert level == "LOW"
        assert "security_camera" in factors
    
    def test_medical_notifications(self):
        """Test medical/health notifications"""
        scorer = PriorityScorer()
        
        # Test video visit
        medical_notif = {
            "title": "You may now join your video visit",
            "subtitle": "MyChart@healthmychart.org",
            "body": "Join your video visit: https://ucsdhealth.well.app/F3liAg",
            "app_identifier": "com.apple.mobilesms",
            "delivered_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        score, level, factors = calculate_priority_score(medical_notif)
        
        assert score >= 70  # Medical appointments should be high priority
        assert level in ["CRITICAL", "HIGH"]
        assert any("medical" in f.lower() or "video visit" in f.lower() for f in factors)
    
    def test_time_decay(self):
        """Test that older notifications get lower scores"""
        scorer = PriorityScorer()
        
        # Same notification at different times
        base_notif = {
            "title": "Important Message",
            "body": "This is an important message",
            "app_identifier": "com.apple.mail"
        }
        
        # Recent notification
        recent_notif = base_notif.copy()
        recent_notif["delivered_time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        recent_score, _, _ = calculate_priority_score(recent_notif)
        
        # Old notification (2 days ago)
        old_notif = base_notif.copy()
        old_notif["delivered_time"] = (datetime.now() - timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S')
        old_score, _, _ = calculate_priority_score(old_notif)
        
        assert recent_score > old_score  # Recent should score higher
        assert old_score < recent_score * 0.7  # Significant decay after 2 days
    
    def test_night_time_boost(self):
        """Test that night-time notifications get priority boost"""
        scorer = PriorityScorer()
        
        # Security notification at 3 AM
        night_time = datetime.now().replace(hour=3, minute=0, second=0)
        night_notif = {
            "title": "Motion Detected",
            "body": "Front Door: Motion detected",
            "app_identifier": "com.security.batterycam",
            "delivered_time": night_time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        score, level, factors = calculate_priority_score(night_notif)
        
        assert "night_time_activity" in factors
        # Night-time security should be elevated
        assert level in ["HIGH", "MEDIUM"]
    
    def test_combined_factors(self):
        """Test notifications with multiple priority factors"""
        scorer = PriorityScorer()
        
        # Urgent financial notification
        combined_notif = {
            "title": "URGENT: Your payment failed",
            "body": "Your payment of $5,000 failed. Immediate action required to avoid service interruption.",
            "app_identifier": "com.apple.passbook",
            "delivered_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        score, level, factors = calculate_priority_score(combined_notif)
        
        assert score >= 90  # Multiple factors should push score very high
        assert level == "CRITICAL"
        assert "financial_app" in factors
        assert any("urgent" in f.lower() for f in factors)
        assert any("large_amount" in f.lower() for f in factors)
    
    def test_notification_model_integration(self):
        """Test priority scoring with Notification model"""
        # Create a notification object
        notif = Notification(
            rec_id=1,
            app_identifier="com.microsoft.teams",
            delivered_time=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            title="Meeting Starting Now",
            body="Your team standup is starting"
        )
        
        # Calculate priority
        notif.calculate_priority()
        
        assert notif.priority_score > 0
        assert notif.priority_level in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
        assert isinstance(notif.priority_factors, list)
        assert len(notif.priority_factors) > 0


class TestPriorityPatterns:
    """Test specific notification patterns"""
    
    def test_onedrive_deletion_warning(self):
        """Test OneDrive deletion warnings get critical priority"""
        notif = {
            "title": "Your OneDrive will be deleted",
            "body": "Final notice: Your OneDrive account will be deleted in 7 days.",
            "app_identifier": "com.microsoft.outlook",
            "delivered_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        score, level, factors = calculate_priority_score(notif)
        
        assert level == "CRITICAL"
        assert "onedrive_deletion" in factors
    
    def test_meeting_notifications(self):
        """Test meeting notifications get appropriate priority"""
        # Meeting starting now
        now_meeting = {
            "title": "Meeting Starting",
            "body": "Your meeting is starting now",
            "app_identifier": "com.microsoft.teams",
            "delivered_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        score1, level1, _ = calculate_priority_score(now_meeting)
        
        # Meeting in 15 minutes
        future_meeting = {
            "title": "Meeting Reminder",
            "body": "Your meeting starts in 15 minutes",
            "app_identifier": "com.microsoft.teams",
            "delivered_time": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        score2, level2, _ = calculate_priority_score(future_meeting)
        
        assert level1 in ["CRITICAL", "HIGH"]
        assert level2 in ["HIGH", "MEDIUM"]
        assert score1 > score2  # "Now" should be higher than "in 15 minutes"
    
    def test_app_specific_scoring(self):
        """Test that different apps get different base scores"""
        message = "Test notification"
        delivered_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Financial app
        financial = {
            "title": message,
            "app_identifier": "com.apple.passbook",
            "delivered_time": delivered_time
        }
        
        # Social app
        social = {
            "title": message,
            "app_identifier": "com.twitter.app",
            "delivered_time": delivered_time
        }
        
        # Work app
        work = {
            "title": message,
            "app_identifier": "com.microsoft.teams",
            "delivered_time": delivered_time
        }
        
        score_fin, _, _ = calculate_priority_score(financial)
        score_soc, _, _ = calculate_priority_score(social)
        score_work, _, _ = calculate_priority_score(work)
        
        # Financial and work apps should score higher than social
        assert score_fin > score_soc
        assert score_work > score_soc
