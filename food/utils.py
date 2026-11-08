"""
Utility functions for dashboard calculations and recommendations
Part of PART_6_BASIC_TRACKING_LOGIC
"""
from django.utils import timezone
from django.db.models import Count, Q, Sum
from datetime import timedelta
from collections import Counter

from food.models import FoodItem, ConsumptionLog
from resources.models import Resource, json_list_contains_any


def calculate_dashboard_summary(user):
    """
    Calculate dashboard summary statistics for a user.
    
    Args:
        user: User object
        
    Returns:
        dict with dashboard metrics:
        - total_inventory_items: count of user's FoodItem objects
        - total_inventory_value: sum of (quantity * price) for all items
        - recent_logs_count: ConsumptionLog count from last 7 days
        - items_expiring_soon: FoodItem count with expiration_date within 7 days
        - expiring_items: queryset of items expiring soon with urgency level
        - most_logged_category: category with highest log count in last 30 days
        - category_breakdown: dict of {category: count} from recent logs
    """
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Get all user's inventory items
    inventory_items = FoodItem.objects.filter(user=user)
    
    # Calculate total inventory items
    total_inventory_items = inventory_items.count()
    
    # Calculate total inventory value
    # Sum of (quantity * price) for items with price
    total_inventory_value = 0
    for item in inventory_items.filter(price__isnull=False):
        total_inventory_value += float(item.quantity) * float(item.price)
    
    # Get recent consumption logs (last 7 days)
    recent_logs = ConsumptionLog.objects.filter(
        user=user,
        consumption_date__gte=week_ago
    )
    recent_logs_count = recent_logs.count()
    
    # Find items expiring within 7 days
    seven_days_from_now = today + timedelta(days=7)
    expiring_soon = inventory_items.filter(
        expiration_date__isnull=False,
        expiration_date__lte=seven_days_from_now,
        expiration_date__gte=today
    )
    items_expiring_soon = expiring_soon.count()
    
    # Add urgency level to expiring items
    expiring_items = []
    for item in expiring_soon:
        days_left = (item.expiration_date - today).days
        if days_left <= 2:
            urgency = 'urgent'
        else:  # 3-7 days
            urgency = 'warning'
        
        expiring_items.append({
            'item': item,
            'days_left': days_left,
            'urgency': urgency
        })
    
    # Sort by urgency (urgent first) then by days left
    expiring_items.sort(key=lambda x: (x['urgency'] == 'warning', x['days_left']))
    
    # Get logs from last 30 days for category analysis
    monthly_logs = ConsumptionLog.objects.filter(
        user=user,
        consumption_date__gte=month_ago
    )
    
    # Find most logged category
    category_counts = monthly_logs.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    most_logged_category = None
    if category_counts:
        most_logged_category = category_counts[0]['category']
    
    # Create category breakdown
    category_breakdown = {
        item['category']: item['count'] 
        for item in category_counts
    }
    
    return {
        'total_inventory_items': total_inventory_items,
        'total_inventory_value': round(total_inventory_value, 2),
        'recent_logs_count': recent_logs_count,
        'items_expiring_soon': items_expiring_soon,
        'expiring_items': expiring_items,
        'most_logged_category': most_logged_category,
        'category_breakdown': category_breakdown,
    }


def generate_recommendations(user):
    """
    Generate personalized resource recommendations based on user's food data.
    
    Implements 5 recommendation rules:
    1. Category Match: If user logged dairy → recommend dairy storage resources
    2. Expiration Warning: If items expiring ≤2 days → recommend expiration/waste resources
    3. Frequent Category: Most frequent category → recommend budget tips
    4. Waste Reduction: Always include 2-3 waste_reduction resources
    5. Storage Tips: Check inventory categories → recommend storage_tips
    
    Args:
        user: User object
        
    Returns:
        list of dicts with:
        - resource: Resource object
        - reason: string explaining why recommended
        - relevance_score: 1-10
        - matched_rule: string identifier
    """
    recommendations = []
    seen_resource_ids = set()
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    # Get user's recent consumption logs
    recent_logs = ConsumptionLog.objects.filter(
        user=user,
        consumption_date__gte=week_ago
    )
    
    # Get user's inventory items
    inventory_items = FoodItem.objects.filter(user=user)
    
    # Get items expiring soon (≤2 days)
    urgent_expiring = inventory_items.filter(
        expiration_date__isnull=False,
        expiration_date__lte=today + timedelta(days=2),
        expiration_date__gte=today
    )
    
    # Get monthly logs for frequency analysis
    monthly_logs = ConsumptionLog.objects.filter(
        user=user,
        consumption_date__gte=month_ago
    )
    
    # Extract categories from logs and inventory
    logged_categories = set(recent_logs.values_list('category', flat=True))
    inventory_categories = set(inventory_items.values_list('category', flat=True))
    
    # Find most frequent category from monthly logs
    category_counts = monthly_logs.values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    most_frequent_category = category_counts[0]['category'] if category_counts else None
    
    
    # RULE 1: Category Match - If user logged dairy → recommend dairy storage resources
    if 'dairy' in logged_categories or 'dairy' in inventory_categories:
        dairy_resources = Resource.objects.filter(
            json_list_contains_any('relevant_food_categories', ['dairy', 'all']),
            category='storage_tips'
        ).exclude(id__in=seen_resource_ids)[:2]
        
        for resource in dairy_resources:
            recommendations.append({
                'resource': resource,
                'reason': 'You have dairy products - learn proper storage techniques',
                'relevance_score': 9,
                'matched_rule': 'category_match'
            })
            seen_resource_ids.add(resource.id)
    
    
    # RULE 2: Expiration Warning - If items expiring ≤2 days → recommend expiration/waste resources
    if urgent_expiring.exists():
        expiring_count = urgent_expiring.count()
        waste_resources = Resource.objects.filter(
            Q(category='waste_reduction') | json_list_contains_any('tags', ['expiration'])
        ).exclude(id__in=seen_resource_ids)[:2]
        
        for resource in waste_resources:
            recommendations.append({
                'resource': resource,
                'reason': f'You have {expiring_count} item(s) expiring within 2 days - reduce waste!',
                'relevance_score': 10,  # Highest priority
                'matched_rule': 'expiration_warning'
            })
            seen_resource_ids.add(resource.id)
    
    
    # RULE 3: Frequent Category - Most frequent category → recommend budget tips
    if most_frequent_category:
        # Map category names between models (if different)
        category_map = {
            'vegetable': 'vegetable',
            'fruit': 'fruit',
            'dairy': 'dairy',
            'meat': 'protein',
            'grain': 'grain',
            'beverage': 'all',
            'snack': 'all',
            'other': 'all',
        }
        
        mapped_category = category_map.get(most_frequent_category, 'all')
        
        budget_resources = Resource.objects.filter(
            json_list_contains_any('relevant_food_categories', [mapped_category, 'all']),
            category='budget_tips'
        ).exclude(id__in=seen_resource_ids)[:2]
        
        for resource in budget_resources:
            recommendations.append({
                'resource': resource,
                'reason': f'You frequently consume {most_frequent_category} - save money with these tips',
                'relevance_score': 8,
                'matched_rule': 'frequent_category'
            })
            seen_resource_ids.add(resource.id)
    
    
    # RULE 4: Waste Reduction - Always include 2-3 waste_reduction resources
    waste_reduction_resources = Resource.objects.filter(
        category='waste_reduction'
    ).exclude(id__in=seen_resource_ids)[:3]
    
    for resource in waste_reduction_resources:
        recommendations.append({
            'resource': resource,
            'reason': 'Essential tips to reduce food waste and save money',
            'relevance_score': 7,
            'matched_rule': 'waste_reduction'
        })
        seen_resource_ids.add(resource.id)
    
    
    # RULE 5: Storage Tips - Check inventory categories → recommend storage_tips
    for category in inventory_categories:
        # Map category names
        category_map = {
            'vegetable': 'vegetable',
            'fruit': 'fruit',
            'dairy': 'dairy',
            'meat': 'protein',
            'grain': 'grain',
            'beverage': 'all',
            'snack': 'all',
            'other': 'all',
        }
        
        mapped_category = category_map.get(category, 'all')
        
        storage_resources = Resource.objects.filter(
            json_list_contains_any('relevant_food_categories', [mapped_category, 'all']),
            category='storage_tips'
        ).exclude(id__in=seen_resource_ids)[:1]
        
        for resource in storage_resources:
            recommendations.append({
                'resource': resource,
                'reason': f'Proper storage tips for your {category} items',
                'relevance_score': 6,
                'matched_rule': 'storage_tips'
            })
            seen_resource_ids.add(resource.id)
    
    
    # Sort by relevance_score (highest first) and return top 5-10
    recommendations.sort(key=lambda x: x['relevance_score'], reverse=True)
    
    # Return top 10 unique recommendations
    return recommendations[:10]
