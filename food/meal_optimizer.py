"""
AI Meal Optimization Engine
Rule-based meal planning system that optimizes for budget, nutrition, and waste reduction
"""
from datetime import timedelta
from collections import defaultdict
from django.utils import timezone
from django.db.models import Sum
from .models import Recipe, FoodItem, FoodItemDatabase


class MealOptimizer:
    """
    Optimizes weekly meal plans based on:
    1. User budget constraints
    2. Available inventory (prioritize to reduce waste)
    3. Minimum nutrition requirements
    4. Dietary preferences
    """
    
    # Nutrition targets per day (for 2 people / per serving)
    NUTRITION_TARGETS = {
        'calories': {'min': 1800, 'max': 2500},
        'protein': {'min': 50},      # grams per day
        'carbs': {'min': 200},        # grams per day
        'fat': {'min': 40, 'max': 80}
    }
    
    # Minimum servings per food category per day
    FOOD_GROUP_TARGETS = {
        'vegetable': 3,
        'fruit': 2,
        'protein': 2,
        'grain': 4,
        'dairy': 1
    }
    
    def __init__(self, user, budget, week_start=None):
        """
        Initialize optimizer with user context
        
        Args:
            user: User object
            budget: Weekly budget in BDT
            week_start: Start date of week (defaults to next Monday)
        """
        self.user = user
        self.budget = float(budget)
        self.week_start = week_start or self._get_next_monday()
        self.week_end = self.week_start + timedelta(days=6)
        
        # Get user preferences
        self.dietary_preference = user.dietary_preferences if user.dietary_preferences else 'any'
        self.household_size = user.household_size
        
        # Results storage
        self.meal_plan = {}
        self.shopping_list = []
        self.inventory_used = []
        self.total_cost = 0
        self.nutrition_summary = {}
    
    def _get_next_monday(self):
        """Get the date of next Monday"""
        today = timezone.now().date()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        return today + timedelta(days=days_until_monday)
    
    def generate_meal_plan(self):
        """
        Main function to generate optimized meal plan
        
        Returns:
            dict with meal_plan, shopping_list, nutrition_summary, cost_breakdown
        """
        # Step 1: Get available inventory
        inventory = self._get_prioritized_inventory()
        
        # Step 2: Get suitable recipes based on preferences
        available_recipes = self._get_filtered_recipes()
        
        # Step 3: Create weekly meal structure
        self._initialize_weekly_structure()
        
        # Step 4: Fill meals prioritizing inventory usage
        self._fill_meals_with_optimization(available_recipes, inventory)
        
        # Step 5: Calculate nutrition summary
        self._calculate_nutrition_summary()
        
        # Step 6: Generate shopping list
        self._generate_shopping_list(inventory)
        
        # Step 7: Validate and adjust if needed
        if self.total_cost > self.budget:
            self._optimize_for_budget(available_recipes)
        
        return {
            'meal_plan': self.meal_plan,
            'shopping_list': self.shopping_list,
            'nutrition_summary': self.nutrition_summary,
            'total_cost': self.total_cost,
            'budget_limit': self.budget,
            'inventory_used': self.inventory_used,
            'week_start': self.week_start.strftime('%Y-%m-%d'),
            'week_end': self.week_end.strftime('%Y-%m-%d')
        }
    
    def _get_prioritized_inventory(self):
        """
        Get user's inventory items prioritized by:
        1. Expiring soon (next 7 days)
        2. Expiring moderate (7-14 days)
        3. Fresh items
        """
        today = timezone.now().date()
        
        inventory = FoodItem.objects.filter(user=self.user, quantity__gt=0)
        
        prioritized = {
            'urgent': [],      # Expiring in 0-7 days
            'moderate': [],    # Expiring in 7-14 days
            'fresh': []        # Expiring after 14 days or no expiry
        }
        
        for item in inventory:
            item_data = {
                'id': item.id,
                'name': item.name.lower(),
                'category': item.category,
                'quantity': float(item.quantity),
                'unit': item.unit,
                'expiration_date': item.expiration_date.strftime('%Y-%m-%d') if item.expiration_date else None,
                'price': float(item.price) if item.price else 0
            }
            
            if item.expiration_date:
                days_left = (item.expiration_date - today).days
                if 0 <= days_left <= 7:
                    prioritized['urgent'].append(item_data)
                elif 7 < days_left <= 14:
                    prioritized['moderate'].append(item_data)
                else:
                    prioritized['fresh'].append(item_data)
            else:
                prioritized['fresh'].append(item_data)
        
        return prioritized
    
    def _get_filtered_recipes(self):
        """Get recipes filtered by dietary preferences"""
        recipes = Recipe.objects.all()
        
        # Filter by dietary preference
        if self.dietary_preference == 'vegetarian':
            recipes = recipes.filter(tags__contains=['vegetarian'])
        elif self.dietary_preference == 'vegan':
            recipes = recipes.filter(tags__contains=['vegan'])
        
        # Categorize by meal type
        categorized = {
            'breakfast': list(recipes.filter(meal_type='breakfast')),
            'lunch': list(recipes.filter(meal_type='lunch')),
            'dinner': list(recipes.filter(meal_type='dinner')),
            'snack': list(recipes.filter(meal_type='snack'))
        }
        
        return categorized
    
    def _initialize_weekly_structure(self):
        """Create empty weekly meal structure"""
        days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        
        for day in days:
            self.meal_plan[day] = {
                'breakfast': None,
                'lunch': None,
                'dinner': None,
                'date': None
            }
            
            # Set actual dates as strings (JSON serializable)
            day_index = days.index(day)
            date_obj = self.week_start + timedelta(days=day_index)
            self.meal_plan[day]['date'] = date_obj.strftime('%Y-%m-%d')
    
    def _fill_meals_with_optimization(self, recipes, inventory):
        """
        Fill meal plan with recipes, prioritizing inventory usage
        
        Strategy:
        1. Match inventory items with recipe ingredients
        2. Select recipes that use urgent inventory
        3. Ensure variety (don't repeat same meal)
        4. Stay within budget
        """
        days = list(self.meal_plan.keys())
        used_recipes = set()
        
        for day in days:
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                # Get candidate recipes for this meal type
                candidates = recipes[meal_type]
                
                # Score each recipe based on inventory match
                scored_recipes = []
                for recipe in candidates:
                    if recipe.id not in used_recipes:
                        score = self._calculate_recipe_score(recipe, inventory)
                        scored_recipes.append((recipe, score))
                
                # Sort by score (highest first)
                scored_recipes.sort(key=lambda x: x[1], reverse=True)
                
                # Select best recipe that fits budget
                for recipe, score in scored_recipes:
                    recipe_cost = float(recipe.estimated_cost)
                    
                    if self.total_cost + recipe_cost <= self.budget * 0.95:  # Keep 5% buffer
                        self.meal_plan[day][meal_type] = recipe.id
                        self.total_cost += recipe_cost
                        used_recipes.add(recipe.id)
                        
                        # Mark inventory items as used
                        self._mark_inventory_used(recipe, inventory)
                        break
                
                # If no recipe selected, use cheapest option
                if self.meal_plan[day][meal_type] is None and scored_recipes:
                    cheapest = min(scored_recipes, key=lambda x: x[0].estimated_cost)
                    recipe = cheapest[0]
                    self.meal_plan[day][meal_type] = recipe.id
                    self.total_cost += float(recipe.estimated_cost)
    
    def _calculate_recipe_score(self, recipe, inventory):
        """
        Calculate score for a recipe based on inventory matching
        
        Higher score = Better match with available inventory
        
        Scoring:
        - Urgent inventory ingredient: +10 points
        - Moderate inventory ingredient: +5 points
        - Fresh inventory ingredient: +3 points
        - Budget-friendly tag: +2 points
        - Quick prep (<20 min): +1 point
        """
        score = 0
        
        # Check ingredient matching
        for ingredient in recipe.ingredients:
            ingredient_name = ingredient.get('item', '').lower()
            ingredient_category = ingredient.get('category', '')
            
            # Check in urgent inventory
            for item in inventory['urgent']:
                if ingredient_name in item['name'] or item['name'] in ingredient_name:
                    score += 10
                elif item['category'] == ingredient_category:
                    score += 5
            
            # Check in moderate inventory
            for item in inventory['moderate']:
                if ingredient_name in item['name'] or item['name'] in ingredient_name:
                    score += 5
                elif item['category'] == ingredient_category:
                    score += 3
            
            # Check in fresh inventory
            for item in inventory['fresh']:
                if ingredient_name in item['name'] or item['name'] in ingredient_name:
                    score += 3
        
        # Bonus points for recipe attributes
        if 'budget-friendly' in recipe.tags:
            score += 2
        
        if recipe.prep_time < 20:
            score += 1
        
        return score
    
    def _mark_inventory_used(self, recipe, inventory):
        """Mark inventory items that will be used in this recipe"""
        for ingredient in recipe.ingredients:
            ingredient_name = ingredient.get('item', '').lower()
            
            # Search in all inventory priorities
            for priority in ['urgent', 'moderate', 'fresh']:
                for item in inventory[priority]:
                    if ingredient_name in item['name'] or item['name'] in ingredient_name:
                        if item not in self.inventory_used:
                            self.inventory_used.append({
                                'id': item['id'],
                                'name': item['name'],
                                'category': item['category'],
                                'priority': priority
                            })
    
    def _calculate_nutrition_summary(self):
        """Calculate total nutrition for the week"""
        total_nutrition = {
            'calories': 0,
            'protein': 0,
            'carbs': 0,
            'fat': 0
        }
        
        meal_count = 0
        
        # Sum up nutrition from all meals
        for day, meals in self.meal_plan.items():
            for meal_type, recipe_id in meals.items():
                if meal_type != 'date' and recipe_id:
                    try:
                        recipe = Recipe.objects.get(id=recipe_id)
                        for nutrient in total_nutrition:
                            total_nutrition[nutrient] += recipe.nutrition.get(nutrient, 0)
                        meal_count += 1
                    except Recipe.DoesNotExist:
                        pass
        
        # Calculate daily averages
        days_count = 7
        self.nutrition_summary = {
            'total': total_nutrition,
            'daily_average': {
                nutrient: round(value / days_count, 1)
                for nutrient, value in total_nutrition.items()
            },
            'total_meals': meal_count,
            'meets_targets': self._check_nutrition_targets(total_nutrition, days_count)
        }
    
    def _check_nutrition_targets(self, total_nutrition, days):
        """Check if nutrition meets minimum daily requirements"""
        daily_avg = {k: v / days for k, v in total_nutrition.items()}
        
        meets = {
            'calories': self.NUTRITION_TARGETS['calories']['min'] <= daily_avg['calories'] <= self.NUTRITION_TARGETS['calories']['max'],
            'protein': daily_avg['protein'] >= self.NUTRITION_TARGETS['protein']['min'],
            'carbs': daily_avg['carbs'] >= self.NUTRITION_TARGETS['carbs']['min'],
            'fat': self.NUTRITION_TARGETS['fat']['min'] <= daily_avg['fat'] <= self.NUTRITION_TARGETS['fat']['max']
        }
        
        return meets
    
    def _generate_shopping_list(self, inventory):
        """
        Generate shopping list for items not in inventory
        
        Compares recipe ingredients with available inventory
        """
        # Collect all ingredients needed from meal plan
        needed_ingredients = defaultdict(lambda: {'quantity': 0, 'unit': '', 'category': ''})
        
        for day, meals in self.meal_plan.items():
            for meal_type, recipe_id in meals.items():
                if meal_type != 'date' and recipe_id:
                    try:
                        recipe = Recipe.objects.get(id=recipe_id)
                        for ingredient in recipe.ingredients:
                            item_name = ingredient.get('item', '').lower()
                            needed_ingredients[item_name]['quantity'] += ingredient.get('quantity', 0)
                            needed_ingredients[item_name]['unit'] = ingredient.get('unit', 'g')
                            needed_ingredients[item_name]['category'] = ingredient.get('category', 'other')
                    except Recipe.DoesNotExist:
                        pass
        
        # Check against inventory
        all_inventory = inventory['urgent'] + inventory['moderate'] + inventory['fresh']
        
        shopping_cost = 0
        
        for item_name, details in needed_ingredients.items():
            # Check if we have this in inventory
            in_inventory = False
            available_qty = 0
            
            for inv_item in all_inventory:
                if item_name in inv_item['name'] or inv_item['name'] in item_name:
                    in_inventory = True
                    available_qty = inv_item['quantity']
                    break
            
            quantity_needed = details['quantity']
            
            # If not enough in inventory, add to shopping list
            if not in_inventory or available_qty < quantity_needed:
                shortage = quantity_needed - (available_qty if in_inventory else 0)
                
                # Get estimated cost from database
                estimated_cost = self._get_item_cost(item_name, shortage, details['unit'])
                shopping_cost += estimated_cost
                
                self.shopping_list.append({
                    'item': item_name.title(),
                    'quantity': round(shortage, 1),
                    'unit': details['unit'],
                    'category': details['category'],
                    'estimated_cost': round(estimated_cost, 2),
                    'in_inventory': in_inventory,
                    'available_quantity': available_qty if in_inventory else 0
                })
        
        # Sort by category for easier shopping
        self.shopping_list.sort(key=lambda x: x['category'])
        
        # Add shopping cost to total cost
        self.total_cost += shopping_cost
    
    def _get_item_cost(self, item_name, quantity, unit):
        """Get estimated cost for an item from FoodItemDatabase"""
        try:
            # Try to find exact match
            db_item = FoodItemDatabase.objects.filter(
                item_name__icontains=item_name
            ).first()
            
            if db_item:
                # Calculate proportional cost based on unit
                cost_per_unit = float(db_item.sample_cost_per_unit)
                db_unit = db_item.unit.lower()
                
                # Convert to common units
                if db_unit in ['kg', 'kilogram']:
                    # Cost is per 1000g
                    if unit.lower() in ['g', 'gram', 'grams']:
                        return (cost_per_unit / 1000) * quantity
                    elif unit.lower() in ['kg', 'kilogram', 'kilograms']:
                        return cost_per_unit * quantity
                elif db_unit in ['liter', 'litre', 'l']:
                    # Cost is per 1000ml
                    if unit.lower() in ['ml', 'milliliter', 'milliliters']:
                        return (cost_per_unit / 1000) * quantity
                    elif unit.lower() in ['liter', 'litre', 'l']:
                        return cost_per_unit * quantity
                elif db_unit in ['piece', 'unit', 'item']:
                    return cost_per_unit * quantity
                else:
                    # Default: assume cost is for 100 units
                    return (cost_per_unit / 100) * quantity
            else:
                # Default estimation based on unit
                if unit.lower() in ['g', 'gram', 'grams']:
                    return quantity * 0.05  # ৳0.05 per gram
                elif unit.lower() in ['ml', 'milliliter', 'milliliters']:
                    return quantity * 0.03  # ৳0.03 per ml
                elif unit.lower() in ['kg', 'kilogram', 'kilograms']:
                    return quantity * 50  # ৳50 per kg
                elif unit.lower() in ['liter', 'litre', 'l']:
                    return quantity * 30  # ৳30 per liter
                else:
                    return quantity * 5  # ৳5 per unit
        except:
            return quantity * 0.05
    
    def _optimize_for_budget(self, recipes):
        """
        If over budget, replace expensive meals with cheaper alternatives
        """
        while self.total_cost > self.budget:
            # Find most expensive meal
            most_expensive = None
            max_cost = 0
            expensive_day = None
            expensive_type = None
            
            for day, meals in self.meal_plan.items():
                for meal_type, recipe_id in meals.items():
                    if meal_type != 'date' and recipe_id:
                        try:
                            recipe = Recipe.objects.get(id=recipe_id)
                            cost = float(recipe.estimated_cost)
                            if cost > max_cost:
                                max_cost = cost
                                most_expensive = recipe
                                expensive_day = day
                                expensive_type = meal_type
                        except Recipe.DoesNotExist:
                            pass
            
            if not most_expensive:
                break
            
            # Find cheaper alternative
            candidates = recipes[expensive_type]
            cheaper_options = [
                r for r in candidates 
                if float(r.estimated_cost) < max_cost and r.id != most_expensive.id
            ]
            
            if cheaper_options:
                # Select cheapest with budget-friendly tag
                budget_friendly = [r for r in cheaper_options if 'budget-friendly' in r.tags]
                replacement = budget_friendly[0] if budget_friendly else cheaper_options[0]
                
                # Replace meal
                cost_saved = max_cost - float(replacement.estimated_cost)
                self.meal_plan[expensive_day][expensive_type] = replacement.id
                self.total_cost -= cost_saved
            else:
                break
    
    def get_meal_plan_summary(self):
        """Get a human-readable summary of the meal plan"""
        summary = {
            'week': f"{self.week_start} to {self.week_end}",
            'total_meals': sum(1 for day in self.meal_plan.values() for k, v in day.items() if k != 'date' and v),
            'total_cost': round(self.total_cost, 2),
            'budget_remaining': round(self.budget - self.total_cost, 2),
            'budget_usage_percentage': round((self.total_cost / self.budget) * 100, 1),
            'inventory_items_used': len(self.inventory_used),
            'shopping_items': len(self.shopping_list),
            'nutrition_targets_met': sum(self.nutrition_summary.get('meets_targets', {}).values()),
        }
        return summary
