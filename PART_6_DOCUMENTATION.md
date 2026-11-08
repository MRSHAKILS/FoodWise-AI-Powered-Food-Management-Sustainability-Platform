# PART 6: Basic Tracking Logic - Implementation Guide

## Overview

This document describes the implementation of PART_6_BASIC_TRACKING_LOGIC dashboard calculation functions and recommendation engine.

## Files Created/Modified

### 1. `food/utils.py` (NEW)

Contains two main functions for dashboard analytics and recommendations.

## Function Documentation

### `calculate_dashboard_summary(user)`

**Purpose:** Calculate comprehensive dashboard statistics for a user.

**Parameters:**

- `user`: Django User object

**Returns:** Dictionary with the following keys:

```python
{
    'total_inventory_items': int,        # Count of user's FoodItem objects
    'total_inventory_value': float,      # Sum of (quantity * price) for all items
    'recent_logs_count': int,            # ConsumptionLog count from last 7 days
    'items_expiring_soon': int,          # FoodItem count expiring within 7 days
    'expiring_items': list,              # List of dicts with urgency levels
    'most_logged_category': str,         # Category with highest log count (30 days)
    'category_breakdown': dict,          # {category: count} from recent logs
}
```

**Expiring Items Structure:**

```python
[
    {
        'item': FoodItem,           # Django model instance
        'days_left': int,           # Days until expiration
        'urgency': str,             # 'urgent' (≤2 days) or 'warning' (3-7 days)
    },
    ...
]
```

**Example Usage:**

```python
from food.utils import calculate_dashboard_summary

summary = calculate_dashboard_summary(request.user)
print(f"Total Items: {summary['total_inventory_items']}")
print(f"Value: ${summary['total_inventory_value']}")
print(f"Expiring: {summary['items_expiring_soon']}")
```

---

### `generate_recommendations(user)`

**Purpose:** Generate personalized resource recommendations based on user's food data using 5 intelligent rules.

**Parameters:**

- `user`: Django User object

**Returns:** List of recommendation dictionaries (top 5-10 results)

```python
[
    {
        'resource': Resource,          # Django Resource model instance
        'reason': str,                 # Human-readable explanation
        'relevance_score': int,        # 1-10 (10 = highest priority)
        'matched_rule': str,           # Rule identifier
    },
    ...
]
```

**Recommendation Rules:**

#### Rule 1: Category Match (Score: 9)

- **Trigger:** User has dairy products in logs or inventory
- **Action:** Recommend dairy storage resources
- **Matched Rule:** `'category_match'`
- **Example Reason:** "You have dairy products - learn proper storage techniques"

#### Rule 2: Expiration Warning (Score: 10 - HIGHEST)

- **Trigger:** Items expiring within 2 days
- **Action:** Recommend waste reduction and expiration resources
- **Matched Rule:** `'expiration_warning'`
- **Example Reason:** "You have 3 item(s) expiring within 2 days - reduce waste!"

#### Rule 3: Frequent Category (Score: 8)

- **Trigger:** User's most consumed category (last 30 days)
- **Action:** Recommend budget tips for that category
- **Matched Rule:** `'frequent_category'`
- **Example Reason:** "You frequently consume dairy - save money with these tips"

#### Rule 4: Waste Reduction (Score: 7)

- **Trigger:** Always active
- **Action:** Include 2-3 general waste reduction resources
- **Matched Rule:** `'waste_reduction'`
- **Example Reason:** "Essential tips to reduce food waste and save money"

#### Rule 5: Storage Tips (Score: 6)

- **Trigger:** User has items in specific categories
- **Action:** Recommend storage tips for those categories
- **Matched Rule:** `'storage_tips'`
- **Example Reason:** "Proper storage tips for your vegetable items"

**Category Mapping:**
The function maps FoodItem categories to Resource categories:

```python
{
    'vegetable': 'vegetable',
    'fruit': 'fruit',
    'dairy': 'dairy',
    'meat': 'protein',
    'grain': 'grain',
    'beverage': 'all',
    'snack': 'all',
    'other': 'all',
}
```

**Example Usage:**

```python
from food.utils import generate_recommendations

recommendations = generate_recommendations(request.user)
for rec in recommendations[:5]:
    print(f"[{rec['relevance_score']}/10] {rec['resource'].title}")
    print(f"Reason: {rec['reason']}")
    print(f"Rule: {rec['matched_rule']}\n")
```

---

## API Endpoints

### 1. Dashboard Summary API

**Endpoint:** `GET /food/api/dashboard/summary/`  
**Authentication:** Required (login_required)  
**View Function:** `dashboard_summary_api()`

**Response Format:**

```json
{
  "total_inventory_items": 15,
  "total_inventory_value": 127.5,
  "recent_logs_count": 8,
  "items_expiring_soon": 3,
  "expiring_items": [
    {
      "id": 5,
      "name": "Milk",
      "quantity": 1.0,
      "unit": "liter",
      "category": "dairy",
      "expiration_date": "2025-11-23",
      "days_left": 2,
      "urgency": "urgent"
    }
  ],
  "most_logged_category": "dairy",
  "category_breakdown": {
    "dairy": 12,
    "vegetable": 8,
    "fruit": 5
  }
}
```

### 2. Recommendations API

**Endpoint:** `GET /food/api/recommendations/`  
**Authentication:** Required (login_required)  
**View Function:** `recommendations_api()`

**Response Format:**

```json
[
  {
    "resource": {
      "id": 5,
      "title": "Dairy Storage Best Practices",
      "description": "Learn how to properly store dairy...",
      "category": "storage_tips",
      "category_display": "Storage Tips",
      "type": "guide",
      "type_display": "Guide",
      "url": "https://example.com/dairy-storage",
      "tags": ["dairy", "refrigeration", "storage"],
      "read_time": 5
    },
    "reason": "You have dairy products - learn proper storage techniques",
    "relevance_score": 9,
    "matched_rule": "category_match"
  }
]
```

### 3. Enhanced Dashboard View

**Endpoint:** `GET /food/dashboard/`  
**Authentication:** Required (login_required)  
**View Function:** `enhanced_dashboard()`  
**Template:** `dashboard.html`

Combines both summary and recommendations in a single view for rendering the dashboard page.

---

## URL Configuration

Added to `food/urls.py`:

```python
# Dashboard & Recommendations API (PART 6)
path('api/dashboard/summary/', views.dashboard_summary_api, name='dashboard_summary_api'),
path('api/recommendations/', views.recommendations_api, name='recommendations_api'),
path('dashboard/', views.enhanced_dashboard, name='enhanced_dashboard'),
```

**URL Reversal:**

```python
from django.urls import reverse

# Get URLs
summary_url = reverse('food:dashboard_summary_api')
recommendations_url = reverse('food:recommendations_api')
dashboard_url = reverse('food:enhanced_dashboard')
```

---

## Testing

### Test Script: `test_dashboard_functions.py`

Run with:

```bash
Get-Content test_dashboard_functions.py | python manage.py shell
```

**Output Example:**

```
============================================================
Testing Dashboard Functions for User: testuser
============================================================

=== Dashboard Summary ===

📦 Total Inventory Items: 15
💰 Total Inventory Value: $127.5
📊 Recent Logs (7 days): 8
⏰ Items Expiring Soon: 3
🔝 Most Logged Category: dairy
📈 Category Breakdown: {'dairy': 12, 'vegetable': 8}

⚠️  Expiring Items Details:
   - Milk: 2 days left (urgent)
   - Cheese: 1 days left (urgent)
   - Yogurt: 5 days left (warning)

============================================================
=== Personalized Recommendations ===

📚 Total Recommendations Generated: 10

1. [10/10] First In, First Out (FIFO) Method
   📁 Category: Waste Reduction
   🎯 Rule: expiration_warning
   💡 Reason: You have 3 item(s) expiring within 2 days - reduce waste!

2. [9/10] Dairy Storage Best Practices
   📁 Category: Storage Tips
   🎯 Rule: category_match
   💡 Reason: You have dairy products - learn proper storage techniques
```

---

## Dependencies

**Python Packages:**

- Django (core framework)
- django.utils.timezone (date/time handling)
- django.db.models (Q objects, Count, Sum aggregations)

**Internal Dependencies:**

- `food.models` - FoodItem, ConsumptionLog
- `resources.models` - Resource

---

## Integration Examples

### 1. Use in Template Context

```python
# In your view
from food.utils import calculate_dashboard_summary, generate_recommendations

def my_dashboard_view(request):
    summary = calculate_dashboard_summary(request.user)
    recommendations = generate_recommendations(request.user)

    context = {
        'summary': summary,
        'recommendations': recommendations[:5],  # Top 5
    }
    return render(request, 'my_dashboard.html', context)
```

### 2. Use with AJAX/Fetch

```javascript
// Fetch dashboard summary
fetch("/food/api/dashboard/summary/")
  .then((response) => response.json())
  .then((data) => {
    console.log("Inventory Items:", data.total_inventory_items);
    console.log("Total Value:", data.total_inventory_value);
    console.log("Expiring Soon:", data.items_expiring_soon);
  });

// Fetch recommendations
fetch("/food/api/recommendations/")
  .then((response) => response.json())
  .then((recommendations) => {
    recommendations.forEach((rec) => {
      console.log(`[${rec.relevance_score}] ${rec.resource.title}`);
      console.log(`Reason: ${rec.reason}`);
    });
  });
```

### 3. Use in Management Commands

```python
# custom management command
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from food.utils import generate_recommendations

class Command(BaseCommand):
    def handle(self, *args, **options):
        User = get_user_model()
        for user in User.objects.all():
            recs = generate_recommendations(user)
            print(f"User {user.username}: {len(recs)} recommendations")
```

---

## Performance Considerations

1. **Database Queries:**

   - `calculate_dashboard_summary()`: ~6-8 queries
   - `generate_recommendations()`: ~8-12 queries (depending on user data)

2. **Optimization Tips:**

   - Use `select_related()` for FoodItem queries if needed
   - Cache results for frequently accessed users
   - Consider background tasks for heavy computations

3. **Caching Example:**

```python
from django.core.cache import cache

def get_cached_summary(user):
    cache_key = f'dashboard_summary_{user.id}'
    summary = cache.get(cache_key)

    if not summary:
        summary = calculate_dashboard_summary(user)
        cache.set(cache_key, summary, timeout=300)  # 5 minutes

    return summary
```

---

## Future Enhancements

1. **Additional Rules:**

   - Seasonal recommendations
   - Budget-based recommendations
   - Nutritional balance suggestions

2. **Machine Learning:**

   - User preference learning
   - Collaborative filtering
   - Consumption pattern prediction

3. **Notifications:**

   - Email alerts for urgent expirations
   - Weekly summary emails
   - Push notifications

4. **Analytics:**
   - Historical trend analysis
   - Cost savings tracking
   - Waste reduction metrics

---

## Status: ✅ COMPLETED

PART 6 implementation is complete with:

- ✅ `calculate_dashboard_summary()` function
- ✅ `generate_recommendations()` function
- ✅ 5 recommendation rules implemented
- ✅ API endpoints for dashboard and recommendations
- ✅ Enhanced dashboard view
- ✅ URL routing configured
- ✅ Test scripts created
- ✅ Comprehensive documentation

All functions tested and working correctly!
