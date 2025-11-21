from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from food.models import FoodItem, ConsumptionLog


def validate_file_size(file):
    """Validate that file size does not exceed 5MB"""
    max_size_mb = 5
    max_size_bytes = max_size_mb * 1024 * 1024  # 5MB in bytes
    
    if file.size > max_size_bytes:
        raise ValidationError(f'File size cannot exceed {max_size_mb}MB. Your file is {file.size / (1024 * 1024):.2f}MB.')


class Upload(models.Model):
    """Image upload model for receipts, food labels, and other food-related images"""
    
    FILE_TYPE_CHOICES = [
        ('receipt', 'Receipt'),
        ('food_label', 'Food Label'),
        ('other', 'Other'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='uploads',
        help_text='User who uploaded the file'
    )
    
    file_name = models.CharField(
        max_length=255,
        help_text='Original filename'
    )
    
    file = models.ImageField(
        upload_to='uploads/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png'],
                message='Only JPG, JPEG, and PNG files are allowed.'
            ),
            validate_file_size
        ],
        help_text='Image file (JPG/PNG, max 5MB)'
    )
    
    file_type = models.CharField(
        max_length=20,
        choices=FILE_TYPE_CHOICES,
        default='other',
        help_text='Type of uploaded file'
    )
    
    mime_type = models.CharField(
        max_length=100,
        blank=True,
        help_text='MIME type of the file (e.g., image/jpeg)'
    )
    
    file_size = models.IntegerField(
        help_text='File size in bytes'
    )
    
    associated_inventory = models.ForeignKey(
        FoodItem,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploads',
        help_text='Optional link to inventory item'
    )
    
    associated_log = models.ForeignKey(
        ConsumptionLog,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='uploads',
        help_text='Optional link to consumption log'
    )
    
    upload_date = models.DateTimeField(
        auto_now_add=True,
        help_text='Date and time of upload'
    )
    
    notes = models.TextField(
        blank=True,
        help_text='Optional notes about the upload'
    )
    
    processed = models.BooleanField(
        default=False,
        help_text='Whether AI processing has been completed'
    )
    
    class Meta:
        ordering = ['-upload_date']
        verbose_name = 'Upload'
        verbose_name_plural = 'Uploads'
        indexes = [
            models.Index(fields=['-upload_date']),
            models.Index(fields=['user', '-upload_date']),
            models.Index(fields=['file_type']),
            models.Index(fields=['processed']),
        ]
    
    def __str__(self):
        return f"{self.file_name} - {self.get_file_type_display()} by {self.user.username}"
    
    def save(self, *args, **kwargs):
        """Override save to automatically set file_size and mime_type"""
        if self.file:
            # Set file size if not already set
            if not self.file_size:
                self.file_size = self.file.size
            
            # Set MIME type if not already set
            if not self.mime_type:
                # Determine MIME type from file extension
                file_extension = self.file.name.split('.')[-1].lower()
                mime_types = {
                    'jpg': 'image/jpeg',
                    'jpeg': 'image/jpeg',
                    'png': 'image/png',
                }
                self.mime_type = mime_types.get(file_extension, 'application/octet-stream')
            
            # Set file_name from uploaded file if not provided
            if not self.file_name:
                self.file_name = self.file.name
        
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """Return human-readable file size"""
        size_bytes = self.file_size
        
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024 * 1024:
            return f"{size_bytes / 1024:.2f} KB"
        else:
            return f"{size_bytes / (1024 * 1024):.2f} MB"
    
    def clean(self):
        """Additional validation"""
        super().clean()
        
        # Validate file size
        if self.file and self.file.size > 5 * 1024 * 1024:
            raise ValidationError({
                'file': 'File size cannot exceed 5MB.'
            })
        
        # Validate file extension
        if self.file:
            allowed_extensions = ['jpg', 'jpeg', 'png']
            file_extension = self.file.name.split('.')[-1].lower()
            if file_extension not in allowed_extensions:
                raise ValidationError({
                    'file': f'File type .{file_extension} is not allowed. Only JPG, JPEG, and PNG files are accepted.'
                })
