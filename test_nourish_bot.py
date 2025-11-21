"""
Test NourishBot with user context
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Platform.settings')
django.setup()

from food.ai_services import chat_with_nourish_bot

# Sample user context
user_context = {
    'inventory': [
        {'name': 'Apples', 'quantity': 5, 'expiring_days': 2, 'category': 'fruit'},
        {'name': 'Chicken Breast', 'quantity': 1, 'expiring_days': 3, 'category': 'meat'},
        {'name': 'Milk', 'quantity': 1, 'expiring_days': 5, 'category': 'dairy'},
        {'name': 'Broccoli', 'quantity': 2, 'expiring_days': 4, 'category': 'vegetable'},
    ],
    'recent_consumption': [
        {'name': 'Rice', 'quantity': 200, 'date': '2025-11-20', 'category': 'grain'},
        {'name': 'Carrots', 'quantity': 3, 'date': '2025-11-19', 'category': 'vegetable'},
    ],
    'budget': 100
}

print("=" * 70)
print("TESTING NOURISHBOT WITH USER DATA")
print("=" * 70)
print("\nUser Context:")
print(f"- Inventory: {len(user_context['inventory'])} items")
print(f"- Recent Consumption: {len(user_context['recent_consumption'])} items")
print(f"- Budget: ${user_context['budget']}")
print("\nInventory Details:")
for item in user_context['inventory']:
    print(f"  - {item['name']}: {item['quantity']} units (expires in {item['expiring_days']} days)")

print("\n" + "=" * 70)
print("SENDING MESSAGE TO NOURISHBOT")
print("=" * 70)

message = "What recipes can I make with my items that are expiring soon?"
print(f"\nUser Message: {message}\n")

try:
    response = chat_with_nourish_bot(message, user_context, chat_history=None)
    
    if response:
        print("✅ NourishBot Response:")
        print("-" * 70)
        print(response)
        print("-" * 70)
        print("\n✅ SUCCESS: NourishBot is working with user data!")
    else:
        print("❌ FAILED: NourishBot returned None")
        print("   This could mean:")
        print("   1. API key not configured")
        print("   2. API quota exceeded")
        print("   3. Network connectivity issue")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
    print("\nPossible causes:")
    print("1. GEMINI_API_KEY not set in .env file")
    print("2. Model name incorrect or not available")
    print("3. API quota exceeded")

print("\n" + "=" * 70)
