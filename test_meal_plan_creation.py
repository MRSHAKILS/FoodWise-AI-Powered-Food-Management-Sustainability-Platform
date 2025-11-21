#!/usr/bin/env python
"""Test script to create a meal plan programmatically"""
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

# Get the user
try:
    user = User.objects.get(username='raiyan')
    print(f"✅ Found user: {user.username}")
    print(f"   Budget limit: ৳{user.budget_limit}")
    print(f"   Household size: {user.household_size}")
    print(f"   Dietary preferences: {user.dietary_preferences}")
    
    # Test parameters
    budget = 5000
    week_start = date.today()
    
    print(f"\n🔧 Creating meal plan...")
    print(f"   Budget: ৳{budget}")
    print(f"   Week start: {week_start}")
    
    # Create optimizer
    optimizer = MealOptimizer(user, budget, week_start)
    print(f"✅ Optimizer initialized")
    
    # Generate meal plan
    result = optimizer.generate_meal_plan()
    print(f"✅ Meal plan generated")
    print(f"   Total cost: ৳{result['total_cost']:.2f}")
    print(f"   Shopping items: {len(result['shopping_list'])}")
    print(f"   Week start: {result['week_start']}")
    print(f"   Week end: {result['week_end']}")

    
    # Create MealPlan object
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
        notes=f"Generated automatically on {date.today()}"
    )
    print(f"✅ MealPlan saved to database with ID: {meal_plan.id}")
    print(f"\n🎉 SUCCESS! Meal plan created successfully!")
    
except User.DoesNotExist:
    print("❌ User 'raiyan' not found")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
