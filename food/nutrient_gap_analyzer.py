"""
Nutrient Gap Prediction Engine
Analyzes user consumption history and predicts nutrient deficiencies
"""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Sum, Count
from collections import defaultdict


class NutrientGapAnalyzer:
    """Analyze consumption patterns and predict nutrient gaps"""
    
    # Nutrient content by food category (per 100g)
    CATEGORY_NUTRIENTS = {
        'vegetable': {
            'vitamins': ['Vitamin A', 'Vitamin C', 'Vitamin K', 'Folate'],
            'minerals': ['Iron', 'Calcium', 'Magnesium'],
            'fiber': 'High',
            'protein': 'Low',
        },
        'fruit': {
            'vitamins': ['Vitamin C', 'Vitamin A', 'Potassium'],
            'minerals': ['Potassium', 'Magnesium'],
            'fiber': 'High',
            'protein': 'Low',
        },
        'dairy': {
            'vitamins': ['Vitamin D', 'Vitamin B12'],
            'minerals': ['Calcium', 'Phosphorus'],
            'protein': 'High',
            'fat': 'Medium',
        },
        'meat': {
            'vitamins': ['Vitamin B12', 'Vitamin B6'],
            'minerals': ['Iron', 'Zinc'],
            'protein': 'High',
            'fat': 'Medium',
        },
        'grain': {
            'vitamins': ['B Vitamins', 'Folate'],
            'minerals': ['Iron', 'Magnesium'],
            'fiber': 'High',
            'carbs': 'High',
        },
        'beverage': {
            'vitamins': ['Vitamin C'],
            'minerals': ['Potassium'],
            'protein': 'Low',
        },
        'snack': {
            'vitamins': ['Variable'],
            'minerals': ['Sodium'],
            'fat': 'High',
            'carbs': 'High',
        },
    }
    
    # Recommended daily servings
    DAILY_RECOMMENDATIONS = {
        'vegetable': 5,  # servings
        'fruit': 3,
        'dairy': 2,
        'meat': 2,
        'grain': 6,
        'beverage': 8,
    }
    
    def __init__(self, user):
        self.user = user
        
    def analyze_consumption_patterns(self, days=30):
        """Analyze user's consumption over the last N days"""
        from food.models import ConsumptionLog
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get consumption logs
        logs = ConsumptionLog.objects.filter(
            user=self.user,
            consumption_date__gte=start_date,
            consumption_date__lte=end_date
        )
        
        # Count consumption by category
        category_counts = logs.values('category').annotate(
            total_count=Count('id'),
            total_quantity=Sum('quantity')
        )
        
        # Convert to dict
        consumption_by_category = {}
        for item in category_counts:
            consumption_by_category[item['category']] = {
                'count': item['total_count'],
                'quantity': float(item['total_quantity'] or 0)
            }
        
        return {
            'total_logs': logs.count(),
            'by_category': consumption_by_category,
            'days_analyzed': days,
            'start_date': start_date,
            'end_date': end_date
        }
    
    def predict_nutrient_gaps(self):
        """Predict likely nutrient deficiencies based on consumption"""
        patterns = self.analyze_consumption_patterns(days=30)
        
        gaps = []
        strengths = []
        
        for category, recommended in self.DAILY_RECOMMENDATIONS.items():
            consumed = patterns['by_category'].get(category, {}).get('count', 0)
            daily_avg = consumed / patterns['days_analyzed']
            
            # Check if consumption is below recommendation
            if daily_avg < recommended * 0.5:  # Less than 50% of recommended
                nutrients = self.CATEGORY_NUTRIENTS.get(category, {})
                
                gap_info = {
                    'category': category,
                    'category_display': dict([
                        ('vegetable', 'Vegetables'),
                        ('fruit', 'Fruits'),
                        ('dairy', 'Dairy'),
                        ('meat', 'Protein'),
                        ('grain', 'Grains'),
                        ('beverage', 'Beverages'),
                    ]).get(category, category.title()),
                    'daily_avg': round(daily_avg, 1),
                    'recommended': recommended,
                    'deficit_percent': round((1 - daily_avg / recommended) * 100, 1),
                    'missing_nutrients': self._get_key_nutrients(nutrients),
                    'severity': self._calculate_severity(daily_avg, recommended),
                }
                gaps.append(gap_info)
            
            elif daily_avg >= recommended * 0.8:  # At least 80% of recommended
                strengths.append({
                    'category': category,
                    'category_display': dict([
                        ('vegetable', 'Vegetables'),
                        ('fruit', 'Fruits'),
                        ('dairy', 'Dairy'),
                        ('meat', 'Protein'),
                        ('grain', 'Grains'),
                        ('beverage', 'Beverages'),
                    ]).get(category, category.title()),
                    'daily_avg': round(daily_avg, 1),
                })
        
        # Sort gaps by severity
        gaps.sort(key=lambda x: x['deficit_percent'], reverse=True)
        
        return {
            'gaps': gaps,
            'strengths': strengths,
            'overall_score': self._calculate_overall_score(patterns),
            'patterns': patterns
        }
    
    def _get_key_nutrients(self, nutrient_dict):
        """Extract key nutrients from category"""
        key_nutrients = []
        
        if 'vitamins' in nutrient_dict:
            key_nutrients.extend(nutrient_dict['vitamins'])
        if 'minerals' in nutrient_dict:
            key_nutrients.extend(nutrient_dict['minerals'])
        if 'protein' in nutrient_dict and nutrient_dict['protein'] == 'High':
            key_nutrients.append('Protein')
        if 'fiber' in nutrient_dict and nutrient_dict['fiber'] == 'High':
            key_nutrients.append('Dietary Fiber')
        
        return key_nutrients[:5]  # Return top 5
    
    def _calculate_severity(self, consumed, recommended):
        """Calculate severity level of deficiency"""
        ratio = consumed / recommended if recommended > 0 else 0
        
        if ratio < 0.25:
            return 'critical'
        elif ratio < 0.5:
            return 'high'
        elif ratio < 0.75:
            return 'moderate'
        else:
            return 'low'
    
    def _calculate_overall_score(self, patterns):
        """Calculate overall nutrition score (0-100)"""
        total_recommended = sum(self.DAILY_RECOMMENDATIONS.values())
        total_consumed = 0
        
        for category, recommended in self.DAILY_RECOMMENDATIONS.items():
            consumed = patterns['by_category'].get(category, {}).get('count', 0)
            daily_avg = consumed / patterns['days_analyzed']
            total_consumed += min(daily_avg, recommended)  # Cap at recommended
        
        score = (total_consumed / total_recommended) * 100
        return min(100, round(score, 1))
    
    def generate_food_suggestions(self):
        """Suggest specific foods to fill nutrient gaps"""
        gaps_data = self.predict_nutrient_gaps()
        suggestions = []
        
        # Food suggestions by category
        CATEGORY_FOODS = {
            'vegetable': [
                {'name': 'Spinach', 'nutrients': 'Iron, Vitamin A, Folate', 'emoji': '🥬'},
                {'name': 'Broccoli', 'nutrients': 'Vitamin C, Vitamin K, Fiber', 'emoji': '🥦'},
                {'name': 'Carrots', 'nutrients': 'Vitamin A, Beta-carotene', 'emoji': '🥕'},
                {'name': 'Sweet Potato', 'nutrients': 'Vitamin A, Fiber, Potassium', 'emoji': '🍠'},
            ],
            'fruit': [
                {'name': 'Banana', 'nutrients': 'Potassium, Vitamin B6', 'emoji': '🍌'},
                {'name': 'Orange', 'nutrients': 'Vitamin C, Fiber', 'emoji': '🍊'},
                {'name': 'Apple', 'nutrients': 'Fiber, Vitamin C', 'emoji': '🍎'},
                {'name': 'Berries', 'nutrients': 'Antioxidants, Vitamin C', 'emoji': '🫐'},
            ],
            'dairy': [
                {'name': 'Milk', 'nutrients': 'Calcium, Vitamin D, Protein', 'emoji': '🥛'},
                {'name': 'Yogurt', 'nutrients': 'Calcium, Probiotics, Protein', 'emoji': '🥄'},
                {'name': 'Cheese', 'nutrients': 'Calcium, Protein, Vitamin B12', 'emoji': '🧀'},
            ],
            'meat': [
                {'name': 'Chicken', 'nutrients': 'Protein, Vitamin B6, Niacin', 'emoji': '🍗'},
                {'name': 'Fish', 'nutrients': 'Omega-3, Protein, Vitamin D', 'emoji': '🐟'},
                {'name': 'Eggs', 'nutrients': 'Protein, Vitamin B12, Choline', 'emoji': '🥚'},
                {'name': 'Lentils', 'nutrients': 'Protein, Iron, Fiber', 'emoji': '🫘'},
            ],
            'grain': [
                {'name': 'Brown Rice', 'nutrients': 'Fiber, B Vitamins, Magnesium', 'emoji': '🍚'},
                {'name': 'Oats', 'nutrients': 'Fiber, Iron, B Vitamins', 'emoji': '🥣'},
                {'name': 'Whole Wheat Bread', 'nutrients': 'Fiber, B Vitamins', 'emoji': '🍞'},
            ],
        }
        
        for gap in gaps_data['gaps'][:3]:  # Top 3 gaps
            category = gap['category']
            if category in CATEGORY_FOODS:
                for food in CATEGORY_FOODS[category][:2]:  # Top 2 foods per category
                    suggestions.append({
                        'food': food['name'],
                        'emoji': food['emoji'],
                        'nutrients': food['nutrients'],
                        'category': gap['category_display'],
                        'reason': f"Low in {gap['category_display']} (only {gap['daily_avg']} of {gap['recommended']} daily servings)",
                        'impact': 'High' if gap['severity'] in ['critical', 'high'] else 'Medium',
                    })
        
        return suggestions
    
    def generate_weekly_meal_plan_suggestions(self):
        """Generate meal plan suggestions based on gaps"""
        gaps_data = self.predict_nutrient_gaps()
        
        meal_suggestions = []
        
        for gap in gaps_data['gaps'][:2]:  # Focus on top 2 gaps
            category = gap['category']
            
            if category == 'vegetable':
                meal_suggestions.append({
                    'meal_type': 'Lunch/Dinner',
                    'suggestion': 'Add a side salad or stir-fried vegetables',
                    'impact': f"Boost {', '.join(gap['missing_nutrients'][:2])}",
                })
            elif category == 'fruit':
                meal_suggestions.append({
                    'meal_type': 'Breakfast/Snack',
                    'suggestion': 'Include fresh fruits or smoothies',
                    'impact': f"Increase {', '.join(gap['missing_nutrients'][:2])}",
                })
            elif category == 'dairy':
                meal_suggestions.append({
                    'meal_type': 'Breakfast',
                    'suggestion': 'Start with yogurt or milk',
                    'impact': 'Boost Calcium and Protein',
                })
            elif category == 'meat':
                meal_suggestions.append({
                    'meal_type': 'Lunch/Dinner',
                    'suggestion': 'Include lean protein (fish, chicken, lentils)',
                    'impact': 'Increase Protein and Iron',
                })
        
        return meal_suggestions
