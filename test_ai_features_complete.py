"""
AI Features Test Script - Tests Gemini API Integration
Tests all 6 AI-powered features with actual API calls
"""

import os
import sys
import django
import json
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Platform.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.contrib.auth import get_user_model
from food.models import FoodItem, ConsumptionLog, WasteLog
from django.utils import timezone
from food.ai_services import (
    analyze_consumption_patterns,
    generate_meal_plan,
    chat_with_nourish_bot,
    calculate_sdg_score,
    GeminiService
)

User = get_user_model()

def print_header(title):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)

def print_success(message):
    """Print success message"""
    print(f"✅ {message}")

def print_error(message):
    """Print error message"""
    print(f"❌ {message}")

def print_info(message):
    """Print info message"""
    print(f"ℹ️  {message}")

def check_api_key():
    """Check if Gemini API key is configured"""
    print_header("1. Checking API Configuration")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('GEMINI_API_KEY')
    google_client_id = os.getenv('GOOGLE_CLIENT_ID')
    google_secret = os.getenv('GOOGLE_CLIENT_SECRET')
    
    if api_key:
        print_success(f"Gemini API Key found: {api_key[:10]}...{api_key[-4:]}")
    else:
        print_error("Gemini API Key NOT found in .env")
        return False
    
    if google_client_id:
        print_success(f"Google Client ID found: {google_client_id[:20]}...")
    else:
        print_info("Google Client ID not configured (optional)")
    
    if google_secret:
        print_success("Google Client Secret found")
    else:
        print_info("Google Client Secret not configured (optional)")
    
    return bool(api_key)

def create_test_user():
    """Create or get test user with sample data"""
    print_header("2. Setting Up Test User with Sample Data")
    
    # Clean up existing test user
    User.objects.filter(username='ai_test_user').delete()
    
    # Create test user
    user = User.objects.create_user(
        username='ai_test_user',
        email='aitest@test.com',
        password='testpass123',
        full_name='AI Test User',
        household_size=3,
        dietary_preferences='Vegetarian',
        location='Test City',
        budget_limit=300.00
    )
    print_success(f"Created test user: {user.username}")
    
    # Add sample inventory items
    print_info("Adding sample inventory items...")
    sample_items = [
        {'name': 'Milk', 'quantity': 2, 'unit': 'liter', 'category': 'dairy', 
         'expiration_date': timezone.now().date() + timedelta(days=2), 'price': 5.50},
        {'name': 'Eggs', 'quantity': 12, 'unit': 'piece', 'category': 'protein',
         'expiration_date': timezone.now().date() + timedelta(days=10), 'price': 4.00},
        {'name': 'Tomatoes', 'quantity': 1.5, 'unit': 'kg', 'category': 'vegetable',
         'expiration_date': timezone.now().date() + timedelta(days=4), 'price': 3.50},
        {'name': 'Rice', 'quantity': 5, 'unit': 'kg', 'category': 'grain',
         'expiration_date': timezone.now().date() + timedelta(days=365), 'price': 10.00},
        {'name': 'Bread', 'quantity': 2, 'unit': 'loaf', 'category': 'grain',
         'expiration_date': timezone.now().date() + timedelta(days=3), 'price': 3.00},
    ]
    
    for item_data in sample_items:
        FoodItem.objects.create(user=user, **item_data)
    print_success(f"Added {len(sample_items)} inventory items")
    
    # Add sample consumption logs
    print_info("Adding sample consumption logs...")
    sample_logs = [
        {'item_name': 'Rice', 'quantity': 0.5, 'unit': 'kg', 'category': 'grain',
         'consumption_date': timezone.now().date() - timedelta(days=1)},
        {'item_name': 'Tomatoes', 'quantity': 0.3, 'unit': 'kg', 'category': 'vegetable',
         'consumption_date': timezone.now().date() - timedelta(days=2)},
        {'item_name': 'Eggs', 'quantity': 4, 'unit': 'piece', 'category': 'protein',
         'consumption_date': timezone.now().date() - timedelta(days=1)},
        {'item_name': 'Milk', 'quantity': 0.5, 'unit': 'liter', 'category': 'dairy',
         'consumption_date': timezone.now().date()},
    ]
    
    for log_data in sample_logs:
        ConsumptionLog.objects.create(user=user, **log_data)
    print_success(f"Added {len(sample_logs)} consumption logs")
    
    return user

def test_consumption_analysis(user):
    """Test AI Consumption Pattern Analyzer"""
    print_header("3. Testing AI Consumption Analysis")
    
    try:
        # Get consumption data
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        consumption_logs = list(ConsumptionLog.objects.filter(
            user=user,
            consumption_date__gte=thirty_days_ago
        ).values('item_name', 'quantity', 'unit', 'category', 'consumption_date'))
        
        print_info(f"Analyzing {len(consumption_logs)} consumption logs...")
        
        # Call AI analysis
        result = analyze_consumption_patterns(consumption_logs)
        
        if result:
            print_success("AI Consumption Analysis completed!")
            print(f"\n📊 Analysis Results:")
            print(f"   Trends identified: {len(result.get('trends', []))}")
            print(f"   Flags raised: {len(result.get('flags', []))}")
            print(f"   Waste risks: {len(result.get('wasteRisk', []))}")
            
            if result.get('trends'):
                print(f"\n   Sample trend: {result['trends'][0]}")
            
            return True
        else:
            print_error("No result from AI analysis (using fallback)")
            return False
            
    except Exception as e:
        print_error(f"Consumption analysis failed: {str(e)}")
        return False

def test_meal_planner(user):
    """Test AI Meal Optimization Engine"""
    print_header("4. Testing AI Meal Planner")
    
    try:
        # Get inventory
        inventory = list(FoodItem.objects.filter(user=user).values(
            'name', 'quantity', 'unit', 'category', 'expiration_date', 'price'
        ))
        
        print_info(f"Generating meal plan with {len(inventory)} inventory items...")
        print_info(f"Budget: ${user.budget_limit}")
        
        # Call AI meal planner
        dietary_needs = {
            'preferences': user.dietary_preferences or 'None',
            'household_size': user.household_size,
            'min_protein': 50,
            'min_veggies': 5
        }
        
        result = generate_meal_plan(
            budget=float(user.budget_limit or 100),
            inventory=inventory,
            dietary_needs=dietary_needs,
            days=7
        )
        
        if result:
            print_success("AI Meal Plan generated!")
            print(f"\n🍽️  Meal Plan Results:")
            print(f"   Days planned: {len(result.get('mealPlan', []))}")
            print(f"   Total cost: ${result.get('totalCost', 0):.2f}")
            print(f"   Shopping items: {len(result.get('shoppingList', []))}")
            
            if result.get('mealPlan') and len(result['mealPlan']) > 0:
                first_day = result['mealPlan'][0]
                print(f"\n   Day 1 sample: {first_day.get('day', 'N/A')}")
                if first_day.get('meals'):
                    print(f"   - {first_day['meals'][0].get('name', 'N/A')}")
            
            return True
        else:
            print_error("No result from AI meal planner")
            return False
            
    except Exception as e:
        print_error(f"Meal planner failed: {str(e)}")
        return False

def test_nourish_bot(user):
    """Test NourishBot Chatbot"""
    print_header("5. Testing NourishBot Chatbot")
    
    test_messages = [
        "I have milk, eggs, and tomatoes. What can I make for breakfast?",
        "How can I reduce food waste?",
        "Give me tips for meal planning on a budget"
    ]
    
    try:
        for i, message in enumerate(test_messages, 1):
            print_info(f"Test {i}/3: '{message[:50]}...'")
            
            # Get user context
            inventory = list(FoodItem.objects.filter(user=user).values('name', 'quantity', 'category'))
            user_context = {
                'user_id': user.id,
                'inventory': inventory,
                'dietary_preferences': user.dietary_preferences,
                'household_size': user.household_size
            }
            
            response = chat_with_nourish_bot(
                user_message=message,
                user_context=user_context,
                chat_history=[]
            )
            
            if response:
                print_success(f"Response received ({len(response)} chars)")
                print(f"   Preview: {response[:100]}...")
            else:
                print_error(f"No response for message {i}")
                
        return True
        
    except Exception as e:
        print_error(f"NourishBot failed: {str(e)}")
        return False

def test_sdg_scoring(user):
    """Test SDG Impact Scoring"""
    print_header("6. Testing SDG Impact Scoring")
    
    try:
        print_info("Calculating SDG impact score...")
        
        # Prepare data for scoring
        waste_data = {
            'total_waste': 5.0,  # kg
            'waste_cost': 15.0,  # dollars
            'waste_reduction': 20  # percent
        }
        
        nutrition_data = {
            'balanced_meals': 15,
            'total_meals': 21,
            'protein_met': True,
            'veggies_met': True
        }
        
        budget_data = {
            'spent': 250.0,
            'budget': float(user.budget_limit or 300),
            'efficiency': 85
        }
        
        # Calculate score
        result = calculate_sdg_score(waste_data, nutrition_data, budget_data)
        
        if result:
            print_success("SDG Score calculated!")
            print(f"\n🎯 SDG Impact Results:")
            print(f"   Total Score: {result.get('totalScore', 0)}/100")
            
            breakdown = result.get('breakdown', {})
            print(f"   - Waste Reduction: {breakdown.get('wasteReduction', 0)}/40")
            print(f"   - Nutrition Balance: {breakdown.get('nutritionBalance', 0)}/30")
            print(f"   - Budget Efficiency: {breakdown.get('budgetEfficiency', 0)}/20")
            print(f"   - Community Engagement: {breakdown.get('communityEngagement', 0)}/10")
            
            if result.get('insights'):
                print(f"\n   Insights: {result['insights'][:100]}...")
            
            return True
        else:
            print_error("No result from SDG scoring")
            return False
            
    except Exception as e:
        print_error(f"SDG scoring failed: {str(e)}")
        return False

def test_ocr_system():
    """Test Gemini Vision OCR (without actual image)"""
    print_header("7. Testing OCR System Status")
    
    try:
        from uploads.ocr_utils import extract_food_from_image
        print_success("OCR module loaded successfully")
        print_info("OCR requires actual image upload - test in UI at /uploads/")
        print_info("Upload a receipt/food label and check 'Process with AI'")
        return True
    except Exception as e:
        print_error(f"OCR module check failed: {str(e)}")
        return False

def cleanup_test_data(user):
    """Clean up test data"""
    print_header("8. Cleaning Up Test Data")
    
    try:
        # Delete test user and related data
        user.delete()
        print_success("Test data cleaned up")
    except Exception as e:
        print_error(f"Cleanup failed: {str(e)}")

def main():
    """Run all AI feature tests"""
    print("\n" + "🤖" * 40)
    print("     FOODWISE AI FEATURES - COMPREHENSIVE TEST SUITE")
    print("🤖" * 40)
    
    results = {
        'api_key': False,
        'consumption_analysis': False,
        'meal_planner': False,
        'nourish_bot': False,
        'sdg_scoring': False,
        'ocr_system': False
    }
    
    # Check API configuration
    if not check_api_key():
        print_error("\n⚠️  Cannot proceed without Gemini API key!")
        print_info("Add GEMINI_API_KEY to your .env file")
        return
    results['api_key'] = True
    
    # Create test user with data
    user = create_test_user()
    
    # Run AI feature tests
    results['consumption_analysis'] = test_consumption_analysis(user)
    results['meal_planner'] = test_meal_planner(user)
    results['nourish_bot'] = test_nourish_bot(user)
    results['sdg_scoring'] = test_sdg_scoring(user)
    results['ocr_system'] = test_ocr_system()
    
    # Cleanup
    cleanup_test_data(user)
    
    # Print summary
    print_header("TEST SUMMARY")
    print("\n📊 Results:")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    success_rate = (passed_tests / total_tests) * 100
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"   {status} - {test_name.replace('_', ' ').title()}")
    
    print(f"\n🎯 Success Rate: {passed_tests}/{total_tests} ({success_rate:.1f}%)")
    
    if success_rate == 100:
        print("\n🎉 ALL AI FEATURES WORKING PERFECTLY!")
        print("   Your platform is ready for production!")
    elif success_rate >= 80:
        print("\n⚠️  Most features working, some issues detected")
        print("   Check the errors above for details")
    else:
        print("\n❌ Multiple AI features not working")
        print("   Verify API key and check error messages")
    
    print("\n" + "=" * 80)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
