"""
Test script to verify all AI features are working correctly
Run with: python test_ai_features.py
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Platform.settings')
django.setup()

from food.ai_services import (
    GeminiService,
    analyze_consumption_patterns,
    generate_meal_plan,
    chat_with_nourish_bot,
    calculate_sdg_score,
    extract_food_from_image,
    rule_based_consumption_analysis
)
from datetime import datetime, timedelta
import json

def test_gemini_service():
    """Test basic Gemini service initialization"""
    print("\n" + "="*60)
    print("TEST 1: Gemini Service Initialization")
    print("="*60)
    
    try:
        service = GeminiService()
        print(f"✅ GeminiService initialized with model: {service.model_name}")
        
        if service.model:
            print(f"✅ Model object created successfully")
            return True
        else:
            print("⚠️  Model object is None - GEMINI_API_KEY may not be configured")
            print("   Fallback mode will be used")
            return False
    except Exception as e:
        print(f"❌ Error initializing GeminiService: {e}")
        return False


def test_consumption_analysis():
    """Test consumption pattern analysis"""
    print("\n" + "="*60)
    print("TEST 2: Consumption Analysis")
    print("="*60)
    
    # Sample consumption data
    sample_data = [
        {
            'item_name': 'Apple',
            'quantity': 2,
            'unit': 'pcs',
            'category': 'fruit',
            'consumption_date': (datetime.now() - timedelta(days=i)).isoformat()
        }
        for i in range(10)
    ] + [
        {
            'item_name': 'Rice',
            'quantity': 0.5,
            'unit': 'kg',
            'category': 'grain',
            'consumption_date': (datetime.now() - timedelta(days=i)).isoformat()
        }
        for i in range(5)
    ]
    
    try:
        result = analyze_consumption_patterns(sample_data)
        
        if result:
            print("✅ Consumption analysis completed")
            print(f"   - Trends found: {len(result.get('trends', []))}")
            print(f"   - Flags found: {len(result.get('flags', []))}")
            print(f"   - Waste risk items: {len(result.get('wasteRisk', []))}")
            if result.get('insights'):
                print(f"   - Insights: {result['insights'][:80]}...")
            return True
        else:
            print("⚠️  Analysis returned None - Testing fallback")
            fallback = rule_based_consumption_analysis(sample_data)
            print(f"✅ Fallback analysis worked: {len(fallback.get('trends', []))} trends")
            return True
            
    except Exception as e:
        print(f"❌ Error in consumption analysis: {e}")
        return False


def test_meal_planner():
    """Test meal plan generation"""
    print("\n" + "="*60)
    print("TEST 3: Meal Plan Generation")
    print("="*60)
    
    sample_inventory = [
        {'id': 1, 'name': 'Chicken Breast', 'quantity': 500, 'unit': 'g', 'category': 'meat', 'price': 5.0},
        {'id': 2, 'name': 'Rice', 'quantity': 2, 'unit': 'kg', 'category': 'grain', 'price': 3.0},
        {'id': 3, 'name': 'Broccoli', 'quantity': 300, 'unit': 'g', 'category': 'vegetable', 'price': 2.0},
        {'id': 4, 'name': 'Tomatoes', 'quantity': 500, 'unit': 'g', 'category': 'vegetable', 'price': 2.5},
    ]
    
    dietary_needs = {
        'vegetarian': False,
        'allergies': [],
        'min_protein_per_day': 50
    }
    
    try:
        result = generate_meal_plan(budget=50, inventory=sample_inventory, dietary_needs=dietary_needs, days=3)
        
        if result:
            print("✅ Meal plan generated")
            print(f"   - Days planned: {len(result.get('mealPlan', []))}")
            print(f"   - Shopping list items: {len(result.get('shoppingList', []))}")
            print(f"   - Total cost: ${result.get('totalCost', 0)}")
            print(f"   - Nutrition score: {result.get('nutritionScore', 0)}")
            return True
        else:
            print("⚠️  Meal plan generation returned None (API key may be missing)")
            return False
            
    except Exception as e:
        print(f"❌ Error in meal planning: {e}")
        return False


def test_nourish_bot():
    """Test NourishBot chat"""
    print("\n" + "="*60)
    print("TEST 4: NourishBot Chat")
    print("="*60)
    
    user_context = {
        'inventory': [
            {'name': 'Apples', 'quantity': 5, 'expiring_days': 3},
            {'name': 'Milk', 'quantity': 1, 'expiring_days': 2}
        ],
        'recent_consumption': [],
        'budget': 100
    }
    
    try:
        response = chat_with_nourish_bot(
            "What recipes can I make with apples?",
            user_context
        )
        
        if response:
            print("✅ NourishBot response received")
            print(f"   Response length: {len(response)} characters")
            print(f"   First 100 chars: {response[:100]}...")
            return True
        else:
            print("⚠️  NourishBot returned None (API key may be missing)")
            return False
            
    except Exception as e:
        print(f"❌ Error in NourishBot: {e}")
        return False


def test_sdg_scoring():
    """Test SDG score calculation"""
    print("\n" + "="*60)
    print("TEST 5: SDG Score Calculation")
    print("="*60)
    
    waste_data = {
        'total_waste_kg': 2.5,
        'total_cost': 15.0,
        'reduction_from_last_week': 10
    }
    
    nutrition_data = {
        'category_diversity': 5,
        'protein_intake': 60,
        'vegetable_servings': 7
    }
    
    budget_data = {
        'budget_limit': 100,
        'actual_spend': 85,
        'efficiency': 85
    }
    
    try:
        result = calculate_sdg_score(waste_data, nutrition_data, budget_data)
        
        if result:
            print("✅ SDG score calculated")
            print(f"   - Total score: {result.get('totalScore', 0)}/100")
            print(f"   - Waste reduction: {result.get('breakdown', {}).get('wasteReduction', 0)}")
            print(f"   - Nutrition balance: {result.get('breakdown', {}).get('nutritionBalance', 0)}")
            print(f"   - Budget efficiency: {result.get('breakdown', {}).get('budgetEfficiency', 0)}")
            return True
        else:
            print("⚠️  SDG score calculation returned None (API key may be missing)")
            return False
            
    except Exception as e:
        print(f"❌ Error in SDG scoring: {e}")
        return False


def test_model_names():
    """Test that correct model names are being used"""
    print("\n" + "="*60)
    print("TEST 6: Model Names Verification")
    print("="*60)
    
    try:
        # Test default model
        service_default = GeminiService()
        print(f"✅ Default model: {service_default.model_name}")
        
        # Test with specific model
        service_flash = GeminiService(model_name='gemini-2.0-flash-lite')
        print(f"✅ Flash model: {service_flash.model_name}")
        
        service_exp = GeminiService(model_name='gemini-exp-1206')
        print(f"✅ Experimental model: {service_exp.model_name}")
        
        # Verify no old model names in code
        import inspect
        source = inspect.getsource(GeminiService)
        if 'gemini-1.5' in source:
            print("⚠️  Warning: Old model names (gemini-1.5) found in code")
            return False
        else:
            print("✅ No old model names found in code")
            
        return True
        
    except Exception as e:
        print(f"❌ Error checking model names: {e}")
        return False


def run_all_tests():
    """Run all tests and generate report"""
    print("\n" + "="*60)
    print("AI FEATURES COMPREHENSIVE TEST SUITE")
    print("="*60)
    
    results = {
        'Gemini Service': test_gemini_service(),
        'Consumption Analysis': test_consumption_analysis(),
        'Meal Planner': test_meal_planner(),
        'NourishBot Chat': test_nourish_bot(),
        'SDG Scoring': test_sdg_scoring(),
        'Model Names': test_model_names()
    }
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    # Check for API key
    print("\n" + "="*60)
    print("CONFIGURATION STATUS")
    print("="*60)
    
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key:
        print(f"✅ GEMINI_API_KEY is configured (length: {len(api_key)})")
    else:
        print("⚠️  GEMINI_API_KEY is NOT configured")
        print("   - AI features will use fallback/rule-based logic")
        print("   - To enable full AI features, add GEMINI_API_KEY to .env file")
        print("   - Get your key from: https://makersuite.google.com/app/apikey")
    
    print("\n" + "="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
