from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count, Sum, Avg, Q, F
from datetime import timedelta
from .models import FoodItem, ConsumptionLog, FoodItemDatabase, MealPlan, SDGScore, WasteLog, ChatSession


class AnalyticsDashboardAdmin(admin.ModelAdmin):
    """Admin dashboard for viewing analytics and metrics"""
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='food_analytics_dashboard'),
        ]
        return custom_urls + urls
    
    def analytics_view(self, request):
        """Main analytics dashboard view"""
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Time periods
        today = timezone.now().date()
        now = timezone.now()
        week_ago = now - timedelta(days=7)
        month_ago = now - timedelta(days=30)
        
        # USER ACTIVITY METRICS
        total_users = User.objects.count()
        users_today = User.objects.filter(last_login__date=today).count()
        users_this_week = User.objects.filter(last_login__gte=week_ago).count()
        users_this_month = User.objects.filter(last_login__gte=month_ago).count()
        new_users_this_week = User.objects.filter(date_joined__gte=week_ago).count()
        new_users_this_month = User.objects.filter(date_joined__gte=month_ago).count()
        
        # Highly active users (5+ activities this week)
        highly_active_users = User.objects.annotate(
            activity_count=Count('food_items', filter=Q(food_items__created_at__gte=week_ago)) +
                         Count('consumption_logs', filter=Q(consumption_logs__created_at__gte=week_ago))
        ).filter(activity_count__gte=5).count()
        
        # Top 10 most active users (last 30 days)
        top_users = User.objects.annotate(
            inventory_count=Count('food_items', filter=Q(food_items__created_at__gte=month_ago)),
            consumption_count=Count('consumption_logs', filter=Q(consumption_logs__created_at__gte=month_ago)),
            total_activity=F('inventory_count') + F('consumption_count')
        ).filter(total_activity__gt=0).order_by('-total_activity')[:10]
        
        # POPULAR FOODS
        popular_inventory_items = FoodItem.objects.filter(
            created_at__gte=month_ago
        ).values('name', 'category').annotate(
            count=Count('id')
        ).order_by('-count')[:15]
        
        popular_consumed_items = ConsumptionLog.objects.filter(
            consumption_date__gte=month_ago
        ).values('item_name', 'category').annotate(
            count=Count('id')
        ).order_by('-count')[:15]
        
        most_wasted_items = WasteLog.objects.filter(
            waste_date__gte=month_ago
        ).values('item_name', 'category', 'reason').annotate(
            count=Count('id'),
            total_cost=Sum('estimated_cost')
        ).order_by('-count')[:15]
        
        # CATEGORY DISTRIBUTION
        category_distribution = FoodItem.objects.filter(
            created_at__gte=month_ago
        ).values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # TRENDS & SCORES
        consumption_trends = ConsumptionLog.objects.filter(
            consumption_date__gte=month_ago
        ).extra(
            select={'date': 'DATE(consumption_date)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        avg_sdg_scores = SDGScore.objects.filter(
            calculated_date__gte=month_ago
        ).aggregate(
            avg_total=Avg('score'),
            avg_waste=Avg('waste_reduction_score'),
            avg_nutrition=Avg('nutrition_score'),
            avg_budget=Avg('budget_efficiency_score')
        )
        
        # Top SDG performers (last 30 days)
        top_sdg_users = SDGScore.objects.filter(
            calculated_date__gte=month_ago
        ).values('user__username').annotate(
            avg_score=Avg('score')
        ).order_by('-avg_score')[:10]
        
        waste_trends = WasteLog.objects.filter(
            waste_date__gte=month_ago
        ).extra(
            select={'week': 'strftime("%%Y-%%W", waste_date)'}
        ).values('week').annotate(
            count=Count('id'),
            total_cost=Sum('estimated_cost')
        ).order_by('week')
        
        # SYSTEM HEALTH
        total_inventory = FoodItem.objects.count()
        expired_items = FoodItem.objects.filter(expiration_date__lt=today).count()
        expiring_soon = FoodItem.objects.filter(
            expiration_date__gte=today,
            expiration_date__lte=today + timedelta(days=3)
        ).count()
        
        items_with_expiry = FoodItem.objects.filter(expiration_date__isnull=False).count()
        
        # CATEGORY INSIGHTS
        category_stats = {}
        categories = FoodItem.CATEGORY_CHOICES
        for code, name in categories:
            category_stats[code] = {
                'name': name,
                'inventory_count': FoodItem.objects.filter(category=code).count(),
                'consumption_count': ConsumptionLog.objects.filter(
                    category=code, consumption_date__gte=month_ago
                ).count(),
                'waste_count': WasteLog.objects.filter(
                    category=code, waste_date__gte=month_ago
                ).count()
            }
        
        context = {
            'title': 'Analytics Dashboard',
            'today': today,
            # User metrics
            'total_users': total_users,
            'users_today': users_today,
            'users_this_week': users_this_week,
            'users_this_month': users_this_month,
            'new_users_this_week': new_users_this_week,
            'new_users_this_month': new_users_this_month,
            'highly_active_users': highly_active_users,
            'top_users': top_users,
            # Food popularity
            'popular_inventory_items': popular_inventory_items,
            'popular_consumed_items': popular_consumed_items,
            'most_wasted_items': most_wasted_items,
            'category_distribution': category_distribution,
            # Trends
            'consumption_trends': consumption_trends,
            'avg_sdg_scores': avg_sdg_scores,
            'top_sdg_users': top_sdg_users,
            'waste_trends': waste_trends,
            # System health
            'total_inventory': total_inventory,
            'expired_items': expired_items,
            'expiring_soon': expiring_soon,
            'items_with_expiry': items_with_expiry,
            'category_stats': category_stats,
        }
        
        return render(request, 'admin/analytics_dashboard.html', context)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False


# Create a custom admin site class to add analytics URL
class CustomAdminSite(admin.AdminSite):
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('food/analytics/', self.admin_view(analytics_view_function), name='food_analytics_dashboard'),
        ]
        return custom_urls + urls


def analytics_view_function(request):
    """Standalone analytics view function"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Time periods
    today = timezone.now().date()
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    # USER ACTIVITY METRICS
    total_users = User.objects.count()
    users_today = User.objects.filter(last_login__date=today).count()
    users_this_week = User.objects.filter(last_login__gte=week_ago).count()
    users_this_month = User.objects.filter(last_login__gte=month_ago).count()
    new_users_this_week = User.objects.filter(date_joined__gte=week_ago).count()
    new_users_this_month = User.objects.filter(date_joined__gte=month_ago).count()
    
    # Highly active users (5+ activities this week)
    highly_active_users = User.objects.annotate(
        activity_count=Count('food_items', filter=Q(food_items__created_at__gte=week_ago)) +
                     Count('consumption_logs', filter=Q(consumption_logs__created_at__gte=week_ago))
    ).filter(activity_count__gte=5).count()
    
    # Top 10 most active users (last 30 days)
    top_users = User.objects.annotate(
        inventory_count=Count('food_items', filter=Q(food_items__created_at__gte=month_ago)),
        consumption_count=Count('consumption_logs', filter=Q(consumption_logs__created_at__gte=month_ago)),
        total_activity=F('inventory_count') + F('consumption_count')
    ).filter(total_activity__gt=0).order_by('-total_activity')[:10]
    
    # POPULAR FOODS
    popular_inventory_items = FoodItem.objects.filter(
        created_at__gte=month_ago
    ).values('name', 'category').annotate(
        count=Count('id')
    ).order_by('-count')[:15]
    
    popular_consumed_items = ConsumptionLog.objects.filter(
        consumption_date__gte=month_ago
    ).values('item_name', 'category').annotate(
        count=Count('id')
    ).order_by('-count')[:15]
    
    most_wasted_items = WasteLog.objects.filter(
        waste_date__gte=month_ago
    ).values('item_name', 'category', 'reason').annotate(
        count=Count('id'),
        total_cost=Sum('estimated_cost')
    ).order_by('-count')[:15]
    
    # CATEGORY DISTRIBUTION
    category_distribution = FoodItem.objects.filter(
        created_at__gte=month_ago
    ).values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # TRENDS & SCORES
    consumption_trends = ConsumptionLog.objects.filter(
        consumption_date__gte=month_ago
    ).extra(
        select={'date': 'DATE(consumption_date)'}
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    avg_sdg_scores = SDGScore.objects.filter(
        calculated_date__gte=month_ago
    ).aggregate(
        avg_total=Avg('score'),
        avg_waste=Avg('waste_reduction_score'),
        avg_nutrition=Avg('nutrition_score'),
        avg_budget=Avg('budget_efficiency_score')
    )
    
    # Top SDG performers (last 30 days)
    top_sdg_users = SDGScore.objects.filter(
        calculated_date__gte=month_ago
    ).values('user__username').annotate(
        avg_score=Avg('score')
    ).order_by('-avg_score')[:10]
    
    waste_trends = WasteLog.objects.filter(
        waste_date__gte=month_ago
    ).extra(
        select={'week': 'strftime("%%Y-%%W", waste_date)'}
    ).values('week').annotate(
        count=Count('id'),
        total_cost=Sum('estimated_cost')
    ).order_by('week')
    
    # SYSTEM HEALTH
    total_inventory = FoodItem.objects.count()
    expired_items = FoodItem.objects.filter(expiration_date__lt=today).count()
    expiring_soon = FoodItem.objects.filter(
        expiration_date__gte=today,
        expiration_date__lte=today + timedelta(days=3)
    ).count()
    
    items_with_expiry = FoodItem.objects.filter(expiration_date__isnull=False).count()
    
    # CATEGORY INSIGHTS
    category_stats = {}
    categories = FoodItem.CATEGORY_CHOICES
    for code, name in categories:
        category_stats[code] = {
            'name': name,
            'inventory_count': FoodItem.objects.filter(category=code).count(),
            'consumption_count': ConsumptionLog.objects.filter(
                category=code, consumption_date__gte=month_ago
            ).count(),
            'waste_count': WasteLog.objects.filter(
                category=code, waste_date__gte=month_ago
            ).count()
        }
    
    context = {
        'title': 'Analytics Dashboard',
        'today': today,
        # User metrics
        'total_users': total_users,
        'users_today': users_today,
        'users_this_week': users_this_week,
        'users_this_month': users_this_month,
        'new_users_this_week': new_users_this_week,
        'new_users_this_month': new_users_this_month,
        'highly_active_users': highly_active_users,
        'top_users': top_users,
        # Food popularity
        'popular_inventory_items': popular_inventory_items,
        'popular_consumed_items': popular_consumed_items,
        'most_wasted_items': most_wasted_items,
        'category_distribution': category_distribution,
        # Trends
        'consumption_trends': consumption_trends,
        'avg_sdg_scores': avg_sdg_scores,
        'top_sdg_users': top_sdg_users,
        'waste_trends': waste_trends,
        # System health
        'total_inventory': total_inventory,
        'expired_items': expired_items,
        'expiring_soon': expiring_soon,
        'items_with_expiry': items_with_expiry,
        'category_stats': category_stats,
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
    actions = ['export_as_json', 'duplicate_items']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('item_name', 'category', 'unit')
        }),
        ('Expiration & Pricing', {
            'fields': ('typical_expiration_days', 'sample_cost_per_unit'),
            'classes': ('collapse',)
        }),
        ('Nutrition & Storage', {
            'fields': ('nutritional_info', 'storage_instructions'),
            'classes': ('collapse',)
        }),
        ('Media', {
            'fields': ('image_url',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_nutritional_info(self, obj):
        return bool(obj.nutritional_info)
    has_nutritional_info.boolean = True
    has_nutritional_info.short_description = 'Has Nutrition Data'
    
    def export_as_json(self, request, queryset):
        import json
        from django.http import JsonResponse
        data = list(queryset.values())
        return JsonResponse(data, safe=False)
    export_as_json.short_description = 'Export selected as JSON'
    
    def duplicate_items(self, request, queryset):
        for item in queryset:
            item.pk = None
            item.item_name = f"{item.item_name} (Copy)"
            item.save()
        self.message_user(request, f"{queryset.count()} items duplicated successfully.")
    duplicate_items.short_description = 'Duplicate selected items'


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'quantity', 'unit', 'category', 'purchase_date', 'expiration_date', 'is_expired', 'days_remaining']
    list_filter = ['category', 'purchase_date', 'expiration_date', 'user']
    search_fields = ['name', 'user__username', 'user__email', 'notes']
    date_hierarchy = 'purchase_date'
    ordering = ['-created_at']
    list_per_page = 50
    actions = ['mark_as_consumed', 'extend_expiration']
    
    fieldsets = (
        ('Item Details', {
            'fields': ('user', 'name', 'category')
        }),
        ('Quantity & Pricing', {
            'fields': ('quantity', 'unit', 'price')
        }),
        ('Dates', {
            'fields': ('purchase_date', 'expiration_date')
        }),
        ('Additional Info', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
    )
    
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
    
    def mark_as_consumed(self, request, queryset):
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} items marked as consumed and removed.")
    mark_as_consumed.short_description = 'Mark as consumed (delete)'
    
    def extend_expiration(self, request, queryset):
        from datetime import timedelta
        for item in queryset:
            if item.expiration_date:
                item.expiration_date += timedelta(days=7)
                item.save()
        self.message_user(request, f"{queryset.count()} items extended by 7 days.")
    extend_expiration.short_description = 'Extend expiration by 7 days'


@admin.register(ConsumptionLog)
class ConsumptionLogAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'user', 'quantity', 'unit', 'category', 'consumption_date', 'created_at']
    list_filter = ['category', 'consumption_date', 'user', 'created_at']
    search_fields = ['item_name', 'user__username', 'user__email']
    date_hierarchy = 'consumption_date'
    ordering = ['-consumption_date', '-created_at']
    list_per_page = 100
    actions = ['export_consumption_report']
    
    def export_consumption_report(self, request, queryset):
        from django.db.models import Count, Sum
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="consumption_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Item Name', 'User', 'Quantity', 'Unit', 'Category', 'Date'])
        
        for log in queryset:
            writer.writerow([log.item_name, log.user.username, log.quantity, log.unit, log.category, log.consumption_date])
        
        return response
    export_consumption_report.short_description = 'Export as CSV'


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    list_display = ['user', 'week_start_date', 'total_cost', 'budget_limit', 'nutrition_score', 'generated_by', 'is_active', 'created_at']
    list_filter = ['generated_by', 'is_active', 'week_start_date']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'week_start_date'
    ordering = ['-week_start_date', '-created_at']
    readonly_fields = ['created_at']


@admin.register(SDGScore)
class SDGScoreAdmin(admin.ModelAdmin):
    list_display = ['user', 'score', 'waste_reduction_score', 'nutrition_score', 'budget_efficiency_score', 'week_number', 'year', 'calculated_date']
    list_filter = ['year', 'week_number', 'calculated_date']
    search_fields = ['user__username', 'user__email']
    date_hierarchy = 'calculated_date'
    ordering = ['-calculated_date']
    readonly_fields = ['calculated_date']


@admin.register(WasteLog)
class WasteLogAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'user', 'quantity', 'unit', 'category', 'reason', 'estimated_cost', 'waste_date', 'cost_impact']
    list_filter = ['category', 'reason', 'waste_date', 'user']
    search_fields = ['item_name', 'user__username', 'user__email']
    date_hierarchy = 'waste_date'
    ordering = ['-waste_date', '-created_at']
    list_per_page = 50
    actions = ['calculate_total_waste', 'export_waste_report']
    
    fieldsets = (
        ('Waste Details', {
            'fields': ('user', 'item_name', 'category', 'reason')
        }),
        ('Quantity & Cost', {
            'fields': ('quantity', 'unit', 'estimated_cost')
        }),
        ('Date', {
            'fields': ('waste_date',)
        }),
    )
    
    def cost_impact(self, obj):
        if obj.estimated_cost:
            cost = float(obj.estimated_cost)
            if cost > 10:
                return f'${cost:.2f} 🔴'
            elif cost > 5:
                return f'${cost:.2f} 🟡'
            else:
                return f'${cost:.2f} 🟢'
        return 'N/A'
    cost_impact.short_description = 'Cost Impact'
    
    def calculate_total_waste(self, request, queryset):
        from django.db.models import Sum
        total = queryset.aggregate(Sum('estimated_cost'))['estimated_cost__sum'] or 0
        self.message_user(request, f"Total waste cost: ${total:.2f} for {queryset.count()} items.")
    calculate_total_waste.short_description = 'Calculate total waste cost'
    
    def export_waste_report(self, request, queryset):
        from django.http import HttpResponse
        import csv
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="waste_report.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Item', 'User', 'Quantity', 'Unit', 'Category', 'Reason', 'Cost', 'Date'])
        
        for log in queryset:
            writer.writerow([log.item_name, log.user.username, log.quantity, log.unit, 
                           log.category, log.reason, log.estimated_cost, log.waste_date])
        
        return response
    export_waste_report.short_description = 'Export waste data as CSV'


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'message_count', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at', 'user']
    search_fields = ['session_id', 'user__username', 'user__email', 'messages']
    date_hierarchy = 'created_at'
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at', 'message_preview']
    list_per_page = 50
    actions = ['deactivate_sessions', 'clear_messages']
    
    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'user', 'is_active')
        }),
        ('Messages', {
            'fields': ('messages', 'message_preview'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def message_count(self, obj):
        try:
            import json
            messages = json.loads(obj.messages) if obj.messages else []
            return len(messages)
        except:
            return 0
    message_count.short_description = 'Messages'
    
    def message_preview(self, obj):
        try:
            import json
            messages = json.loads(obj.messages) if obj.messages else []
            if messages:
                preview = "\n".join([f"{msg.get('role', 'unknown')}: {msg.get('content', '')[:100]}..." for msg in messages[-3:]])
                return preview or "No messages"
            return "No messages"
        except:
            return "Error loading messages"
    message_preview.short_description = 'Recent Messages'
    
    def deactivate_sessions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} sessions deactivated.")
    deactivate_sessions.short_description = 'Deactivate selected sessions'
    
    def clear_messages(self, request, queryset):
        queryset.update(messages='[]')
        self.message_user(request, f"Messages cleared for {queryset.count()} sessions.")
    clear_messages.short_description = 'Clear messages (keep session)'
