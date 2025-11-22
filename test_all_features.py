"""
Comprehensive Feature Testing Script
Tests all URLs, views, and features to document working vs broken functionality
"""

import sys
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Platform.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from django.test import Client
from users.models import User
from food.models import FoodItem, FoodItemDatabase
from resources.models import Resource
import json

def test_all_features():
    """Test all features and generate comprehensive report"""
    
    client = Client()
    results = {
        'working': [],
        'broken': [],
        'requires_auth': [],
        'not_implemented': []
    }
    
    print("=" * 80)
    print("FOODWISE PLATFORM - COMPREHENSIVE FEATURE TEST")
    print("=" * 80)
    print()
    
    # Test URLs without authentication
    print("🔍 Testing Public URLs (No Auth Required)")
    print("-" * 80)
    
    public_urls = [
        ('/', 'Landing Page'),
        ('/users/login/', 'Login Page'),
        ('/users/register/', 'Register Page'),
    ]
    
    for url, name in public_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                results['working'].append(f"✅ {name} ({url}) - OK")
                print(f"✅ {name}: OK (200)")
            elif response.status_code == 302:
                results['working'].append(f"✅ {name} ({url}) - Redirect")
                print(f"✅ {name}: Redirect (302)")
            else:
                results['broken'].append(f"❌ {name} ({url}) - {response.status_code}")
                print(f"❌ {name}: Error ({response.status_code})")
        except Exception as e:
            results['broken'].append(f"❌ {name} ({url}) - Exception: {str(e)}")
            print(f"❌ {name}: Exception - {str(e)[:50]}")
    
    print()
    
    # Create test user for authenticated tests
    print("👤 Creating Test User...")
    print("-" * 80)
    
    try:
        # Clean up existing test user
        User.objects.filter(username='testuser').delete()
        
        test_user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123',
            full_name='Test User',
            household_size=2,
            dietary_preferences='None',
            location='Test City',
            budget_limit=500.00
        )
        print(f"✅ Test user created: {test_user.username}")
        
        # Login
        login_success = client.login(username='testuser', password='testpass123')
        if login_success:
            print("✅ Test user logged in successfully")
        else:
            print("❌ Failed to login test user")
            results['broken'].append("❌ User authentication system")
    except Exception as e:
        print(f"❌ Failed to create test user: {str( e)}")
        results['broken'].append(f"❌ User creation - {str(e)}")
        return results
    
    print()
    
    # Test Authenticated URLs - Food App
    print("🍎 Testing Food App URLs (Authenticated)")
    print("-" * 80)
    
    food_urls = [
        ('/food/inventory/', 'Inventory List'),
        ('/food/inventory/add/', 'Add Inventory Item'),
        ('/food/logs/', 'Consumption Logs'),
        ('/food/logs/add/', 'Add Consumption Log'),
        ('/food/history/', 'Consumption History'),
        ('/food/food-items/', 'Food Items List'),
        ('/food/food-database/', 'Food Database'),
        ('/food/dashboard/', 'Enhanced Dashboard'),
        ('/food/waste-logs/', 'Waste Logs'),
        ('/food/surplus/', 'Food Surplus'),
        ('/food/ai/consumption-analysis/', 'AI Consumption Analysis'),
        ('/food/ai/meal-planner/', 'AI Meal Planner'),
        ('/food/ai/nourish-bot/', 'NourishBot Chatbot'),
        ('/food/ai/sdg-score/', 'SDG Score'),
        ('/food/ai/waste-estimation/', 'Waste Estimation'),
        ('/food/ai/expiration-risks/', 'Expiration Risks'),
    ]
    
    for url, name in food_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                results['working'].append(f"✅ {name} ({url})")
                print(f"✅ {name}: OK")
            elif response.status_code == 404:
                results['broken'].append(f"❌ {name} ({url}) - Not Found")
                print(f"❌ {name}: 404 Not Found")
            elif response.status_code == 500:
                results['broken'].append(f"❌ {name} ({url}) - Server Error")
                print(f"❌ {name}: 500 Server Error")
            else:
                results['broken'].append(f"❌ {name} ({url}) - {response.status_code}")
                print(f"❌ {name}: Error ({response.status_code})")
        except Exception as e:
            results['broken'].append(f"❌ {name} ({url}) - Exception: {str(e)[:50]}")
            print(f"❌ {name}: Exception - {str(e)[:50]}")
    
    print()
    
    # Test Resources App
    print("📚 Testing Resources App URLs")
    print("-" * 80)
    
    resources_urls = [
        ('/resources/', 'Resources List'),
        ('/resources/recommendations/', 'Recommended Resources'),
    ]
    
    for url, name in resources_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                results['working'].append(f"✅ {name} ({url})")
                print(f"✅ {name}: OK")
            else:
                results['broken'].append(f"❌ {name} ({url}) - {response.status_code}")
                print(f"❌ {name}: Error ({response.status_code})")
        except Exception as e:
            results['broken'].append(f"❌ {name} ({url}) - Exception: {str(e)[:50]}")
            print(f"❌ {name}: Exception")
    
    print()
    
    # Test Uploads App
    print("📸 Testing Uploads App URLs")
    print("-" * 80)
    
    uploads_urls = [
        ('/uploads/', 'Upload Form'),
        ('/uploads/list/', 'Uploads List'),
    ]
    
    for url, name in uploads_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                results['working'].append(f"✅ {name} ({url})")
                print(f"✅ {name}: OK")
            else:
                results['broken'].append(f"❌ {name} ({url}) - {response.status_code}")
                print(f"❌ {name}: Error ({response.status_code})")
        except Exception as e:
            results['broken'].append(f"❌ {name} ({url}) - Exception: {str(e)[:50]}")
            print(f"❌ {name}: Exception")
    
    print()
    
    # Test API Endpoints
    print("🔌 Testing API Endpoints")
    print("-" * 80)
    
    api_urls = [
        ('/food/api/dashboard/summary/', 'Dashboard Summary API'),
        ('/food/api/recommendations/', 'Recommendations API'),
        ('/food/api/estimate/waste/', 'Waste Estimation API'),
        ('/food/api/score/sdg/', 'SDG Score API'),
    ]
    
    for url, name in api_urls:
        try:
            response = client.get(url)
            if response.status_code == 200:
                results['working'].append(f"✅ {name} ({url})")
                print(f"✅ {name}: OK")
            else:
                results['broken'].append(f"❌ {name} ({url}) - {response.status_code}")
                print(f"❌ {name}: Error ({response.status_code})")
        except Exception as e:
            results['broken'].append(f"❌ {name} ({url}) - Exception: {str(e)[:50]}")
            print(f"❌ {name}: Exception")
    
    print()
    
    # Test Database Seeding
    print("🌱 Testing Database Content")
    print("-" * 80)
    
    try:
        food_db_count = FoodItemDatabase.objects.count()
        resource_count = Resource.objects.count()
        
        print(f"📊 Food Items Database: {food_db_count} items")
        print(f"📊 Educational Resources: {resource_count} items")
        
        if food_db_count >= 20:
            results['working'].append(f"✅ Food Database Seeded ({food_db_count} items)")
        else:
            results['broken'].append(f"⚠️ Food Database Incomplete ({food_db_count}/20 items)")
        
        if resource_count >= 20:
            results['working'].append(f"✅ Resources Seeded ({resource_count} items)")
        else:
            results['broken'].append(f"⚠️ Resources Incomplete ({resource_count}/20 items)")
            
    except Exception as e:
        print(f"❌ Database check failed: {str(e)}")
        results['broken'].append(f"❌ Database check - {str(e)}")
    
    print()
    
    # Cleanup
    test_user.delete()
    
    return results


def print_summary(results):
    """Print test results summary"""
    
    print()
    print("=" * 80)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 80)
    print()
    
    total_working = len(results['working'])
    total_broken = len(results['broken'])
    total_tests = total_working + total_broken
    
    success_rate = (total_working / total_tests * 100) if total_tests > 0 else 0
    
    print(f"✅ Working Features: {total_working}")
    print(f"❌ Broken Features: {total_broken}")
    print(f"📈 Success Rate: {success_rate:.1f}%")
    print()
    
    if results['broken']:
        print("🔴 BROKEN FEATURES:")
        print("-" * 80)
        for item in results['broken']:
            print(f"  {item}")
        print()
    
    print("=" * 80)
    print("💾 Saving detailed report to feature_test_report.txt")
    
    # Save to file
    with open('feature_test_report.txt', 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("FOODWISE PLATFORM - FEATURE TEST REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Total Tests: {total_tests}\n")
        f.write(f"✅ Working: {total_working}\n")
        f.write(f"❌ Broken: {total_broken}\n")
        f.write(f"📈 Success Rate: {success_rate:.1f}%\n\n")
        
        f.write("=" * 80 + "\n")
        f.write("WORKING FEATURES\n")
        f.write("=" * 80 + "\n")
        for item in results['working']:
            f.write(f"{item}\n")
        
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("BROKEN FEATURES\n")
        f.write("=" * 80 + "\n")
        for item in results['broken']:
            f.write(f"{item}\n")
    
    print("✅ Report saved!")


if __name__ == '__main__':
    try:
        results = test_all_features()
        print_summary(results)
    except Exception as e:
        print(f"\n❌ Fatal error during testing: {str(e)}")
        import traceback
        traceback.print_exc()
