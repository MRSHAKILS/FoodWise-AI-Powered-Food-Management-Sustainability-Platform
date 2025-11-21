"""
Custom Admin Analytics Views
Provides dashboard analytics for active users, popular foods, and nutrient trends
"""

from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model
from .models import FoodItem, ConsumptionLog, WasteLog, SDGScore, FoodItemDatabase

User = get_user_model()


class AnalyticsDashboardAdmin(admin.ModelAdmin):
    """
    Custom admin class to add analytics dashboard
    """
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('analytics/', self.admin_site.admin_view(self.analytics_view), name='analytics_dashboard'),
        ]
        return custom_urls + urls
    
    def analytics_view(self, request):
        """Main analytics dashboard view"""
        
        # Time ranges
        today = timezone.now().date()
        last_7_days = today - timedelta(days=7)
        last_30_days = today - timedelta(days=30)
        last_90_days = today - timedelta(days=90)
        
        # ===== ACTIVE USERS ANALYTICS =====
        total_users = User.objects.filter(is_active=True).count()
        
        # Active users by time period
        users_today = User.objects.filter(
            last_login__date=today
        ).count()
        
        users_this_week = User.objects.filter(
            last_login__gte=last_7_days
        ).count()
        
        users_this_month = User.objects.filter(
            last_login__gte=last_30_days
        ).count()
        
        # New registrations
        new_users_this_week = User.objects.filter(
            date_joined__gte=last_7_days
        ).count()
        
        new_users_this_month = User.objects.filter(
            date_joined__gte=last_30_days
        ).count()
        
        # User engagement levels
        highly_active_users = User.objects.filter(
            fooditem__created_at__gte=last_7_days
        ).annotate(
            item_count=Count('fooditem')
        ).filter(item_count__gte=5).count()
        
        # Top active users with their activity
        top_users = User.objects.annotate(
            inventory_count=Count('fooditem', filter=Q(fooditem__created_at__gte=last_30_days)),
            consumption_count=Count('consumptionlog', filter=Q(consumptionlog__created_at__gte=last_30_days)),
            total_activity=F('inventory_count') + F('consumption_count')
        ).order_by('-total_activity')[:10]
        
        # ===== POPULAR FOODS ANALYTICS =====
        
        # Most added items to inventory (last 30 days)
        popular_inventory_items = FoodItem.objects.filter(
            created_at__gte=last_30_days
        ).values('name', 'category').annotate(
            count=Count('id'),
            avg_quantity=Avg('quantity')
        ).order_by('-count')[:15]
        
        # Most consumed items (last 30 days)
        popular_consumed_items = ConsumptionLog.objects.filter(
            consumption_date__gte=last_30_days
        ).values('item_name', 'category').annotate(
            count=Count('id'),
            total_quantity=Sum('quantity')
        ).order_by('-count')[:15]
        
        # Most wasted items (last 30 days)
        most_wasted_items = WasteLog.objects.filter(
            waste_date__gte=last_30_days
        ).values('item_name', 'category', 'reason').annotate(
            count=Count('id'),
            total_cost=Sum('estimated_cost')
        ).order_by('-total_cost')[:15]
        
        # Category distribution
        category_distribution = FoodItem.objects.filter(
            created_at__gte=last_30_days
        ).values('category').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Database items popularity (based on usage)
        database_item_usage = FoodItemDatabase.objects.annotate(
            usage_count=Count('fooditem', filter=Q(fooditem__created_at__gte=last_90_days))
        ).filter(usage_count__gt=0).order_by('-usage_count')[:20]
        
        # ===== NUTRIENT & HEALTH TRENDS =====
        
        # Consumption by category over time
        consumption_trends = ConsumptionLog.objects.filter(
            consumption_date__gte=last_30_days
        ).values('category', 'consumption_date').annotate(
            daily_count=Count('id')
        ).order_by('consumption_date')
        
        # Average SDG scores
        avg_sdg_scores = SDGScore.objects.filter(
            calculated_date__gte=last_30_days
        ).aggregate(
            avg_total=Avg('score'),
            avg_waste=Avg('waste_reduction_score'),
            avg_nutrition=Avg('nutrition_score'),
            avg_budget=Avg('budget_efficiency_score')
        )
        
        # Top performers by SDG score
        top_sdg_users = SDGScore.objects.filter(
            calculated_date__gte=last_30_days
        ).values('user__username').annotate(
            avg_score=Avg('score')
        ).order_by('-avg_score')[:10]
        
        # Waste reduction trends
        waste_trends = WasteLog.objects.filter(
            waste_date__gte=last_90_days
        ).extra(
            select={'week': 'EXTRACT(week FROM waste_date)'}
        ).values('week').annotate(
            total_cost=Sum('estimated_cost'),
            item_count=Count('id')
        ).order_by('week')
        
        # Budget efficiency
        budget_stats = User.objects.filter(
            is_active=True,
            budget_limit__isnull=False
        ).aggregate(
            avg_budget=Avg('budget_limit'),
            total_users_with_budget=Count('id')
        )
        
        # ===== SYSTEM HEALTH METRICS =====
        
        # Inventory health
        expired_items = FoodItem.objects.filter(
            expiration_date__lt=today
        ).count()
        
        expiring_soon = FoodItem.objects.filter(
            expiration_date__gte=today,
            expiration_date__lte=today + timedelta(days=3)
        ).count()
        
        total_inventory = FoodItem.objects.count()
        
        # Data completeness
        items_with_expiry = FoodItem.objects.filter(
            expiration_date__isnull=False
        ).count()
        
        items_with_price = FoodItem.objects.filter(
            price__isnull=False
        ).count()
        
        # ===== CATEGORY INSIGHTS =====
        
        # Get category-wise statistics
        category_stats = {}
        for category_code, category_name in FoodItem.CATEGORY_CHOICES:
            stats = {
                'name': category_name,
                'inventory_count': FoodItem.objects.filter(category=category_code).count(),
                'consumption_count': ConsumptionLog.objects.filter(
                    category=category_code,
                    consumption_date__gte=last_30_days
                ).count(),
                'waste_count': WasteLog.objects.filter(
                    category=category_code,
                    waste_date__gte=last_30_days
                ).count(),
            }
            if stats['inventory_count'] > 0 or stats['consumption_count'] > 0:
                category_stats[category_code] = stats
        
        context = {
            'title': 'Analytics Dashboard',
            'site_title': 'Admin Analytics',
            
            # User analytics
            'total_users': total_users,
            'users_today': users_today,
            'users_this_week': users_this_week,
            'users_this_month': users_this_month,
            'new_users_this_week': new_users_this_week,
            'new_users_this_month': new_users_this_month,
            'highly_active_users': highly_active_users,
            'top_users': top_users,
            
            # Popular foods
            'popular_inventory_items': popular_inventory_items,
            'popular_consumed_items': popular_consumed_items,
            'most_wasted_items': most_wasted_items,
            'category_distribution': category_distribution,
            'database_item_usage': database_item_usage,
            
            # Trends
            'consumption_trends': consumption_trends,
            'avg_sdg_scores': avg_sdg_scores,
            'top_sdg_users': top_sdg_users,
            'waste_trends': waste_trends,
            'budget_stats': budget_stats,
            
            # System health
            'expired_items': expired_items,
            'expiring_soon': expiring_soon,
            'total_inventory': total_inventory,
            'items_with_expiry': items_with_expiry,
            'items_with_price': items_with_price,
            
            # Category insights
            'category_stats': category_stats,
            
            # Date context
            'today': today,
            'last_7_days': last_7_days,
            'last_30_days': last_30_days,
        }
        
        return render(request, 'admin/analytics_dashboard.html', context)


# Register a dummy model to get the analytics link in admin
admin.site.register(FoodItemDatabase, AnalyticsDashboardAdmin)
