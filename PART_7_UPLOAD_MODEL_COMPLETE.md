# ✅ PART 7: Image Upload Infrastructure - COMPLETE

## Upload Model Implementation

### Model Created: `uploads.models.Upload`

A comprehensive Django model for handling image uploads with validation and associations.

## Model Fields

### Core Fields

| Field         | Type           | Description                        |
| ------------- | -------------- | ---------------------------------- |
| `id`          | BigAutoField   | Primary key (auto-generated)       |
| `user`        | ForeignKey     | User who uploaded the file         |
| `file_name`   | CharField(255) | Original filename                  |
| `file`        | ImageField     | Image file with validation         |
| `file_type`   | CharField      | Type: receipt, food_label, other   |
| `mime_type`   | CharField(100) | Auto-detected MIME type            |
| `file_size`   | IntegerField   | File size in bytes                 |
| `upload_date` | DateTimeField  | Auto-set on creation               |
| `notes`       | TextField      | Optional notes (blank=True)        |
| `processed`   | BooleanField   | AI processing flag (default=False) |

### Association Fields (Optional)

| Field                  | Type                       | Description             |
| ---------------------- | -------------------------- | ----------------------- |
| `associated_inventory` | ForeignKey(FoodItem)       | Link to inventory item  |
| `associated_log`       | ForeignKey(ConsumptionLog) | Link to consumption log |

Both associations are `null=True, blank=True` with `on_delete=SET_NULL`.

## File Type Choices

```python
FILE_TYPE_CHOICES = [
    ('receipt', 'Receipt'),
    ('food_label', 'Food Label'),
    ('other', 'Other'),
]
```

## Validation Rules

### File Size Validation

- **Maximum**: 5MB (5,242,880 bytes)
- **Validator**: `validate_file_size()` function
- **Error**: "File size cannot exceed 5MB. Your file is X.XX MB."

### File Extension Validation

- **Allowed**: JPG, JPEG, PNG only
- **Validator**: `FileExtensionValidator`
- **Error**: "Only JPG, JPEG, and PNG files are allowed."

### MIME Type Detection

Auto-detected from file extension:

- `.jpg/.jpeg` → `image/jpeg`
- `.png` → `image/png`

## Model Methods

### `__str__(self)`

Returns: `"{file_name} - {file_type} by {username}"`

Example: `"receipt_2025.jpg - Receipt by john"`

### `save(self, *args, **kwargs)` (Overridden)

Automatically sets:

1. `file_size` from uploaded file
2. `mime_type` from file extension
3. `file_name` if not provided

### `get_file_size_display(self)`

Returns human-readable file size:

- `< 1KB`: "X bytes"
- `< 1MB`: "X.XX KB"
- `≥ 1MB`: "X.XX MB"

Example: `"2.45 MB"`

### `clean(self)`

Additional validation:

- Checks file size ≤ 5MB
- Validates file extension (jpg/jpeg/png)

## Related Names

Access uploads from related models:

```python
# From User
user.uploads.all()

# From FoodItem
food_item.uploads.all()

# From ConsumptionLog
log.uploads.all()
```

## Database Configuration

### Meta Options

```python
ordering = ['-upload_date']  # Newest first
verbose_name = 'Upload'
verbose_name_plural = 'Uploads'
```

### Database Indexes

Performance optimization with 4 indexes:

1. `upload_date` (descending) - For recent uploads queries
2. `user + upload_date` - For user-specific upload lists
3. `file_type` - For filtering by type
4. `processed` - For AI processing queue queries

## Admin Configuration

### Admin Features

- **List Display**: file_name, user, file_type, file_size (formatted), upload_date, processed
- **List Filters**: file_type, processed, upload_date, user
- **Search**: file_name, user\_\_username, notes
- **Date Hierarchy**: upload_date
- **Readonly Fields**: upload_date, file_size, mime_type, file_size_display

### Fieldsets

1. **File Information**: file, file_name, file_type, mime_type, file_size
2. **User & Date**: user, upload_date
3. **Associations** (collapsible): associated_inventory, associated_log
4. **Processing**: processed, notes

## Settings Configuration

### Media Files Setup

Added to `Platform/settings.py`:

```python
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

### URL Configuration

Added to `Platform/urls.py`:

```python
from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Directory Structure

```
media/
└── uploads/          # User-uploaded images
    ├── receipt_*.jpg
    ├── label_*.png
    └── ...
```

## Dependencies Installed

### Pillow (12.0.0)

Required for `ImageField` support:

```bash
pip install Pillow
```

Added to `requirements.txt`.

## Migration Applied

**File**: `uploads/migrations/0001_initial.py`

Creates:

- Upload model table
- All fields and constraints
- 4 database indexes
- Foreign key relationships

**Command**:

```bash
python manage.py migrate uploads
```

**Status**: ✅ Applied successfully

## Usage Examples

### Creating an Upload

```python
from uploads.models import Upload
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Create upload from uploaded file
upload = Upload.objects.create(
    user=user,
    file=request.FILES['uploaded_file'],
    file_type='receipt',
    notes='Grocery receipt from Walmart'
)

# File size and MIME type are auto-set
print(upload.file_size)  # e.g., 2457600
print(upload.mime_type)  # e.g., 'image/jpeg'
print(upload.get_file_size_display())  # e.g., '2.34 MB'
```

### Querying Uploads

```python
# All uploads by user
user_uploads = Upload.objects.filter(user=request.user)

# Recent receipts
receipts = Upload.objects.filter(
    file_type='receipt',
    upload_date__gte=last_week
)

# Unprocessed uploads (for AI queue)
pending = Upload.objects.filter(processed=False)

# Uploads with associations
inventory_pics = Upload.objects.filter(
    associated_inventory__isnull=False
)
```

### Associating with Inventory

```python
from food.models import FoodItem

# Create or get food item
item = FoodItem.objects.get(id=5)

# Associate upload
upload.associated_inventory = item
upload.save()

# Access from item
item_images = item.uploads.all()
```

## Validation in Forms

```python
from django import forms
from uploads.models import Upload

class UploadForm(forms.ModelForm):
    class Meta:
        model = Upload
        fields = ['file', 'file_type', 'notes']

    def clean_file(self):
        file = self.cleaned_data.get('file')

        # Validation is automatic via model validators
        # Additional custom validation can be added here

        return file
```

## File Access

### In Templates

```django
{% if upload.file %}
    <img src="{{ upload.file.url }}" alt="{{ upload.file_name }}">
    <p>Size: {{ upload.get_file_size_display }}</p>
    <p>Type: {{ upload.get_file_type_display }}</p>
{% endif %}
```

### In Views

```python
def upload_detail(request, pk):
    upload = Upload.objects.get(pk=pk)

    context = {
        'upload': upload,
        'file_url': upload.file.url,
        'file_path': upload.file.path,
        'size': upload.get_file_size_display(),
    }

    return render(request, 'upload_detail.html', context)
```

## Error Handling

### File Too Large

```python
try:
    upload = Upload.objects.create(
        user=user,
        file=large_file,
        file_type='receipt'
    )
except ValidationError as e:
    # "File size cannot exceed 5MB"
    messages.error(request, str(e))
```

### Invalid File Type

```python
try:
    upload = Upload.objects.create(
        user=user,
        file=pdf_file,  # .pdf file
        file_type='receipt'
    )
except ValidationError as e:
    # "Only JPG, JPEG, and PNG files are allowed"
    messages.error(request, str(e))
```

## Security Considerations

### Implemented

- ✅ File size limit (5MB)
- ✅ File type validation (images only)
- ✅ User authentication required (ForeignKey)
- ✅ Media files in .gitignore
- ✅ Separate media directory

### Recommended Additions

- [ ] Virus scanning on upload
- [ ] Image dimension limits
- [ ] Rate limiting for uploads
- [ ] S3/cloud storage for production
- [ ] Signed URLs for file access

## Future Enhancements (PART 7 Extended)

### AI Processing Integration

```python
# Mark as processed after AI extraction
upload.processed = True
upload.save()

# Query processing status
pending = Upload.objects.filter(processed=False)
completed = Upload.objects.filter(processed=True)
```

### Image Analysis Fields (Future)

Potential additions:

- `extracted_text` (TextField) - OCR results
- `extracted_items` (JSONField) - Parsed receipt items
- `confidence_score` (FloatField) - AI confidence
- `processing_date` (DateTimeField) - When processed
- `processing_errors` (TextField) - Error logs

## Testing

### Model Test

```bash
python manage.py shell -c "from uploads.models import Upload; print('Fields:', len(Upload._meta.get_fields()))"
```

### System Check

```bash
python manage.py check
# Output: System check identified no issues (0 silenced).
```

### Create Test Upload

```python
python manage.py shell

from uploads.models import Upload
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()
user = User.objects.first()

# Create fake image file
image = SimpleUploadedFile(
    "test.jpg",
    b"fake image content",
    content_type="image/jpeg"
)

upload = Upload.objects.create(
    user=user,
    file=image,
    file_type='receipt',
    file_name='test.jpg',
    file_size=len(b"fake image content"),
    notes='Test upload'
)

print(f"Created: {upload}")
```

## Files Modified/Created

### Created

1. ✅ `uploads/models.py` - Upload model with validation
2. ✅ `uploads/admin.py` - Admin configuration
3. ✅ `uploads/migrations/0001_initial.py` - Database migration
4. ✅ `media/uploads/` - Upload directory
5. ✅ `test_upload_model.py` - Test script

### Modified

1. ✅ `Platform/settings.py` - Added MEDIA_URL and MEDIA_ROOT
2. ✅ `Platform/urls.py` - Added media file serving
3. ✅ `requirements.txt` - Added Pillow

## Status Summary

| Component             | Status       |
| --------------------- | ------------ |
| Model Definition      | ✅ Complete  |
| Field Validation      | ✅ Complete  |
| Admin Panel           | ✅ Complete  |
| Database Migration    | ✅ Applied   |
| Media Configuration   | ✅ Complete  |
| File Upload Directory | ✅ Created   |
| Dependencies          | ✅ Installed |
| System Check          | ✅ Passing   |

## Next Steps (PART 7 Continuation)

1. **Upload Form View**

   - Create upload form template
   - Handle file upload in view
   - Display upload success/errors

2. **Upload List View**

   - Display user's uploads
   - Filter by file type
   - Sort by date

3. **Upload Detail View**

   - Show full upload information
   - Display image preview
   - Edit/delete functionality

4. **AI Integration (Future)**
   - Receipt OCR processing
   - Food label parsing
   - Automatic inventory creation

---

## Quick Reference

```python
# Model: Upload
# Location: uploads/models.py
# Admin: uploads/admin.py
# Max Size: 5MB
# Formats: JPG, JPEG, PNG
# Upload Path: media/uploads/

# Create
upload = Upload.objects.create(user=user, file=file, file_type='receipt')

# Query
uploads = Upload.objects.filter(user=user, processed=False)

# Access
file_url = upload.file.url
file_size = upload.get_file_size_display()

# Associate
upload.associated_inventory = food_item
upload.save()
```

---

**Implementation Status**: ✅ **COMPLETE**  
**Ready for**: Upload form views and AI processing integration
