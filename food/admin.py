from django.contrib import admin
from .models import FoodItem, ConsumptionLog, FoodItemDatabase, MealPlan, SDGScore, WasteLog, ChatSession


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
    list_display = ['item_name', 'user', 'quantity', 'unit', 'category', 'reason', 'estimated_cost', 'waste_date']
    list_filter = ['category', 'reason', 'waste_date']
    search_fields = ['item_name', 'user__username', 'user__email']
    date_hierarchy = 'waste_date'
    ordering = ['-waste_date', '-created_at']


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'is_active', 'created_at', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['session_id', 'user__username', 'user__email']
    date_hierarchy = 'created_at'
    ordering = ['-updated_at']
    readonly_fields = ['created_at', 'updated_at']
