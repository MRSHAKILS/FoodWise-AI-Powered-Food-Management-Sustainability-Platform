from django.contrib import admin
from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'type', 'read_time', 'created_at']
    list_filter = ['category', 'type', 'created_at']
    search_fields = ['title', 'description', 'tags']
    ordering = ['title']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'url')
        }),
        ('Classification', {
            'fields': ('category', 'type', 'tags', 'relevant_food_categories')
        }),
        ('Metadata', {
            'fields': ('read_time', 'created_at')
        }),
    )
