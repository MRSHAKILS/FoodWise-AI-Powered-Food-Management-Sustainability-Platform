"""
Django-integrated food risk prediction system
Analyzes inventory and consumption patterns from database
"""
from datetime import datetime, timedelta
from collections import defaultdict
from django.utils import timezone


class FoodRiskPredictor:
    """AI-based food expiration risk prediction system integrated with Django models"""
    
    def __init__(self, user):
        self.user = user
        self.current_date = timezone.now().date()
        
        # Category risk weights (higher = faster consumption needed)
        self.category_weights = {
            'meat': 2.0,
            'dairy': 1.8,
            'fruit': 1.6,
            'vegetable': 1.5,
            'grain': 1.0,
            'beverage': 0.9,
            'snack': 0.8,
            'other': 0.7
        }
        
        # Seasonal factors (warm season increases spoilage)
        self.season_factor = self._get_seasonal_factor()
    
    def _get_seasonal_factor(self):
        """Determine seasonal risk factor based on current month"""
        month = self.current_date.month
        # Warm season: March-October (higher risk)
        if 3 <= month <= 10:
            return 1.3  # Items spoil 30% faster
        else:
            return 1.0  # Normal risk
    
    def calculate_consumption_frequency(self):
        """Calculate how frequently each item is consumed from database"""
        from food.models import ConsumptionLog
        
        consumption_freq = defaultdict(lambda: {'count': 0, 'total_quantity': 0, 'last_consumed': None})
        
        logs = ConsumptionLog.objects.filter(user=self.user).order_by('-consumption_date')
        
        for log in logs:
            item_name = log.item_name.lower()
            consumption_freq[item_name]['count'] += 1
            consumption_freq[item_name]['total_quantity'] += float(log.quantity)
            
            if not consumption_freq[item_name]['last_consumed'] or log.consumption_date > consumption_freq[item_name]['last_consumed']:
                consumption_freq[item_name]['last_consumed'] = log.consumption_date
        
        return consumption_freq
    
    def calculate_days_until_expiry(self, item):
        """Calculate days remaining until expiry"""
        if item.expiration_date:
            days_until_expiry = (item.expiration_date - self.current_date).days
            return days_until_expiry
        return None
    
    def calculate_risk_score(self, item, consumption_freq):
        """
        Calculate risk score (0-100) for each item.
        Higher score = Higher risk of spoilage
        """
        item_name = item.name.lower()
        category = item.category
        
        # 1. Days until expiry factor (0-40 points)
        days_left = self.calculate_days_until_expiry(item)
        
        if days_left is None:
            expiry_score = 10  # No expiry date = low baseline risk
        elif days_left <= 0:
            expiry_score = 40
        elif days_left <= 1:
            expiry_score = 35
        elif days_left <= 2:
            expiry_score = 30
        elif days_left <= 3:
            expiry_score = 25
        elif days_left <= 5:
            expiry_score = 20
        elif days_left <= 7:
            expiry_score = 15
        else:
            expiry_score = max(0, 40 - (days_left * 0.5))
        
        # 2. Category risk factor (0-25 points)
        category_score = self.category_weights.get(category, 1.0) * 12.5
        
        # 3. Consumption frequency factor (0-20 points)
        freq_data = consumption_freq.get(item_name, {'count': 0})
        if freq_data['count'] == 0:
            frequency_score = 20  # Never consumed = high risk
        elif freq_data['count'] == 1:
            frequency_score = 15
        elif freq_data['count'] == 2:
            frequency_score = 10
        else:
            frequency_score = max(0, 20 - (freq_data['count'] * 2))
        
        # 4. Seasonal factor (0-15 points)
        seasonal_score = 0
        if category in ['fruit', 'vegetable', 'meat', 'dairy']:
            seasonal_score = (self.season_factor - 1.0) * 50
        
        # Total risk score
        total_risk = expiry_score + category_score + frequency_score + seasonal_score
        total_risk = min(100, max(0, total_risk))
        
        return {
            'total_risk': round(total_risk, 2),
            'days_until_expiry': days_left,
            'expiry_score': round(expiry_score, 2),
            'category_score': round(category_score, 2),
            'frequency_score': round(frequency_score, 2),
            'seasonal_score': round(seasonal_score, 2)
        }
    
    def get_risk_level(self, risk_score):
        """Categorize risk level"""
        if risk_score >= 70:
            return "critical"
        elif risk_score >= 50:
            return "high"
        elif risk_score >= 30:
            return "medium"
        else:
            return "low"
    
    def get_risk_badge_color(self, risk_level):
        """Get Tailwind CSS color classes for risk level"""
        colors = {
            'critical': {
                'bg': 'bg-red-100',
                'text': 'text-red-800',
                'border': 'border-red-300',
                'icon': '🔴'
            },
            'high': {
                'bg': 'bg-orange-100',
                'text': 'text-orange-800',
                'border': 'border-orange-300',
                'icon': '🟠'
            },
            'medium': {
                'bg': 'bg-yellow-100',
                'text': 'text-yellow-800',
                'border': 'border-yellow-300',
                'icon': '🟡'
            },
            'low': {
                'bg': 'bg-green-100',
                'text': 'text-green-800',
                'border': 'border-green-300',
                'icon': '🟢'
            }
        }
        return colors.get(risk_level, colors['low'])
    
    def get_risk_recommendation(self, item, risk_data):
        """Generate actionable recommendation"""
        days_left = risk_data['days_until_expiry']
        risk_level = self.get_risk_level(risk_data['total_risk'])
        
        if risk_level == 'critical':
            if days_left is not None and days_left <= 0:
                return "⚠️ Expired! Discard immediately for safety."
            return "🔥 Use TODAY or discard! Very high spoilage risk."
        elif risk_level == 'high':
            return "⚡ Consume within 1-2 days to prevent waste."
        elif risk_level == 'medium':
            return "📅 Plan to use within this week."
        else:
            return "✅ Fresh! Monitor for changes."
    
    def predict_risks_for_inventory(self):
        """Main prediction function - analyze all user's inventory"""
        from food.models import FoodItem
        
        # Get consumption patterns
        consumption_freq = self.calculate_consumption_frequency()
        
        # Get all inventory items for user
        inventory_items = FoodItem.objects.filter(user=self.user).select_related('user')
        
        risk_items = []
        
        for item in inventory_items:
            risk_data = self.calculate_risk_score(item, consumption_freq)
            risk_level = self.get_risk_level(risk_data['total_risk'])
            risk_colors = self.get_risk_badge_color(risk_level)
            recommendation = self.get_risk_recommendation(item, risk_data)
            
            risk_items.append({
                'item': item,  # Django model instance
                'risk_score': risk_data['total_risk'],
                'risk_level': risk_level,
                'risk_level_display': risk_level.capitalize(),
                'risk_colors': risk_colors,
                'days_until_expiry': risk_data['days_until_expiry'],
                'recommendation': recommendation,
                'breakdown': {
                    'expiry_score': risk_data['expiry_score'],
                    'category_score': risk_data['category_score'],
                    'frequency_score': risk_data['frequency_score'],
                    'seasonal_score': risk_data['seasonal_score']
                }
            })
        
        # Sort by risk score (highest first)
        risk_items.sort(key=lambda x: x['risk_score'], reverse=True)
        
        return risk_items
    
    def get_summary_stats(self, risk_items):
        """Get summary statistics for dashboard"""
        stats = {
            'total_items': len(risk_items),
            'critical': len([x for x in risk_items if x['risk_level'] == 'critical']),
            'high': len([x for x in risk_items if x['risk_level'] == 'high']),
            'medium': len([x for x in risk_items if x['risk_level'] == 'medium']),
            'low': len([x for x in risk_items if x['risk_level'] == 'low']),
            'season_factor': self.season_factor
        }
        return stats
