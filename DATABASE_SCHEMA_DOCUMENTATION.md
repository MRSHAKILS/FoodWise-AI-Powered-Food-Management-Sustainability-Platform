# 🗄️ Database Schema & System Architecture Documentation

## 📋 Table of Contents
1. [Database Models Overview](#database-models-overview)
2. [Users App](#users-app)
3. [Food App](#food-app)
4. [Resources App](#resources-app)
5. [Uploads App](#uploads-app)
6. [URL Routing](#url-routing)
7. [Forms](#forms)
8. [Views & Actions](#views--actions)
9. [Authentication Flow](#authentication-flow)
10. [Common Workflows](#common-workflows)

---

## 🎯 Database Models Overview

### App Structure
```
Platform/
├── users/      → User authentication & profile management
├── food/       → Inventory tracking & consumption logs
├── resources/  → Educational resources & sustainability guides
└── uploads/    → File uploads (images, receipts, etc.)
```

---

## 👥 Users App

### Model: `User` (Custom User Model)
**File:** `users/models.py`

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | BigAutoField | Primary key | Auto-increment |
| `username` | CharField | Unique username | Max 150 chars, required |
| `email` | EmailField | User email | Unique, required |
| `password` | CharField | Hashed password | Required |
| `full_name` | CharField | Full name | Max 255 chars, optional |
| `budget_limit` | DecimalField | Monthly food budget | Max 10 digits, 2 decimals, nullable |
| `date_joined` | DateTimeField | Account creation date | Auto |
| `last_login` | DateTimeField | Last login timestamp | Auto |
| `is_active` | BooleanField | Account active status | Default: True |
| `is_staff` | BooleanField | Admin panel access | Default: False |
| `is_superuser` | BooleanField | Superuser status | Default: False |

**Relationships:**
- One-to-Many with `FoodItem` (user can have many food items)
- One-to-Many with `ConsumptionLog` (user can have many consumption logs)
- One-to-Many with `Resource` (user can create resources)
- One-to-Many with `Upload` (user can upload files)

**URLs:** `users/urls.py`
```python
/users/profile/          → User profile page (login required)
/users/profile/edit/     → Edit profile (login required)
/users/login/            → Login page
/users/register/         → Registration page
/users/logout/           → Logout action
/users/google-auth/      → Google OAuth handler
```

**Forms:**
- `RegisterForm` → User registration
- `ProfileEditForm` → Profile editing

**Views:**
- `login_view()` → Handle login (POST: authenticate, GET: show form)
- `register_view()` → Handle registration
- `logout_view()` → Log out user and redirect
- `profile_view()` → Display user profile with inventory & logs
- `profile_edit_view()` → Edit profile information
- `google_auth_view()` → Handle Google OAuth callback

---

## 🍽️ Food App

### Model: `FoodItem` (User Inventory)
**File:** `food/models.py`

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | BigAutoField | Primary key | Auto-increment |
| `user` | ForeignKey | Owner of item | CASCADE delete, required |
| `name` | CharField | Item name | Max 255 chars |
| `quantity` | DecimalField | Current quantity | Max 10 digits, 2 decimals |
| `unit` | CharField | Unit of measurement | Max 50 chars (kg, liter, pcs) |
| `category` | CharField | Food category | Choices: vegetable, fruit, dairy, meat, grain, beverage, snack, other |
| `purchase_date` | DateField | Date purchased | Default: today |
| `expiration_date` | DateField | Expiry date | Optional |
| `price` | DecimalField | Cost per unit | Max 10 digits, 2 decimals, optional |
| `notes` | TextField | Additional notes | Optional |
| `created_at` | DateTimeField | Creation timestamp | Auto |
| `updated_at` | DateTimeField | Last update timestamp | Auto |

**Computed Properties:**
- `is_expired` → Returns True if past expiration date
- `days_until_expiration` → Number of days until expiry
- `is_expiring_soon` → True if expiring within 7 days
- `is_low_stock` → True if quantity ≤ 2

**Relationships:**
- Many-to-One with `User` (belongs to one user)

---

### Model: `ConsumptionLog` (Usage Tracking)
**File:** `food/models.py`

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | BigAutoField | Primary key | Auto-increment |
| `user` | ForeignKey | Owner of log | CASCADE delete, required |
| `item_name` | CharField | Name of consumed item | Max 255 chars |
| `quantity` | DecimalField | Amount consumed | Max 10 digits, 2 decimals |
| `unit` | CharField | Unit of measurement | Max 50 chars |
| `category` | CharField | Food category | Same choices as FoodItem |
| `consumption_date` | DateField | Date consumed | Default: today |
| `notes` | TextField | Additional notes | Optional |
| `created_at` | DateTimeField | Log creation timestamp | Auto |

**Relationships:**
- Many-to-One with `User` (belongs to one user)

---

### Model: `FoodItemDatabase` (Master Food Database)
**File:** `food/models.py`

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | BigAutoField | Primary key | Auto-increment |
| `item_name` | CharField | Food item name | Max 255 chars, unique |
| `category` | CharField | Food category | Choices: fruit, dairy, grain, vegetable, protein, snacks, beverages, other |
| `typical_expiration_days` | IntegerField | Average shelf life | In days |
| `sample_cost_per_unit` | DecimalField | Average cost | Max 10 digits, 2 decimals |
| `unit` | CharField | Standard unit | Choices: kg, g, liter, ml, dozen, piece, loaf, bunch, 500g |
| `nutritional_info` | JSONField | Nutritional data | Format: {"calories": 100, "protein": 5, "carbs": 20, "fat": 2} |
| `storage_instructions` | TextField | How to store | Optional |
| `image_url` | URLField | Image URL | Max 500 chars, optional |
| `created_at` | DateTimeField | Creation timestamp | Auto |

**Purpose:** Reference database for common food items with typical properties

---

**URLs:** `food/urls.py`
```python
/food/inventory/                  → List all inventory items (login required)
/food/add/                        → Add new food item (login required)
/food/item/<int:id>/              → View food item details (login required)
/food/item/<int:id>/edit/         → Edit food item (login required)
/food/item/<int:id>/delete/       → Delete food item (login required)
/food/logs/                       → View consumption logs (login required)
/food/log/add/                    → Add consumption log (login required)
/food/history/                    → View consumption history (login required)
/food/database/                   → Browse food database (login required)
/food/database/<int:id>/          → Food database item details (login required)
/food/database/search/            → Search food database (login required)
```

**Forms:**
- `FoodItemForm` → Add/edit food items in inventory
- `ConsumptionLogForm` → Log food consumption

**Views:**
- `inventory_list()` → Display all user's food items
- `inventory_form()` → Add new food item to inventory
- `food_item_detail()` → Show detailed view of a food item
- `food_item_edit()` → Edit existing food item
- `food_item_delete()` → Remove food item from inventory
- `logs_list()` → Display consumption logs
- `log_form()` → Add new consumption log
- `history_view()` → Show consumption history with charts
- `food_database_list()` → Browse master food database
- `food_database_detail()` → View details of database food item
- `food_database_search()` → Search food database

**Management Commands:**
```bash
# Seed master food database (60+ items)
python manage.py seed_food

# Seed user inventory from food_data.json
python manage.py seed_user_inventory --user-id <id>
python manage.py seed_user_inventory --username <username>
python manage.py seed_user_inventory --email <email>
```

---

## 📚 Resources App

### Model: `Resource` (Educational Content)
**File:** `resources/models.py`

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | BigAutoField | Primary key | Auto-increment |
| `title` | CharField | Resource title | Max 255 chars |
| `description` | TextField | Full description | Optional |
| `category` | CharField | Resource category | Choices: recipe, storage, sustainability, waste_reduction, nutrition, tips |
| `content` | TextField | Main content | Optional |
| `external_url` | URLField | External link | Max 500 chars, optional |
| `image_url` | URLField | Cover image | Max 500 chars, optional |
| `author` | ForeignKey | Creator | User model, nullable |
| `created_at` | DateTimeField | Creation timestamp | Auto |
| `updated_at` | DateTimeField | Last update timestamp | Auto |
| `is_featured` | BooleanField | Featured status | Default: False |
| `views_count` | IntegerField | View counter | Default: 0 |

**Relationships:**
- Many-to-One with `User` (optional author)

**URLs:** `resources/urls.py`
```python
/resources/                  → List all resources
/resources/<int:id>/         → View resource details
```

**Views:**
- `resources_list()` → Display all resources with filtering
- `resource_detail()` → Show detailed resource view (increments view count)

**Management Commands:**
```bash
# Seed resources with sample data
python manage.py seed_resources
```

---

## 📤 Uploads App

### Model: `Upload` (File Management)
**File:** `uploads/models.py`

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| `id` | BigAutoField | Primary key | Auto-increment |
| `user` | ForeignKey | Uploader | CASCADE delete, required |
| `file` | FileField | Uploaded file | Upload to 'uploads/' |
| `file_type` | CharField | File category | Choices: receipt, invoice, image, document, other |
| `title` | CharField | File title | Max 255 chars, optional |
| `description` | TextField | File description | Optional |
| `uploaded_at` | DateTimeField | Upload timestamp | Auto |
| `file_size` | IntegerField | Size in bytes | Optional |
| `mime_type` | CharField | MIME type | Max 100 chars, optional |

**Relationships:**
- Many-to-One with `User` (belongs to one user)

**URLs:** `uploads/urls.py`
```python
/uploads/                    → List all uploads (login required)
/uploads/new/                → Upload new file (login required)
/uploads/<int:id>/delete/    → Delete upload (login required)
```

**Forms:**
- `UploadForm` → File upload form

**Views:**
- `uploads_list()` → Display all user uploads
- `upload_form()` → Handle file uploads
- `upload_delete()` → Remove uploaded file

---

## 🔗 URL Routing

### Main URL Configuration
**File:** `Platform/urls.py`
```python
/                         → Landing page (public)
/dashboard/               → User dashboard (login required)
/users/                   → User management (login, register, profile)
/food/                    → Inventory & consumption tracking
/resources/               → Educational resources
/uploads/                 → File uploads
/accounts/                → Django-allauth (Google OAuth)
/admin/                   → Admin panel
```

---

## 📝 Forms

### Users Forms
**File:** `users/forms.py`
- `RegisterForm` → Fields: username, email, password1, password2, full_name
- `ProfileEditForm` → Fields: username, email, full_name, budget_limit

### Food Forms
**File:** `food/forms.py`
- `FoodItemForm` → ModelForm for FoodItem (all fields except user, created_at, updated_at)
- `ConsumptionLogForm` → ModelForm for ConsumptionLog (all fields except user, created_at)

### Uploads Forms
**File:** `uploads/forms.py`
- `UploadForm` → ModelForm for Upload (file, file_type, title, description)

---

## 🎬 Views & Actions

### Common View Patterns

#### List Views
```python
def list_view(request):
    items = Model.objects.filter(user=request.user)
    return render(request, 'template.html', {'items': items})
```

#### Detail Views
```python
def detail_view(request, id):
    item = get_object_or_404(Model, id=id, user=request.user)
    return render(request, 'template.html', {'item': item})
```

#### Create Views
```python
def create_view(request):
    if request.method == 'POST':
        form = ModelForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.user = request.user
            instance.save()
            return redirect('success_url')
    else:
        form = ModelForm()
    return render(request, 'form.html', {'form': form})
```

#### Edit Views
```python
def edit_view(request, id):
    item = get_object_or_404(Model, id=id, user=request.user)
    if request.method == 'POST':
        form = ModelForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('success_url')
    else:
        form = ModelForm(instance=item)
    return render(request, 'form.html', {'form': form})
```

#### Delete Views
```python
def delete_view(request, id):
    item = get_object_or_404(Model, id=id, user=request.user)
    item.delete()
    return redirect('list_url')
```

---

## 🔐 Authentication Flow

### Registration Flow
1. User visits `/users/register/`
2. Fills `RegisterForm` (username, email, password, full_name)
3. POST to `register_view()`
4. User created with hashed password
5. Auto-login and redirect to dashboard

### Login Flow (Traditional)
1. User visits `/users/login/`
2. Submits username/email + password
3. POST to `login_view()`
4. Django authenticates credentials
5. Session created, redirect to dashboard

### Login Flow (Google OAuth)
1. User clicks "Continue with Google"
2. Redirected to `/accounts/google/login/` (django-allauth)
3. Google authentication page
4. Callback to `/accounts/google/login/callback/`
5. User created/retrieved, session created
6. Redirect to dashboard

### Logout Flow
1. User clicks logout
2. POST to `/users/logout/`
3. `logout_view()` calls `logout(request)`
4. Session destroyed, redirect to landing

---

## 🔄 Common Workflows

### Workflow: Add Food to Inventory
```
1. Login → /users/login/
2. Navigate → /food/add/
3. Fill form → FoodItemForm
4. Submit → POST to inventory_form()
5. Validation → Check all fields
6. Save → FoodItem.objects.create(user=request.user, ...)
7. Redirect → /food/inventory/
```

### Workflow: Log Food Consumption
```
1. Login → /users/login/
2. Navigate → /food/log/add/
3. Fill form → ConsumptionLogForm
4. Submit → POST to log_form()
5. Validation → Check all fields
6. Save → ConsumptionLog.objects.create(user=request.user, ...)
7. Redirect → /food/logs/
```

### Workflow: View Consumption History
```
1. Login → /users/login/
2. Navigate → /food/history/
3. Query → ConsumptionLog.objects.filter(user=request.user)
4. Aggregate → Group by date/category
5. Display → Charts + tables
```

### Workflow: Upload Receipt
```
1. Login → /users/login/
2. Navigate → /uploads/new/
3. Choose file → Image/PDF
4. Fill metadata → Title, description, type
5. Submit → POST to upload_form()
6. Save file → MEDIA_ROOT/uploads/
7. Create record → Upload.objects.create(...)
8. Redirect → /uploads/
```

### Workflow: Search Food Database
```
1. Login → /users/login/
2. Navigate → /food/database/search/
3. Enter query → Item name or category
4. Submit → GET to food_database_search()
5. Query → FoodItemDatabase.objects.filter(item_name__icontains=query)
6. Display → Results with details
7. Click item → /food/database/<id>/
```

---

## 🔍 Database Queries (Common Patterns)

### Get User's Food Items
```python
items = FoodItem.objects.filter(user=request.user)
```

### Get Expiring Soon Items
```python
from datetime import date, timedelta
soon = date.today() + timedelta(days=7)
expiring = FoodItem.objects.filter(
    user=request.user,
    expiration_date__lte=soon,
    expiration_date__gte=date.today()
)
```

### Get Low Stock Items
```python
low_stock = FoodItem.objects.filter(user=request.user, quantity__lte=2)
```

### Get Consumption Logs by Date Range
```python
from datetime import date
logs = ConsumptionLog.objects.filter(
    user=request.user,
    consumption_date__gte=date(2025, 11, 1),
    consumption_date__lte=date(2025, 11, 30)
)
```

### Count by Category
```python
from django.db.models import Count
category_counts = FoodItem.objects.filter(user=request.user).values('category').annotate(count=Count('id'))
```

---

## 🛠️ Utility Functions

### Calculate Total Inventory Value
```python
from django.db.models import Sum, F
total_value = FoodItem.objects.filter(user=request.user).aggregate(
    total=Sum(F('quantity') * F('price'))
)['total'] or 0
```

### Get Days Until Expiration
```python
def days_until_expiration(food_item):
    if food_item.expiration_date:
        delta = food_item.expiration_date - date.today()
        return delta.days
    return None
```

### Check Budget Limit
```python
def check_budget(user, new_expense):
    if user.budget_limit:
        spent_this_month = FoodItem.objects.filter(
            user=user,
            purchase_date__year=timezone.now().year,
            purchase_date__month=timezone.now().month
        ).aggregate(total=Sum('price'))['total'] or 0
        return (spent_this_month + new_expense) <= user.budget_limit
    return True
```

---

## 📊 Dashboard Overview

**File:** `templates/dashboard.html`  
**URL:** `/dashboard/`  
**View:** `dashboard_view()` in `users/views.py`

**Displays:**
- User profile info
- Total inventory items
- Items expiring soon (< 7 days)
- Low stock items (quantity ≤ 2)
- Recent consumption logs
- Quick action buttons (Add Item, Log Consumption, View History)

---

## 🎨 Templates Structure

```
templates/
├── base.html                              → Base layout
├── home.html                              → Landing page
├── dashboard.html                         → User dashboard
├── navbar.html                            → Navigation bar
├── footer.html                            → Footer
├── socialaccount/
│   └── authentication_error.html          → Google OAuth error page
├── users/
│   ├── login.html                         → Login page
│   ├── register.html                      → Registration page
│   └── profile.html                       → User profile
├── food/
│   ├── inventory_list.html                → Inventory list
│   ├── inventory_form.html                → Add/edit food item
│   ├── food_item_detail.html              → Food item details
│   ├── logs_list.html                     → Consumption logs
│   ├── log_form.html                      → Add consumption log
│   ├── history.html                       → Consumption history
│   ├── food_database_list.html            → Browse food database
│   ├── food_database_detail.html          → Database item details
│   └── food_database_search.html          → Search database
├── resources/
│   ├── resources_list.html                → Resources list
│   └── resource_detail.html               → Resource details
└── uploads/
    ├── uploads_list.html                  → Uploads list
    └── upload_form.html                   → Upload form
```

---

## 🔧 Settings Configuration

**File:** `Platform/settings.py`

### Key Settings
```python
# Authentication
AUTH_USER_MODEL = 'users.User'
LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'landing'

# Allauth
ACCOUNT_EMAIL_VERIFICATION = 'none'
SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_AUTO_SIGNUP = True

# Database (SQLite for development)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## 📦 Dependencies

**File:** `requirements.txt`
- `Django==5.2.6`
- `django-allauth==65.13.1`
- `psycopg2-binary` (for PostgreSQL)
- `google-auth`
- `google-auth-oauthlib`

---

## 🚀 Quick Start Commands

```bash
# Setup
python manage.py migrate
python manage.py createsuperuser

# Seed data
python manage.py seed_food                              # Master database (60+ items)
python manage.py seed_resources                         # Resources
python manage.py seed_user_inventory --user-id 1        # User inventory
python manage.py seed_consumption_logs --user-id 1      # Consumption logs

# Run server
python manage.py runserver

# Access
http://127.0.0.1:8000/          → Landing page
http://127.0.0.1:8000/admin/    → Admin panel
http://127.0.0.1:8000/dashboard/ → User dashboard
```

---

## 🔄 Smart Consumption Tracking

### Automatic Consumption Logging
When a user deletes an item from inventory, the system **automatically**:
1. Creates a consumption log entry with full details
2. Records quantity, unit, category, and date
3. Adds notes indicating it was consumed from inventory
4. Enables data-driven recommendations and analytics

### Benefits for Personalization
- **Historical Data**: Track what users consume over time
- **Pattern Recognition**: Identify consumption habits and preferences
- **Smart Recommendations**: Suggest items based on past consumption
- **Waste Reduction**: Analyze what gets consumed vs. what expires
- **Budget Tracking**: Calculate spending based on consumption patterns

### Manual Consumption Logging
Users can also manually log consumption without deleting from inventory:
- Go to `/food/log/add/`
- Specify item name, quantity, category, date
- Useful for tracking partial consumption or shared meals

---

## 📝 Notes

- All food-related models use `DecimalField` for precise quantity/price calculations
- Dates use `timezone.now()` to ensure timezone awareness
- All user-related data uses `CASCADE` delete (when user deleted, all related data deleted)
- File uploads stored in `MEDIA_ROOT/uploads/`
- Images/receipts can be linked via URL or uploaded directly
- Master food database (`FoodItemDatabase`) is separate from user inventory (`FoodItem`)

---

**Last Updated:** November 21, 2025  
**Django Version:** 5.2.6  
**Database:** SQLite (development) / PostgreSQL (production)
