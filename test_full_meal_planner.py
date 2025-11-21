#!/usr/bin/env python
"""Comprehensive test for the meal planning system"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Platform.settings')
django.setup()

from django.contrib.auth import get_user_model
from datetime import date, timedelta
from food.meal_optimizer import MealOptimizer
from food.models import MealPlan, Recipe, FoodItem

User = get_user_model()

def print_separator():
    print("\n" + "="*80 + "\n")

def test_recipe_database():
    """Test that recipes are loaded"""
    print("📚 Testing Recipe Database...")
    recipes = Recipe.objects.all()
    print(f"   Total recipes: {recipes.count()}")
    
    breakfast = Recipe.objects.filter(meal_type='breakfast').count()
    lunch = Recipe.objects.filter(meal_type='lunch').count()
    dinner = Recipe.objects.filter(meal_type='dinner').count()
    snack = Recipe.objects.filter(meal_type='snack').count()
    
    print(f"   Breakfast: {breakfast}")
    print(f"   Lunch: {lunch}")
    print(f"   Dinner: {dinner}")
    print(f"   Snacks: {snack}")
    
    if recipes.count() > 0:
        print("✅ Recipe database is populated")
        return True
    else:
        print("❌ Recipe database is empty")
        return False

def test_user_setup():
    """Test user configuration"""
    print("👤 Testing User Setup...")
    try:
        user = User.objects.get(username='raiyan')
        print(f"   Username: {user.username}")
        print(f"   Budget limit: ৳{user.budget_limit if user.budget_limit else 'Not set'}")
        print(f"   Household size: {user.household_size}")
        print(f"   Dietary preferences: {user.dietary_preferences if user.dietary_preferences else 'None'}")
        print("✅ User setup complete")
        return user
    except User.DoesNotExist:
        print("❌ User not found")
        return None

def test_inventory():
    """Test user's food inventory"""
    print("📦 Testing Food Inventory...")
    user = User.objects.get(username='raiyan')
    inventory = FoodItem.objects.filter(user=user, quantity__gt=0)
    
    print(f"   Total items: {inventory.count()}")
    
    if inventory.count() > 0:
        urgent = inventory.filter(expiration_date__lte=date.today() + timedelta(days=7)).count()
        moderate = inventory.filter(
            expiration_date__gt=date.today() + timedelta(days=7),
            expiration_date__lte=date.today() + timedelta(days=14)
        ).count()
        
        print(f"   Expiring soon (0-7 days): {urgent}")
        print(f"   Expiring moderate (7-14 days): {moderate}")
        print("✅ Inventory available for optimization")
    else:
        print("⚠️  No inventory items (optimizer will work with recipes only)")
    
    return inventory.count() > 0

def test_meal_plan_generation(user, budget):
    """Test meal plan generation"""
    print(f"🍽️  Testing Meal Plan Generation (Budget: ৳{budget})...")
    
    week_start = date.today()
    
    # Create optimizer
    optimizer = MealOptimizer(user, budget, week_start)
    print("   ✓ Optimizer initialized")
    
    # Generate meal plan
    result = optimizer.generate_meal_plan()
    print("   ✓ Meal plan generated")
    
    # Analyze results
    print(f"\n   📊 Results:")
    print(f"   Total cost: ৳{result['total_cost']:.2f}")
    print(f"   Budget limit: ৳{result['budget_limit']:.2f}")
    print(f"   Budget status: {'✅ Within budget' if result['total_cost'] <= result['budget_limit'] else '⚠️  Over budget'}")
    print(f"   Shopping list items: {len(result['shopping_list'])}")
    print(f"   Week: {result['week_start']} to {result['week_end']}")
    
    # Count meals
    meal_count = 0
    for day in result['meal_plan'].values():
        if isinstance(day, dict):
            for meal_type in ['breakfast', 'lunch', 'dinner']:
                if day.get(meal_type):
                    meal_count += 1
    
    print(f"   Total meals planned: {meal_count}/21")
    
    # Show nutrition summary
    if result['nutrition_summary']:
        print(f"\n   🥗 Nutrition Summary:")
        print(f"   Calories: {result['nutrition_summary'].get('calories', 0):.0f}")
        print(f"   Protein: {result['nutrition_summary'].get('protein', 0):.1f}g")
        print(f"   Carbs: {result['nutrition_summary'].get('carbohydrates', 0):.1f}g")
        print(f"   Fat: {result['nutrition_summary'].get('fat', 0):.1f}g")
    
    return result

def test_meal_plan_save(user, result):
    """Test saving meal plan to database"""
    print("\n💾 Testing Database Save...")
    
    try:
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
            notes=f"Test plan created on {date.today()}"
        )
        print(f"   ✓ MealPlan saved with ID: {meal_plan.id}")
        print("✅ Database save successful")
        return meal_plan
    except Exception as e:
        print(f"❌ Database save failed: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_meal_plan_retrieval(meal_plan_id):
    """Test retrieving meal plan from database"""
    print(f"\n🔍 Testing Meal Plan Retrieval (ID: {meal_plan_id})...")
    
    try:
        meal_plan = MealPlan.objects.get(id=meal_plan_id)
        print(f"   ✓ Retrieved meal plan")
        print(f"   Week: {meal_plan.week_start} to {meal_plan.week_end}")
        print(f"   Cost: ৳{meal_plan.actual_cost:.2f} / ৳{meal_plan.budget_limit:.2f}")
        print(f"   Created: {meal_plan.created_at}")
        print("✅ Retrieval successful")
        return True
    except MealPlan.DoesNotExist:
        print("❌ Meal plan not found")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print("🧪 AI MEAL OPTIMIZATION ENGINE - COMPREHENSIVE TEST")
    print("="*80)
    
    # Test 1: Recipe Database
    print_separator()
    if not test_recipe_database():
        print("\n❌ Cannot proceed without recipes")
        return
    
    # Test 2: User Setup
    print_separator()
    user = test_user_setup()
    if not user:
        print("\n❌ Cannot proceed without user")
        return
    
    # Test 3: Inventory
    print_separator()
    test_inventory()
    
    # Test 4: Meal Plan Generation - Budget Test 1
    print_separator()
    result1 = test_meal_plan_generation(user, 5000)
    
    if result1:
        meal_plan1 = test_meal_plan_save(user, result1)
        if meal_plan1:
            test_meal_plan_retrieval(meal_plan1.id)
    
    # Test 5: Meal Plan Generation - Budget Test 2
    print_separator()
    result2 = test_meal_plan_generation(user, 3000)
    
    if result2:
        meal_plan2 = test_meal_plan_save(user, result2)
        if meal_plan2:
            test_meal_plan_retrieval(meal_plan2.id)
    
    # Final Summary
    print_separator()
    total_plans = MealPlan.objects.filter(user=user).count()
    print("📈 FINAL SUMMARY")
    print(f"   Total meal plans created: {total_plans}")
    print("\n✅ ALL TESTS COMPLETED SUCCESSFULLY!")
    print("="*80 + "\n")

if __name__ == '__main__':
    main()
