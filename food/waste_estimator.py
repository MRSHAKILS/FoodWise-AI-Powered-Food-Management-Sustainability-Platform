"""
AI Waste Estimation Model
Estimates wasted grams, money lost, and provides projections
"""
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Avg, Count
from collections import defaultdict


class WasteEstimator:
    """AI-based waste estimation and projection system"""
    
    # Community average data (dummy dataset for comparison)
    COMMUNITY_AVERAGES = {
        'weekly_waste_grams': 2500,  # 2.5 kg per week average
        'weekly_waste_money': 35.00,  # $35 per week average
        'monthly_waste_grams': 10000,  # 10 kg per month average
        'monthly_waste_money': 140.00,  # $140 per month average
        'waste_by_category': {
            'vegetable': 850,
            'fruit': 750,
            'dairy': 500,
            'meat': 400,
            'grain': 200,
            'beverage': 150,
            'snack': 100,
            'other': 50
        }
    }
    
    # Average grams per unit for different items (estimation)
    UNIT_TO_GRAMS = {
        'kg': 1000,
        'g': 1,
        'liter': 1000,  # Approximate
        'ml': 1,
        'units': 250,  # Average item ~250g
        'piece': 200,
        'dozen': 600,  # ~50g per egg
        'loaf': 400,
        'bunch': 300,
    }
    
    def __init__(self, user):
        self.user = user
        self.current_date = timezone.now().date()
    
    def estimate_grams(self, quantity, unit):
        """Convert quantity to grams estimation"""
        unit_lower = unit.lower()
        grams_per_unit = self.UNIT_TO_GRAMS.get(unit_lower, 250)  # Default 250g
        return float(quantity) * grams_per_unit
    
    def calculate_actual_waste(self, days=30):
        """
        Calculate actual waste from expired/deleted items
        Returns waste in grams and money
        """
        from food.models import FoodItem, ConsumptionLog
        
        # Get items that expired in the period
        start_date = self.current_date - timedelta(days=days)
        
        # Find items with expired dates that were likely wasted
        expired_items = FoodItem.objects.filter(
            user=self.user,
            expiration_date__lt=self.current_date,
            expiration_date__gte=start_date
        )
        
        total_waste_grams = 0
        total_money_lost = 0
        waste_by_category = defaultdict(lambda: {'grams': 0, 'money': 0, 'count': 0})
        
        for item in expired_items:
            grams = self.estimate_grams(item.quantity, item.unit)
            money = float(item.price) if item.price else 0
            
            total_waste_grams += grams
            total_money_lost += money
            
            waste_by_category[item.category]['grams'] += grams
            waste_by_category[item.category]['money'] += money
            waste_by_category[item.category]['count'] += 1
        
        return {
            'total_grams': round(total_waste_grams, 2),
            'total_money': round(total_money_lost, 2),
            'by_category': dict(waste_by_category),
            'period_days': days
        }
    
    def predict_waste_projection(self, risk_items):
        """
        Predict future waste based on current risk scores
        Returns weekly and monthly projections
        """
        weekly_waste_grams = 0
        weekly_waste_money = 0
        monthly_waste_grams = 0
        monthly_waste_money = 0
        
        projected_by_category = defaultdict(lambda: {'weekly_grams': 0, 'monthly_grams': 0, 'weekly_money': 0, 'monthly_money': 0})
        
        for risk_item in risk_items:
            item = risk_item['item']
            risk_score = risk_item['risk_score']
            
            # Waste probability based on risk score
            waste_probability = risk_score / 100.0
            
            # Estimate grams
            grams = self.estimate_grams(item.quantity, item.unit)
            money = float(item.price) if item.price else 0
            
            # Project waste
            projected_waste_grams = grams * waste_probability
            projected_waste_money = money * waste_probability
            
            # Determine if likely to waste this week or month
            days_left = risk_item.get('days_until_expiry')
            
            if days_left is not None:
                if days_left <= 7:  # Will likely waste this week
                    weekly_waste_grams += projected_waste_grams
                    weekly_waste_money += projected_waste_money
                    projected_by_category[item.category]['weekly_grams'] += projected_waste_grams
                    projected_by_category[item.category]['weekly_money'] += projected_waste_money
                
                if days_left <= 30:  # Will likely waste this month
                    monthly_waste_grams += projected_waste_grams
                    monthly_waste_money += projected_waste_money
                    projected_by_category[item.category]['monthly_grams'] += projected_waste_grams
                    projected_by_category[item.category]['monthly_money'] += projected_waste_money
        
        return {
            'weekly': {
                'grams': round(weekly_waste_grams, 2),
                'money': round(weekly_waste_money, 2),
                'by_category': {k: {'grams': round(v['weekly_grams'], 2), 'money': round(v['weekly_money'], 2)} 
                               for k, v in projected_by_category.items()}
            },
            'monthly': {
                'grams': round(monthly_waste_grams, 2),
                'money': round(monthly_waste_money, 2),
                'by_category': {k: {'grams': round(v['monthly_grams'], 2), 'money': round(v['monthly_money'], 2)} 
                               for k, v in projected_by_category.items()}
            }
        }
    
    def compare_to_community(self, user_waste_data, projections):
        """
        Compare user's waste to community averages
        Returns comparison percentages and insights
        """
        weekly_user = projections['weekly']['money']
        monthly_user = projections['monthly']['money']
        
        weekly_community = self.COMMUNITY_AVERAGES['weekly_waste_money']
        monthly_community = self.COMMUNITY_AVERAGES['monthly_waste_money']
        
        weekly_diff_percent = ((weekly_user - weekly_community) / weekly_community * 100) if weekly_community > 0 else 0
        monthly_diff_percent = ((monthly_user - monthly_community) / monthly_community * 100) if monthly_community > 0 else 0
        
        # Determine performance level
        if weekly_diff_percent < -30:
            performance = "excellent"
            message = "🌟 Outstanding! You're wasting significantly less than average."
        elif weekly_diff_percent < -10:
            performance = "good"
            message = "👍 Great job! You're below community average."
        elif weekly_diff_percent < 10:
            performance = "average"
            message = "📊 You're around the community average."
        elif weekly_diff_percent < 30:
            performance = "needs_improvement"
            message = "⚠️ You're wasting more than average. Try our recommendations!"
        else:
            performance = "critical"
            message = "🚨 Significant waste detected. Immediate action needed!"
        
        return {
            'weekly': {
                'user': weekly_user,
                'community': weekly_community,
                'difference_percent': round(weekly_diff_percent, 1),
                'difference_amount': round(weekly_user - weekly_community, 2)
            },
            'monthly': {
                'user': monthly_user,
                'community': monthly_community,
                'difference_percent': round(monthly_diff_percent, 1),
                'difference_amount': round(monthly_user - monthly_community, 2)
            },
            'performance': performance,
            'message': message,
            'savings_potential': round(max(0, weekly_user - weekly_community) * 52, 2)  # Annual savings if improved
        }
    
    def generate_waste_report(self, risk_items):
        """
        Generate comprehensive waste estimation report
        Combines actual waste, projections, and community comparison
        """
        # Calculate actual waste (last 30 days)
        actual_waste_30d = self.calculate_actual_waste(days=30)
        actual_waste_7d = self.calculate_actual_waste(days=7)
        
        # Predict future waste
        projections = self.predict_waste_projection(risk_items)
        
        # Compare to community
        comparison = self.compare_to_community(actual_waste_30d, projections)
        
        # Calculate waste reduction tips value
        potential_monthly_savings = 0
        for risk_item in risk_items:
            if risk_item['risk_score'] >= 50:  # High/Critical risk
                item = risk_item['item']
                if item.price:
                    potential_monthly_savings += float(item.price)
        
        return {
            'actual_waste': {
                'last_7_days': actual_waste_7d,
                'last_30_days': actual_waste_30d
            },
            'projections': projections,
            'community_comparison': comparison,
            'insights': {
                'total_at_risk_items': len([x for x in risk_items if x['risk_score'] >= 50]),
                'potential_monthly_savings': round(potential_monthly_savings, 2),
                'waste_trend': self._calculate_waste_trend()
            },
            'recommendations': self._generate_waste_recommendations(risk_items, projections)
        }
    
    def _calculate_waste_trend(self):
        """Calculate if waste is increasing or decreasing"""
        # Compare last 7 days vs previous 7 days
        current_week = self.calculate_actual_waste(days=7)
        previous_week_start = self.current_date - timedelta(days=14)
        previous_week_end = self.current_date - timedelta(days=7)
        
        from food.models import FoodItem
        
        prev_expired = FoodItem.objects.filter(
            user=self.user,
            expiration_date__lt=previous_week_end,
            expiration_date__gte=previous_week_start
        )
        
        prev_waste_money = sum(float(item.price or 0) for item in prev_expired)
        current_waste_money = current_week['total_money']
        
        if prev_waste_money == 0:
            return "stable"
        
        change_percent = ((current_waste_money - prev_waste_money) / prev_waste_money * 100)
        
        if change_percent < -10:
            return "improving"
        elif change_percent > 10:
            return "worsening"
        else:
            return "stable"
    
    def _generate_waste_recommendations(self, risk_items, projections):
        """Generate actionable recommendations to reduce waste"""
        recommendations = []
        
        # High risk items
        high_risk_count = len([x for x in risk_items if x['risk_score'] >= 70])
        if high_risk_count > 0:
            recommendations.append({
                'priority': 'high',
                'action': f"Consume or freeze {high_risk_count} critical items immediately",
                'impact': 'Prevent immediate waste'
            })
        
        # Category-specific recommendations
        weekly_proj = projections['weekly']['by_category']
        if weekly_proj:
            worst_category = max(weekly_proj.items(), key=lambda x: x[1]['money'])
            recommendations.append({
                'priority': 'medium',
                'action': f"Focus on {worst_category[0]} items - highest projected waste",
                'impact': f"Save ${worst_category[1]['money']:.2f} this week"
            })
        
        # Shopping behavior
        if projections['weekly']['money'] > 20:
            recommendations.append({
                'priority': 'medium',
                'action': "Buy smaller quantities or shop more frequently",
                'impact': 'Reduce over-purchasing'
            })
        
        return recommendations
