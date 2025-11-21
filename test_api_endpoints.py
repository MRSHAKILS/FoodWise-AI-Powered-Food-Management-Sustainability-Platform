"""
Test API endpoints for PART_6
"""
from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()
client = Client()

# Get or create test user
user = User.objects.first()
if not user:
    print("No users found. Please create a user first.")
    exit()

# Login the user
client.force_login(user)

print(f"\n{'='*60}")
print(f"Testing API Endpoints for User: {user.username}")
print(f"{'='*60}\n")

# Test dashboard summary API
print("1️⃣  Testing /api/dashboard/summary/")
print("-" * 60)
response = client.get(reverse('food:dashboard_summary_api'))
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ API Response:")
    print(f"   Total Inventory Items: {data['total_inventory_items']}")
    print(f"   Total Inventory Value: ${data['total_inventory_value']}")
    print(f"   Recent Logs Count: {data['recent_logs_count']}")
    print(f"   Items Expiring Soon: {data['items_expiring_soon']}")
    print(f"   Most Logged Category: {data['most_logged_category']}")
    print(f"   Category Breakdown: {data['category_breakdown']}")
else:
    print(f"❌ Error: {response.status_code}")

print(f"\n2️⃣  Testing /api/recommendations/")
print("-" * 60)
response = client.get(reverse('food:recommendations_api'))
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"✅ API Response:")
    print(f"   Total Recommendations: {len(data)}")
    for i, rec in enumerate(data[:3], 1):
        print(f"\n   {i}. {rec['resource']['title']}")
        print(f"      Score: {rec['relevance_score']}/10")
        print(f"      Rule: {rec['matched_rule']}")
        print(f"      Category: {rec['resource']['category_display']}")
else:
    print(f"❌ Error: {response.status_code}")

print(f"\n{'='*60}")
print("✅ API endpoint tests completed!")
print(f"{'='*60}\n")
