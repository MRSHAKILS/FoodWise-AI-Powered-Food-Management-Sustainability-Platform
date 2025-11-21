"""
Test script for PART_6 dashboard calculation functions
"""
from django.contrib.auth import get_user_model
from food.utils import calculate_dashboard_summary, generate_recommendations

User = get_user_model()
user = User.objects.first()

if not user:
    print("No users found in database. Please create a user first.")
    exit()

print(f"\n{'='*60}")
print(f"Testing Dashboard Functions for User: {user.username}")
print(f"{'='*60}\n")

# Test calculate_dashboard_summary
print("=== Dashboard Summary ===\n")
summary = calculate_dashboard_summary(user)

print(f"📦 Total Inventory Items: {summary['total_inventory_items']}")
print(f"💰 Total Inventory Value: ${summary['total_inventory_value']}")
print(f"📊 Recent Logs (7 days): {summary['recent_logs_count']}")
print(f"⏰ Items Expiring Soon: {summary['items_expiring_soon']}")
print(f"🔝 Most Logged Category: {summary['most_logged_category']}")
print(f"📈 Category Breakdown: {summary['category_breakdown']}")

if summary['expiring_items']:
    print(f"\n⚠️  Expiring Items Details:")
    for item_data in summary['expiring_items']:
        item = item_data['item']
        print(f"   - {item.name}: {item_data['days_left']} days left ({item_data['urgency']})")

# Test generate_recommendations
print(f"\n\n{'='*60}")
print("=== Personalized Recommendations ===\n")
recs = generate_recommendations(user)

print(f"📚 Total Recommendations Generated: {len(recs)}\n")

for i, rec in enumerate(recs, 1):
    print(f"{i}. [{rec['relevance_score']}/10] {rec['resource'].title}")
    print(f"   📁 Category: {rec['resource'].get_category_display()}")
    print(f"   🎯 Rule: {rec['matched_rule']}")
    print(f"   💡 Reason: {rec['reason']}")
    print()

print(f"{'='*60}")
print("✅ All tests completed successfully!")
print(f"{'='*60}\n")
