from django.contrib import admin
from .models import FoodItem, ConsumptionLog, FoodItemDatabase


@admin.register(FoodItemDatabase)
class FoodItemDatabaseAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'category', 'typical_expiration_days', 'sample_cost_per_unit', 'unit', 'created_at']
    list_filter = ['category', 'unit']
    search_fields = ['item_name', 'storage_instructions']
    ordering = ['item_name']
    readonly_fields = ['created_at']


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'quantity', 'unit', 'category', 'expiration_date', 'is_expired']
    list_filter = ['category', 'purchase_date', 'expiration_date']
    search_fields = ['name', 'user__username', 'user__email']
    date_hierarchy = 'purchase_date'
    ordering = ['-created_at']


@admin.register(ConsumptionLog)
class ConsumptionLogAdmin(admin.ModelAdmin):
    list_display = ['item_name', 'user', 'quantity', 'unit', 'category', 'consumption_date']
    list_filter = ['category', 'consumption_date']
    search_fields = ['item_name', 'user__username', 'user__email']
    date_hierarchy = 'consumption_date'
    ordering = ['-consumption_date', '-created_at']
