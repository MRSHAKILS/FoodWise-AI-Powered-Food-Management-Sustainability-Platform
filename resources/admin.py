from django.contrib import admin
from .models import Resource


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'type', 'read_time', 'has_url', 'tag_count', 'created_at']
    list_filter = ['category', 'type', 'created_at']
    search_fields = ['title', 'description', 'tags', 'relevant_food_categories']
    ordering = ['title']
    readonly_fields = ['created_at', 'tag_preview']
    list_per_page = 50
    list_editable = ['category', 'type', 'read_time']
    actions = ['export_as_json', 'duplicate_resources']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'description', 'url')
        }),
        ('Classification', {
            'fields': ('category', 'type', 'read_time')
        }),
        ('Tags & Categories', {
            'fields': ('tags', 'relevant_food_categories', 'tag_preview'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def has_url(self, obj):
        return bool(obj.url)
    has_url.boolean = True
    has_url.short_description = 'Has Link'
    
    def tag_count(self, obj):
        return len(obj.tags) if obj.tags else 0
    tag_count.short_description = 'Tags'
    
    def tag_preview(self, obj):
        if obj.tags:
            return ', '.join(obj.tags[:5])
        return 'No tags'
    tag_preview.short_description = 'Tag Preview'
    
    def export_as_json(self, request, queryset):
        import json
        from django.http import JsonResponse
        data = list(queryset.values())
        return JsonResponse(data, safe=False)
    export_as_json.short_description = 'Export selected as JSON'
    
    def duplicate_resources(self, request, queryset):
        for resource in queryset:
            resource.pk = None
            resource.title = f"{resource.title} (Copy)"
            resource.save()
        self.message_user(request, f"{queryset.count()} resources duplicated successfully.")
    duplicate_resources.short_description = 'Duplicate selected resources'
