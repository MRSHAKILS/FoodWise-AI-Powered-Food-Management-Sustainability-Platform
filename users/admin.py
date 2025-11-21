from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Avg, Q
from django.utils.html import format_html
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 
                    'activity_status', 'inventory_count', 'total_waste_cost']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined', 'last_login']
    search_fields = ['username', 'first_name', 'last_name', 'email']
    ordering = ['-date_joined']
    date_hierarchy = 'date_joined'
    actions = ['activate_users', 'deactivate_users', 'send_welcome_email']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {
            'fields': ('budget_limit',),
            'classes': ('collapse',)
        }),
    )
    
    def activity_status(self, obj):
        """Show user activity status with color coding"""
        if not obj.last_login:
            return format_html('<span style="color: gray;">⚪ Never logged in</span>')
        
        days_since_login = (timezone.now() - obj.last_login).days
        
        if days_since_login == 0:
            return format_html('<span style="color: green;">🟢 Active today</span>')
        elif days_since_login <= 7:
            return format_html('<span style="color: blue;">🔵 Active this week</span>')
        elif days_since_login <= 30:
            return format_html('<span style="color: orange;">🟡 Active this month</span>')
        else:
            return format_html('<span style="color: red;">🔴 Inactive >{} days</span>', days_since_login)
    
    activity_status.short_description = 'Activity Status'
    activity_status.admin_order_field = 'last_login'
    
    def inventory_count(self, obj):
        """Show count of user's inventory items"""
        from food.models import FoodItem
        count = FoodItem.objects.filter(user=obj).count()
        if count > 0:
            return format_html('<strong>{}</strong> items', count)
        return '0 items'
    
    inventory_count.short_description = 'Inventory Items'
    
    def total_waste_cost(self, obj):
        """Show total waste cost for user"""
        from food.models import WasteLog
        total = WasteLog.objects.filter(user=obj).aggregate(
            total=Sum('estimated_cost')
        )['total'] or 0
        
        if total > 50:
            color = 'red'
        elif total > 20:
            color = 'orange'
        else:
            color = 'green'
        
        return format_html('<span style="color: {};"><strong>${:.2f}</strong></span>', color, float(total))
    
    total_waste_cost.short_description = 'Total Waste Cost'
    
    def activate_users(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} users activated.")
    activate_users.short_description = 'Activate selected users'
    
    def deactivate_users(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} users deactivated.")
    deactivate_users.short_description = 'Deactivate selected users'
    
    def send_welcome_email(self, request, queryset):
        # Placeholder for email functionality
        self.message_user(request, f"Welcome emails would be sent to {queryset.count()} users.")
    send_welcome_email.short_description = 'Send welcome email'
