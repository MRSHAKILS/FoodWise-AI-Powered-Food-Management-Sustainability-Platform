"""
SDG Impact Scoring Engine
Evaluates user progress in waste reduction and nutrition improvement
Uses AI (Gemini) for personalized insights and recommendations
"""

import os
import google.generativeai as genai
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg
from decimal import Decimal


class SDGImpactScorer:
    """
    Calculates Personal SDG Score (0-100) based on:
    - Waste Reduction (40 points)
    - Nutrition Improvement (30 points)
    - Inventory Management (30 points)
    """
    
    def __init__(self, user):
        self.user = user
        self.score_breakdown = {}
        
        # Initialize Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        else:
            self.model = None
    
    def calculate_sdg_score(self):
        """Calculate overall SDG score (0-100)"""
        # Get 30-day period for scoring
        today = timezone.now().date()
        thirty_days_ago = today - timedelta(days=30)
        
        # Calculate component scores
        waste_score = self._calculate_waste_reduction_score(thirty_days_ago, today)
        nutrition_score = self._calculate_nutrition_score(thirty_days_ago, today)
        inventory_score = self._calculate_inventory_management_score()
        
        # Store breakdown
        self.score_breakdown = {
            'waste_reduction': round(waste_score, 1),
            'nutrition': round(nutrition_score, 1),
            'inventory_management': round(inventory_score, 1)
        }
        
        # Calculate total score
        total_score = waste_score + nutrition_score + inventory_score
        
        return round(total_score, 1)
    
    def _calculate_waste_reduction_score(self, start_date, end_date):
        """
        Waste Reduction Score (0-40 points)
        - Items consumed vs wasted ratio
        - Expiring items utilized
        - Consumption logs consistency
        """
        from food.models import ConsumptionLog, FoodItem
        
        score = 0
        
        # Get consumption logs in period
        logs = ConsumptionLog.objects.filter(
            user=self.user,
            consumption_date__gte=start_date,
            consumption_date__lte=end_date
        )
        
        total_logs = logs.count()
        
        # Score based on consumption tracking (0-20 points)
        # More logs = better tracking = less waste
        if total_logs >= 20:
            score += 20
        elif total_logs >= 15:
            score += 16
        elif total_logs >= 10:
            score += 12
        elif total_logs >= 5:
            score += 8
        elif total_logs > 0:
            score += 5
        else:
            score += 0  # No tracking
        
        # Score for consistency in logging (0-10 points)
        logging_days = logs.values('consumption_date').distinct().count()
        days_in_period = (end_date - start_date).days + 1
        if days_in_period > 0:
            consistency = logging_days / days_in_period
            score += consistency * 10
        
        # Score for using expiring items (0-10 points)
        # Check if items expiring soon were consumed
        expiring_items = FoodItem.objects.filter(
            user=self.user,
            expiration_date__gte=start_date,
            expiration_date__lte=start_date + timedelta(days=7),
            quantity=0  # Consumed (quantity reduced to 0)
        ).count()
        
        if expiring_items >= 5:
            score += 10
        elif expiring_items >= 3:
            score += 7
        elif expiring_items >= 1:
            score += 5
        
        return min(score, 40)  # Cap at 40
    
    def _calculate_nutrition_score(self, start_date, end_date):
        """
        Nutrition Score (0-30 points)
        - Meal planning usage
        - Recipe variety
        - Balanced consumption
        """
        from food.models import MealPlan, ConsumptionLog
        
        score = 0
        
        # Score for meal planning (0-15 points)
        meal_plans = MealPlan.objects.filter(
            user=self.user,
            week_start__gte=start_date,
            week_start__lte=end_date
        ).count()
        
        if meal_plans >= 3:
            score += 15
        elif meal_plans >= 2:
            score += 12
        elif meal_plans >= 1:
            score += 10
        else:
            score += 5  # Base score for awareness
        
        # Score for consumption variety (0-15 points)
        # Different categories consumed
        logs = ConsumptionLog.objects.filter(
            user=self.user,
            consumption_date__gte=start_date,
            consumption_date__lte=end_date
        )
        
        unique_categories = logs.values('category').distinct().count()
        
        if unique_categories >= 6:
            score += 15
        elif unique_categories >= 4:
            score += 12
        elif unique_categories >= 2:
            score += 8
        elif unique_categories >= 1:
            score += 5
        
        return min(score, 30)  # Cap at 30
    
    def _calculate_inventory_management_score(self):
        """
        Inventory Management Score (0-30 points)
        - Active inventory tracking
        - Expiration monitoring
        - Stock organization
        """
        from food.models import FoodItem
        
        score = 0
        today = timezone.now().date()
        
        # Score for active inventory (0-15 points)
        active_items = FoodItem.objects.filter(user=self.user, quantity__gt=0).count()
        
        if active_items >= 15:
            score += 15
        elif active_items >= 10:
            score += 12
        elif active_items >= 5:
            score += 10
        elif active_items >= 1:
            score += 7
        
        # Score for proactive expiration management (0-15 points)
        total_inventory = FoodItem.objects.filter(user=self.user).count()
        
        if total_inventory > 0:
            # Items with expiration dates set
            items_with_exp = FoodItem.objects.filter(
                user=self.user,
                expiration_date__isnull=False
            ).count()
            
            exp_ratio = items_with_exp / total_inventory
            score += 10 * exp_ratio
            
            # Check for expired items still in inventory (penalty)
            expired_count = FoodItem.objects.filter(
                user=self.user,
                expiration_date__lt=today,
                quantity__gt=0
            ).count()
            
            if expired_count == 0:
                score += 5  # Bonus for no expired items
            elif expired_count <= 2:
                score += 3
        
        return min(score, 30)  # Cap at 30
    
    def get_weekly_insights(self):
        """Generate weekly insights on improvements"""
        today = timezone.now().date()
        current_week_start = today - timedelta(days=7)
        previous_week_start = today - timedelta(days=14)
        
        # Get scores for both weeks
        current_score = self.calculate_sdg_score()
        
        # Calculate previous week score (simplified)
        prev_waste = self._calculate_waste_reduction_score(previous_week_start, current_week_start)
        prev_nutrition = self._calculate_nutrition_score(previous_week_start, current_week_start)
        prev_inventory = self._calculate_inventory_management_score()
        previous_score = round(prev_waste + prev_nutrition + prev_inventory, 1)
        
        # Calculate improvement
        improvement = current_score - previous_score
        
        insights = {
            'current_score': current_score,
            'previous_score': previous_score,
            'improvement': round(improvement, 1),
            'breakdown': self.score_breakdown,
            'trend': 'improving' if improvement > 0 else 'stable' if improvement == 0 else 'declining'
        }
        
        return insights
    
    def generate_ai_recommendations(self):
        """Generate personalized recommendations using Gemini AI"""
        if not self.model:
            return self._get_fallback_recommendations()
        
        try:
            # Get current score and insights
            score = self.calculate_sdg_score()
            insights = self.get_weekly_insights()
            
            # Get user stats
            from food.models import FoodItem, ConsumptionLog, MealPlan
            
            total_items = FoodItem.objects.filter(user=self.user).count()
            active_items = FoodItem.objects.filter(user=self.user, quantity__gt=0).count()
            meal_plans = MealPlan.objects.filter(user=self.user).count()
            
            today = timezone.now().date()
            week_ago = today - timedelta(days=7)
            recent_logs = ConsumptionLog.objects.filter(
                user=self.user,
                consumption_date__gte=week_ago
            )
            consumed = recent_logs.filter(consumption_type='consumed').count()
            wasted = recent_logs.filter(consumption_type='wasted').count()
            
            # Create prompt for Gemini
            prompt = f"""As a food sustainability advisor, analyze this user's food management data and provide 3 specific, actionable recommendations to improve their SDG Impact Score.

Current Data:
- SDG Score: {score}/100
- Score Breakdown: Waste Reduction: {insights['breakdown']['waste_reduction']}/40, Nutrition: {insights['breakdown']['nutrition']}/30, Inventory: {insights['breakdown']['inventory_management']}/30
- Weekly Trend: {insights['trend']} ({insights['improvement']:+.1f} points)
- Active Inventory Items: {active_items}
- Total Items Tracked: {total_items}
- Meal Plans Created: {meal_plans}
- Last 7 Days: {consumed} items consumed, {wasted} items wasted

Provide exactly 3 recommendations in this format:
1. [Category]: [Specific Action] - Expected Impact: +[X] points
2. [Category]: [Specific Action] - Expected Impact: +[X] points
3. [Category]: [Specific Action] - Expected Impact: +[X] points

Keep each recommendation under 100 characters. Focus on the weakest areas. Be specific and actionable."""

            # Generate with Gemini
            response = self.model.generate_content(prompt)
            recommendations_text = response.text.strip()
            
            # Parse recommendations
            recommendations = []
            lines = recommendations_text.split('\n')
            for line in lines:
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-')):
                    # Clean up the line
                    line = line.lstrip('0123456789.-) ')
                    if line:
                        recommendations.append(line)
            
            # Take first 3
            recommendations = recommendations[:3]
            
            # If parsing failed, use fallback
            if len(recommendations) < 3:
                return self._get_fallback_recommendations()
            
            return {
                'recommendations': recommendations,
                'ai_generated': True
            }
            
        except Exception as e:
            print(f"AI recommendation error: {e}")
            return self._get_fallback_recommendations()
    
    def _get_fallback_recommendations(self):
        """Fallback recommendations based on score breakdown"""
        score = self.calculate_sdg_score()
        breakdown = self.score_breakdown
        
        recommendations = []
        
        # Waste reduction recommendations
        if breakdown['waste_reduction'] < 25:
            recommendations.append(
                "Waste Reduction: Log all food consumption daily to track waste patterns - Expected Impact: +5-10 points"
            )
        
        # Nutrition recommendations
        if breakdown['nutrition'] < 20:
            recommendations.append(
                "Nutrition: Create weekly meal plans to improve dietary balance - Expected Impact: +8-12 points"
            )
        
        # Inventory recommendations
        if breakdown['inventory_management'] < 20:
            recommendations.append(
                "Inventory: Add expiration dates to all items for better tracking - Expected Impact: +5-8 points"
            )
        
        # Generic recommendations if all scores are good
        if len(recommendations) == 0:
            recommendations = [
                "Maintain consistency: Keep logging consumption daily to sustain your excellent score",
                "Expand variety: Try new recipes from different categories to boost nutrition score",
                "Share knowledge: Your waste reduction is excellent - consider sharing tips with others"
            ]
        
        return {
            'recommendations': recommendations[:3],
            'ai_generated': False
        }
    
    def get_sdg_achievement_badges(self):
        """Get achievement badges based on score"""
        score = self.calculate_sdg_score()
        breakdown = self.score_breakdown
        
        badges = []
        
        if score >= 90:
            badges.append({
                'name': 'SDG Champion',
                'icon': '🏆',
                'description': 'Outstanding sustainability performance'
            })
        elif score >= 75:
            badges.append({
                'name': 'Eco Warrior',
                'icon': '⭐',
                'description': 'Excellent progress towards SDG goals'
            })
        elif score >= 60:
            badges.append({
                'name': 'Green Guardian',
                'icon': '🌱',
                'description': 'Good sustainability practices'
            })
        
        if breakdown['waste_reduction'] >= 35:
            badges.append({
                'name': 'Zero Waste Hero',
                'icon': '♻️',
                'description': 'Exceptional waste reduction'
            })
        
        if breakdown['nutrition'] >= 25:
            badges.append({
                'name': 'Nutrition Champion',
                'icon': '🥗',
                'description': 'Excellent meal planning'
            })
        
        if breakdown['inventory_management'] >= 25:
            badges.append({
                'name': 'Organization Master',
                'icon': '📦',
                'description': 'Superior inventory management'
            })
        
        return badges
