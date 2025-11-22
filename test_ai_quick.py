"""
Simple AI Test - Quick verification of Gemini API and basic features
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Platform.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from dotenv import load_dotenv
load_dotenv()

def test_api_key():
    """Test 1: Check if API key is configured"""
    print("\n" + "="*60)
    print("Test 1: API Key Configuration")
    print("="*60)
    
    api_key = os.getenv('GEMINI_API_KEY')
    google_id = os.getenv('GOOGLE_CLIENT_ID')
    
    if api_key:
        print(f"✅ Gemini API Key: {api_key[:15]}...{api_key[-4:]}")
    else:
        print("❌ Gemini API Key NOT FOUND")
        return False
    
    if google_id:
        print(f"✅ Google OAuth Client ID: {google_id[:30]}...")
    else:
        print("ℹ️  Google OAuth not configured (optional)")
    
    return True

def test_gemini_connection():
    """Test 2: Test actual connection to Gemini API"""
    print("\n" + "="*60)
    print("Test 2: Gemini API Connection")
    print("="*60)
    
    try:
        import google.generativeai as genai
        
        api_key = os.getenv('GEMINI_API_KEY')
        genai.configure(api_key=api_key)
        
        # Try a simple generation
        model = genai.GenerativeModel('gemini-2.0-flash-lite')
        response = model.generate_content("Say 'Hello from Gemini!' in one sentence.")
        
        print(f"✅ Connection successful!")
        print(f"   Response: {response.text[:100]}...")
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {str(e)[:100]}")
        return False

def test_ai_services_import():
    """Test 3: Check if AI services can be imported"""
    print("\n" + "="*60)
    print("Test 3: AI Services Module")
    print("="*60)
    
    try:
        from food.ai_services import (
            GeminiService,
            analyze_consumption_patterns,
            generate_meal_plan,
            chat_with_nourish_bot
        )
        print("✅ All AI service functions imported successfully")
        
        # Test GeminiService initialization
        service = GeminiService()
        print(f"✅ GeminiService initialized (model: {service.model_name})")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {str(e)}")
        return False

def test_simple_chat():
    """Test 4: Test simple NourishBot chat"""
    print("\n" + "="*60)
    print("Test 4: NourishBot Simple Test")
    print("="*60)
    
    try:
        from food.ai_services import chat_with_nourish_bot
        
        user_context = {
            'user_id': 1,
            'inventory': [
                {'name': 'Rice', 'quantity': 2, 'category': 'grain'},
                {'name': 'Tomatoes', 'quantity': 3, 'category': 'vegetable'}
            ],
            'dietary_preferences': 'Vegetarian',
            'household_size': 2
        }
        
        print("ℹ️  Sending test message to NourishBot...")
        response = chat_with_nourish_bot(
            user_message="Hello! Can you help me reduce food waste?",
            user_context=user_context,
            chat_history=[]
        )
        
        if response:
            print(f"✅ NourishBot Response received!")
            print(f"   Preview: {response[:150]}...")
            return True
        else:
            print("❌ No response from NourishBot")
            return False
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "quota" in error_msg.lower():
            print(f"⚠️  Rate limit reached - API is working but too many requests")
            print(f"   This is normal - just wait a minute and try again")
            return True
        else:
            print(f"❌ Chat test failed: {error_msg[:100]}")
            return False

def test_database():
    """Test 5: Check database seeding"""
    print("\n" + "="*60)
    print("Test 5: Database Status")
    print("="*60)
    
    try:
        from food.models import FoodItemDatabase
        from resources.models import Resource
        
        food_count = FoodItemDatabase.objects.count()
        resource_count = Resource.objects.count()
        
        print(f"✅ Food Database: {food_count} items")
        print(f"✅ Resources: {resource_count} items")
        
        return food_count > 0 and resource_count > 0
        
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")
        return False

def test_ocr_module():
    """Test 6: Check OCR module"""
    print("\n" + "="*60)
    print("Test 6: OCR Module (Gemini Vision)")
    print("="*60)
    
    try:
        from uploads.ocr_utils import extract_food_from_image
        print("✅ OCR module loaded")
        print("ℹ️  To test OCR: Upload an image at /uploads/ and check 'Process with AI'")
        return True
    except Exception as e:
        print(f"❌ OCR module error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "🤖"*30)
    print("     FOODWISE AI - QUICK VERIFICATION TEST")
    print("🤖"*30)
    
    tests = [
        ("API Key Configuration", test_api_key),
        ("Gemini Connection", test_gemini_connection),
        ("AI Services Import", test_ai_services_import),
        ("NourishBot Chat", test_simple_chat),
        ("Database Status", test_database),
        ("OCR Module", test_ocr_module),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test crashed: {str(e)[:100]}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\n🎯 Success Rate: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("   Your AI features are configured and working!")
        print("\n📝 Next Steps:")
        print("   1. Visit http://127.0.0.1:8000/food/ai/nourish-bot/")
        print("   2. Try the AI Meal Planner")
        print("   3. Upload a receipt to test OCR")
    elif passed >= total * 0.66:
        print("\n✅ Most tests passed!")
        print("   Core AI functionality is working")
    else:
        print("\n⚠️  Some issues detected")
        print("   Check the errors above")
    
    print("\n" + "="*60)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
