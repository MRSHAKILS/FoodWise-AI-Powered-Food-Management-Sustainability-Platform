from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import FoodItem, ConsumptionLog, FoodItemDatabase, MealPlan, FoodSurplus

User = get_user_model()


def analytics_view(request):
    """Analytics dashboard view showing system metrics"""
    
    # Time ranges
    today = timezone.now().date()
    last_7_days = today - timedelta(days=7)
    last_30_days = today - timedelta(days=30)
    
    # User analytics
    total_users = User.objects.filter(is_active=True).count()
    users_today = User.objects.filter(last_login__date=today).count()
    users_this_week = User.objects.filter(last_login__gte=last_7_days).count()
    users_this_month = User.objects.filter(last_login__gte=last_30_days).count()
    new_users_this_week = User.objects.filter(date_joined__gte=last_7_days).count()
    new_users_this_month = User.objects.filter(date_joined__gte=last_30_days).count()
    
    # Top active users
    top_users = User.objects.annotate(
        inventory_count=Count('food_items', filter=Q(food_items__created_at__gte=last_30_days)),
        consumption_count=Count('consumption_logs', filter=Q(consumption_logs__created_at__gte=last_30_days)),
        total_activity=F('inventory_count') + F('consumption_count')
    ).order_by('-total_activity')[:10]
    
    # Popular foods
    popular_inventory_items = FoodItem.objects.filter(
        created_at__gte=last_30_days
    ).values('name', 'category').annotate(
        count=Count('id')
    ).order_by('-count')[:15]
    
    popular_consumed_items = ConsumptionLog.objects.filter(
        consumption_date__gte=last_30_days
    ).values('item_name', 'category').annotate(
        count=Count('id')
    ).order_by('-count')[:15]
    
    # Category distribution
    category_distribution = FoodItem.objects.filter(
        created_at__gte=last_30_days
    ).values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # System health
    expired_items = FoodItem.objects.filter(expiration_date__lt=today).count()
    expiring_soon = FoodItem.objects.filter(
        expiration_date__gte=today,
        expiration_date__lte=today + timedelta(days=3)
    ).count()
    total_inventory = FoodItem.objects.count()
    
    # Surplus stats
    surplus_stats = {
        'total': FoodSurplus.objects.count(),
        'available': FoodSurplus.objects.filter(status='available').count(),
        'completed': FoodSurplus.objects.filter(status='completed').count(),
    }
    
    context = {
        'title': 'Analytics Dashboard',
        'total_users': total_users,
        'users_today': users_today,
        'users_this_week': users_this_week,
        'users_this_month': users_this_month,
        'new_users_this_week': new_users_this_week,
        'new_users_this_month': new_users_this_month,
        'top_users': top_users,
        'popular_inventory_items': popular_inventory_items,
        'popular_consumed_items': popular_consumed_items,
        'category_distribution': category_distribution,
        'expired_items': expired_items,
        'expiring_soon': expiring_soon,
        'total_inventory': total_inventory,
        'surplus_stats': surplus_stats,
        'today': today,
    }
    
    return render(request, 'admin/analytics_dashboard.html', context)


@admin.register(FoodItemDatabase)
class FoodItemDatabaseAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'category', 'typical_expiration_days', 'sample_cost_per_unit', 'unit', 'has_nutritional_info', 'created_at']
    list_filter = ['category', 'unit', 'created_at']
    search_fields = ['item_name', 'storage_instructions', 'nutritional_info']
    ordering = ['item_name']
    readonly_fields = ['created_at']
    list_per_page = 50
    list_editable = ['category', 'typical_expiration_days', 'sample_cost_per_unit']
    
    def has_nutritional_info(self, obj):
        return bool(obj.nutritional_info)
    has_nutritional_info.boolean = True
    has_nutritional_info.short_description = 'Has Nutrition Data'


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'quantity', 'unit', 'category', 'purchase_date', 'expiration_date', 'is_expired', 'days_remaining']
    list_filter = ['category', 'purchase_date', 'expiration_date', 'user']
    search_fields = ['name', 'user__username', 'user__email', 'notes']
    date_hierarchy = 'purchase_date'
    ordering = ['-created_at']
    list_per_page = 50
    
    def days_remaining(self, obj):
        days = obj.days_until_expiration
        if days is None:
            return 'N/A'
        if days < 0:
            return f'Expired {abs(days)} days ago'
        elif days == 0:
            return 'Expires today!'
        else:
            return f'{days} days'
    days_remaining.short_description = 'Days Until Expiry'


@admin.register(ConsumptionLog)
class ConsumptionLogAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'user', 'quantity', 'unit', 'category', 'consumption_date', 'created_at']
    list_filter = ['category', 'consumption_date', 'user', 'created_at']
    search_fields = ['item_name', 'user__username', 'user__email']
    date_hierarchy = 'consumption_date'
    ordering = ['-consumption_date', '-created_at']
    list_per_page = 100


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'week_start_date', 'total_cost', 'budget_limit', 'nutrition_score', 'generated_by', 'is_active', 'created_at']
    list_filter = ['generated_by', 'is_active', 'week_start_date']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'week_start_date'
    ordering = ['-week_start_date', '-created_at']
    readonly_fields = ['created_at']


@admin.register(FoodSurplus)
class FoodSurplusAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'donor', 'recipient', 'quantity', 'unit', 'category', 'status', 'pickup_location', 'available_until', 'is_available_status']
    list_filter = ['status', 'category', 'created_at', 'available_until']
    search_fields = ['item_name', 'donor__username', 'recipient__username', 'pickup_location', 'description']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'is_available_status', 'time_remaining_display']
    list_per_page = 50
    
    def is_available_status(self, obj):
        return obj.is_available
    is_available_status.boolean = True
    is_available_status.short_description = 'Currently Available'
    
    def time_remaining_display(self, obj):
        return obj.time_remaining if obj.is_available else 'Expired/Unavailable'
    time_remaining_display.short_description = 'Time Remaining'
