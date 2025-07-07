#!/usr/bin/env python3
"""
Priority Scoring Module
Intelligent priority scoring for notifications based on content, sender, and context
"""

import re
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional
from dataclasses import dataclass
import logging


@dataclass
class ScoringRule:
    """Represents a scoring rule with keywords and weights"""
    keywords: Dict[str, float]
    category: str
    
    def evaluate(self, text: str) -> Tuple[float, Optional[str]]:
        """Evaluate text against keywords and return score and matched keyword"""
        max_score = 0
        matched_keyword = None
        
        for keyword, score in self.keywords.items():
            if keyword in text:
                if score > max_score:
                    max_score = score
                    matched_keyword = keyword
        
        return max_score, matched_keyword


class PriorityScorer:
    """Calculate priority scores for notifications"""
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Define scoring rules by category
        self.rules = {
            'urgency': ScoringRule({
                'critical': 10,
                'urgent': 10,
                'emergency': 10,
                'immediately': 8,
                'asap': 8,
                'now': 7,
                'expire': 8,
                'expiring': 8,
                'deadline': 7,
                'overdue': 8,
                'final notice': 9,
                'last chance': 8,
                'action required': 7,
                'attention required': 7,
                'time sensitive': 8
            }, 'urgency'),
            
            'financial': ScoringRule({
                'payment': 5,
                'charge': 5,
                'transaction': 5,
                'withdraw': 6,
                'withdrawal': 6,
                'deposit': 4,
                'overdrawn': 9,
                'declined': 8,
                'fraud': 10,
                'suspicious': 9,
                'approved': 3,
                'large purchase': 6,
                'refund': 5,
                'balance': 4,
                'overdraft': 9
            }, 'financial'),
            
            'security': ScoringRule({
                'stranger': 8,
                'motion': 3,
                'detected': 4,
                'alert': 6,
                'warning': 7,
                'alarm': 9,
                'break': 9,
                'unauthorized': 9,
                'intruder': 10,
                'breach': 10,
                'locked': 5,
                'unlocked': 6,
                'door': 4,
                'window': 4
            }, 'security'),
            
            'medical': ScoringRule({
                'appointment': 6,
                'visit': 5,
                'medical': 6,
                'doctor': 6,
                'prescription': 7,
                'refill': 7,
                'results': 8,
                'video visit': 8,
                'reminder': 5,
                'health': 5,
                'test': 6,
                'vaccine': 6,
                'medication': 7
            }, 'medical'),
            
            'work': ScoringRule({
                'meeting': 5,
                'deadline': 7,
                'review': 4,
                'approval': 6,
                'expense': 5,
                'report': 4,
                'submitted': 4,
                'onedrive': 7,
                'deletion': 9,
                'project': 5,
                'task': 4,
                'assignment': 5,
                'due': 6
            }, 'work'),
            
            'communication': ScoringRule({
                'call': 4,
                'message': 3,
                'reply': 4,
                'respond': 5,
                'waiting': 4,
                'missed': 5,
                'voicemail': 4,
                'chat': 3
            }, 'communication')
        }
        
        # App priority weights
        self.app_weights = {
            # Financial apps
            'com.apple.passbook': 1.5,
            'com.apple.wallet': 1.5,
            
            # Communication apps
            'com.apple.MobileSMS': 1.3,
            'com.apple.mobilesms': 1.3,
            'com.microsoft.teams': 1.2,
            'com.tinyspeck.slackmacgap': 1.2,
            'com.apple.mail': 1.1,
            'com.microsoft.outlook': 1.1,
            
            # Security apps
            'com.security.batterycam': 1.4,
            'com.ring.ring': 1.4,
            
            # Calendar/Productivity
            'com.apple.iCal': 1.2,
            'com.apple.reminders': 1.2,
            
            # Lower priority apps
            'com.apple.news': 0.7,
            'com.eero.eero-ios': 0.8,
            'com.spotify.client': 0.6,
            
            # Default
            'default': 1.0
        }
        
        # Time-based scoring
        self.time_decay_hours = 24  # Priority decreases over time
        self.recent_boost_hours = 1  # Boost for very recent notifications
    
    def calculate_priority(self, notification: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate priority score for a notification"""
        score = 0.0
        factors = []
        
        # Extract text content
        text = self._extract_text(notification).lower()
        
        # 1. Evaluate all rules
        category_scores = {}
        for category, rule in self.rules.items():
            cat_score, keyword = rule.evaluate(text)
            if cat_score > 0:
                category_scores[category] = cat_score
                factors.append(f"{category}:{keyword}(+{cat_score})")
        
        # Add best score from each category
        if category_scores:
            score += sum(category_scores.values())
        
        # 2. Check for monetary amounts
        money_score, money_factor = self._evaluate_monetary_amounts(text)
        if money_score > 0:
            score += money_score
            factors.append(money_factor)
        
        # 3. Check for dates/times
        date_score, date_factor = self._evaluate_dates(text)
        if date_score > 0:
            score += date_score
            factors.append(date_factor)
        
        # 4. Apply app weight
        app_id = notification.get('app_identifier', '')
        app_weight = self.app_weights.get(app_id, self.app_weights['default'])
        if app_weight != 1.0:
            score *= app_weight
            factors.append(f"app_weight:{app_id}(x{app_weight})")
        
        # 5. Time-based adjustments
        time_score, time_factor = self._evaluate_time_factors(notification)
        if time_score != 1.0:
            score *= time_score
            factors.append(time_factor)
        
        # 6. Special patterns
        special_score, special_factors = self._evaluate_special_patterns(notification, text)
        if special_score > 0:
            score += special_score
            factors.extend(special_factors)
        
        # Round score
        score = round(score, 2)
        
        # Determine priority level
        if score >= 15:
            priority_level = 'CRITICAL'
        elif score >= 10:
            priority_level = 'HIGH'
        elif score >= 5:
            priority_level = 'MEDIUM'
        else:
            priority_level = 'LOW'
        
        return {
            'score': score,
            'level': priority_level,
            'factors': factors
        }
    
    def _extract_text(self, notification: Dict[str, Any]) -> str:
        """Extract all text content from notification"""
        text_parts = []
        for field in ['title', 'subtitle', 'body', 'informative_text']:
            value = notification.get(field, '')
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, (list, tuple)):
                text_parts.append(' '.join(str(v) for v in value))
            elif value:
                text_parts.append(str(value))
        
        return ' '.join(text_parts)
    
    def _evaluate_monetary_amounts(self, text: str) -> Tuple[float, str]:
        """Evaluate monetary amounts in text"""
        money_pattern = r'\$[\d,]+\.?\d*'
        amounts = re.findall(money_pattern, text)
        
        if not amounts:
            return 0, ''
        
        # Find highest amount
        max_amount = 0
        for amount_str in amounts:
            try:
                amount = float(amount_str.replace('$', '').replace(',', ''))
                max_amount = max(max_amount, amount)
            except ValueError:
                continue
        
        # Score based on amount
        if max_amount >= 1000:
            return 8, f"high_amount:${max_amount}(+8)"
        elif max_amount >= 100:
            return 5, f"medium_amount:${max_amount}(+5)"
        elif max_amount > 0:
            return 2, f"amount:${max_amount}(+2)"
        
        return 0, ''
    
    def _evaluate_dates(self, text: str) -> Tuple[float, str]:
        """Evaluate date/time references in text"""
        # Look for today, tomorrow, date patterns
        if 'today' in text:
            return 5, "date:today(+5)"
        elif 'tomorrow' in text:
            return 4, "date:tomorrow(+4)"
        elif 'tonight' in text:
            return 5, "date:tonight(+5)"
        
        # Check for specific times
        time_pattern = r'\b\d{1,2}:\d{2}\s*(?:am|pm|AM|PM)?\b'
        if re.search(time_pattern, text):
            return 3, "specific_time(+3)"
        
        return 0, ''
    
    def _evaluate_time_factors(self, notification: Dict[str, Any]) -> Tuple[float, str]:
        """Evaluate time-based factors"""
        try:
            delivered_str = notification.get('delivered_time', '')
            if isinstance(delivered_str, datetime):
                delivered_time = delivered_str
            else:
                delivered_time = datetime.fromisoformat(delivered_str.replace(' ', 'T'))
            
            hours_old = (datetime.now() - delivered_time).total_seconds() / 3600
            
            # Boost very recent notifications
            if hours_old < self.recent_boost_hours:
                return 1.5, f"very_recent:{hours_old:.1f}h(x1.5)"
            
            # Decay older notifications
            elif hours_old < self.time_decay_hours:
                decay_factor = 1 - (hours_old / self.time_decay_hours) * 0.3
                return decay_factor, f"age:{hours_old:.1f}h(x{decay_factor:.2f})"
            
            # Old notifications
            else:
                return 0.7, f"old:{hours_old:.1f}h(x0.7)"
        
        except Exception as e:
            self.logger.debug(f"Error evaluating time factors: {e}")
            return 1.0, ''
    
    def _evaluate_special_patterns(self, notification: Dict[str, Any], text: str) -> Tuple[float, List[str]]:
        """Evaluate special patterns and conditions"""
        score = 0
        factors = []
        
        # Security alerts at night
        if notification.get('app_identifier') == 'com.security.batterycam':
            if 'stranger' in text or 'motion' in text:
                try:
                    delivered_str = notification.get('delivered_time', '')
                    if isinstance(delivered_str, datetime):
                        hour = delivered_str.hour
                    else:
                        hour = datetime.fromisoformat(delivered_str.replace(' ', 'T')).hour
                    
                    if hour < 6 or hour > 22:  # Night time
                        score += 5
                        factors.append("security_night(+5)")
                except:
                    pass
        
        # Multiple exclamation marks or all caps
        if '!!!' in text or text.isupper():
            score += 2
            factors.append("emphasis(+2)")
        
        # Questions requiring response
        if '?' in text and any(word in text for word in ['confirm', 'verify', 'approve', 'reply']):
            score += 3
            factors.append("question_response(+3)")
        
        return score, factors
    
    def score_notifications(self, notifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Score a list of notifications and sort by priority"""
        scored = []
        
        for notif in notifications:
            priority_info = self.calculate_priority(notif)
            notif_copy = notif.copy()
            notif_copy['priority_score'] = priority_info['score']
            notif_copy['priority_level'] = priority_info['level']
            notif_copy['priority_factors'] = priority_info['factors']
            scored.append(notif_copy)
        
        # Sort by priority score (highest first)
        scored.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        return scored


# Convenience functions for backward compatibility
def calculate_notification_priority(notification: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate priority for a single notification"""
    scorer = PriorityScorer()
    return scorer.calculate_priority(notification)


def add_priority_to_notifications(notifications: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Add priority scoring to a list of notifications"""
    scorer = PriorityScorer()
    return scorer.score_notifications(notifications)