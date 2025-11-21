#!/usr/bin/env python
"""Test meal plan with tight budget to see optimization"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from datetime import date, timedelta
from food.meal_optimizer import MealOptimizer
from food.models import MealPlan

User = get_user_model()

user = User.objects.get(username='raiyan')
print(f"Creating meal plan with tight budget...")

# Test with 3000 budget
budget = 3000
week_start = date.today() + timedelta(days=7)  # Next week

optimizer = MealOptimizer(user, budget, week_start)
result = optimizer.generate_meal_plan()

print(f"\n📊 Results:")
print(f"   Budget: {result['budget_limit']:.2f}")
print(f"   Total cost: {result['total_cost']:.2f}")
print(f"   Budget usage: {(result['total_cost'] / result['budget_limit'] * 100):.1f}%")
print(f"   Shopping items: {len(result['shopping_list'])}")

# Save to database
meal_plan = MealPlan.objects.create(
    user=user,
    week_start=result['week_start'],
    week_end=result['week_end'],
    budget_limit=result['budget_limit'],
    actual_cost=result['total_cost'],
    meals=result['meal_plan'],
    shopping_list=result['shopping_list'],
    nutrition_summary=result['nutrition_summary'],
    inventory_used=result['inventory_used'],
    notes="Low budget test"
)

print(f"\n✅ Meal plan {meal_plan.id} created successfully!")
