from django.contrib import admin
from .models import Upload


@admin.register(Upload)
class UploadAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'user', 'file_type', 'file_size_display', 'upload_date', 'processed']
    list_filter = ['file_type', 'processed', 'upload_date', 'user']
    search_fields = ['file_name', 'user__username', 'notes']
    readonly_fields = ['upload_date', 'file_size', 'mime_type', 'file_size_display']
    date_hierarchy = 'upload_date'
    
    fieldsets = (
        ('File Information', {
            'fields': ('file', 'file_name', 'file_type', 'mime_type', 'file_size', 'file_size_display')
        }),
        ('User & Date', {
            'fields': ('user', 'upload_date')
        }),
        ('Associations', {
            'fields': ('associated_inventory', 'associated_log'),
            'classes': ('collapse',)
        }),
        ('Processing', {
            'fields': ('processed', 'notes')
        }),
    )
    
    def file_size_display(self, obj):
        """Display human-readable file size"""
        return obj.get_file_size_display()
    file_size_display.short_description = 'File Size'
