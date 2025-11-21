from django import forms
from django.core.exceptions import ValidationError
from .models import Upload


class UploadForm(forms.ModelForm):
    """Form for uploading images (receipts, food labels, etc.)"""
    
    class Meta:
        model = Upload
        fields = ['file', 'file_type', 'notes']
        widgets = {
            'file': forms.FileInput(attrs={
                'class': 'block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none file:mr-4 file:py-2 file:px-4 file:rounded-l-lg file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100',
                'accept': 'image/jpeg,image/png,image/jpg',
                'id': 'file-upload',
            }),
            'file_type': forms.Select(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent',
                'rows': 4,
                'placeholder': 'Add any notes about this upload (optional)...'
            }),
        }
        labels = {
            'file': 'Choose Image File',
            'file_type': 'What type of image is this?',
            'notes': 'Notes (Optional)',
        }
        help_texts = {
            'file': 'Supported formats: JPG, PNG. Maximum size: 5MB.',
            'file_type': 'Select the type of image you are uploading',
            'notes': 'Any additional information about this upload',
        }
    
    def clean_file(self):
        """Validate file type and size"""
        file = self.cleaned_data.get('file')
        
        if not file:
            raise ValidationError('Please select a file to upload.')
        
        # Validate file extension
        allowed_extensions = ['jpg', 'jpeg', 'png']
        file_extension = file.name.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise ValidationError(
                f'Invalid file type: .{file_extension}. Only JPG, JPEG, and PNG files are allowed.'
            )
        
        # Validate MIME type
        allowed_mime_types = ['image/jpeg', 'image/png']
        if hasattr(file, 'content_type'):
            if file.content_type not in allowed_mime_types:
                raise ValidationError(
                    f'Invalid MIME type: {file.content_type}. Only JPEG and PNG images are allowed.'
                )
        
        # Validate file size (max 5MB)
        max_size = 5 * 1024 * 1024  # 5MB in bytes
        if file.size > max_size:
            raise ValidationError(
                f'File size too large: {file.size / (1024 * 1024):.2f}MB. Maximum allowed size is 5MB.'
            )
        
        return file
    
    def clean_file_type(self):
        """Ensure a valid file type is selected"""
        file_type = self.cleaned_data.get('file_type')
        
        valid_types = ['receipt', 'food_label', 'other']
        if file_type not in valid_types:
            raise ValidationError('Please select a valid file type.')
        
        return file_type
