# 📁 AI-Powered Food Management Platform - Complete Documentation

> **Single Unified Reference Document** - All project structure, URLs, implementation tasks, and quick start guide in one place.

---

## 📊 Quick Status Dashboard

**Overall Progress: 40% Complete** | **Estimated Time Remaining: 33 hours**

| Phase | Status | Completion | Critical Blockers |
|-------|--------|-----------|-------------------|
| Phase 1: Setup & Models | 🟡 | 70% | Models not defined |
| Phase 2: Authentication | 🔴 | 30% | Logic not implemented |
| Phase 3: Database Seeding | 🔴 | 0% | **MANDATORY** - Script missing |
| Phase 4: Core Features | 🟡 | 40% | CRUD not functional |
| Phase 5: Rule-Based Logic | 🔴 | 10% | Recommendation engine missing |
| Phase 6: Image Upload | 🟡 | 30% | File handling incomplete |
| Phase 7: Dashboard UI | ✅ | 80% | Dynamic data needed |
| Phase 8: Documentation | 🟡 | 60% | README incomplete |

**Legend:** ✅ Complete | 🟡 Partial | 🔴 Critical

---

## 🎯 Project Overview

**Purpose:** Full-stack food management & sustainability platform for **Innovatex Hackathon**  
**SDG Goals:** SDG 2 (Zero Hunger) + SDG 12 (Responsible Consumption)  
**Tech Stack:** Django 5.2.6 + Vanilla JS + Tailwind CSS + SQLite  
**Deadline:** Must be completed before onsite hackathon (Part 1)

---

## 📂 Complete Directory Structure

```
AI-Powered-Food-Management-Sustainability-Platform/
│
├── 📁 Platform/                    # Django Project Configuration
│   ├── __init__.py
│   ├── asgi.py                     # ASGI config for deployment
│   ├── settings.py                 # ⚙️ CORE: DB, INSTALLED_APPS, MIDDLEWARE, TEMPLATES
│   ├── urls.py                     # 🔗 CORE: Main URL router (includes all app URLs)
│   └── wsgi.py                     # WSGI config for deployment
│
├── 📁 users/                       # 👥 User Management App (Phase 2)
│   ├── migrations/                 # Database migrations
│   ├── templates/users/
│   │   ├── login.html              # ✅ Login page (UI ready)
│   │   ├── register.html           # ✅ Registration form (UI ready)
│   │   ├── profile.html            # 🔴 Profile view (TODO)
│   │   └── profile_edit.html       # 🔴 Edit profile (TODO: create template)
│   ├── __init__.py
│   ├── admin.py                    # 🔴 TODO: Register User model
│   ├── apps.py
│   ├── models.py                   # 🔴 CRITICAL: Empty - define User model
│   ├── forms.py                    # 🔴 CRITICAL: Missing - create forms
│   ├── urls.py                     # ✅ Complete (login, register, profile, logout)
│   ├── views.py                    # 🟡 Placeholder views with TODO comments
│   └── tests.py                    # 🔴 Empty - write tests
│
├── 📁 food/                        # 🍎 Inventory & Consumption App (Phase 4)
│   ├── migrations/
│   ├── templates/food/
│   │   ├── inventory_list.html     # 🔴 List with filters (TODO)
│   │   ├── inventory_form.html     # 🔴 Add item form (TODO)
│   │   ├── inventory_edit.html     # 🔴 Edit item (TODO: create template)
│   │   ├── logs_list.html          # 🔴 Consumption logs (TODO: create template)
│   │   ├── log_form.html           # 🔴 Log entry form (TODO: create template)
│   │   └── history.html            # 🔴 Historical data (TODO: create template)
│   ├── __init__.py
│   ├── admin.py                    # 🔴 TODO: Register FoodItem, ConsumptionLog
│   ├── apps.py
│   ├── models.py                   # 🔴 CRITICAL: Empty - define FoodItem & ConsumptionLog
│   ├── forms.py                    # 🔴 CRITICAL: Missing - create forms
│   ├── urls.py                     # ✅ Complete (inventory CRUD, logs, history)
│   ├── views.py                    # 🟡 Placeholder views with TODO comments
│   ├── tests.py                    # 🔴 Empty
│   └── management/commands/        # 🔴 CRITICAL: Missing - create seed script
│       └── seed_food.py            # 🔴 TODO: Seed 15-20 food items
│
├── 📁 resources/                   # 📚 Educational Resources App (Phase 3 & 5)
│   ├── migrations/
│   ├── templates/resources/
│   │   ├── resources_list.html     # ✅ List view (UI ready)
│   │   ├── resources_by_category.html  # 🔴 Category filter (TODO: create template)
│   │   ├── resource_detail.html    # 🔴 Detail view (TODO: create template)
│   │   └── recommendations.html    # 🔴 Rule-based recs (TODO: create template)
│   ├── __init__.py
│   ├── admin.py                    # 🔴 TODO: Register Resource model
│   ├── apps.py
│   ├── models.py                   # 🔴 CRITICAL: Empty - define Resource model
│   ├── utils.py                    # 🔴 CRITICAL: Missing - recommendation engine
│   ├── urls.py                     # ✅ Complete (list, filter, recommendations)
│   ├── views.py                    # ✅ View functions added
│   ├── tests.py                    # 🔴 Empty
│   └── management/commands/        # 🔴 CRITICAL: Missing - create seed script
│       └── seed_resources.py       # 🔴 TODO: Seed 15-20 resources (4 categories)
│
├── 📁 uploads/                     # 📸 Image Upload App (Phase 6)
│   ├── migrations/
│   ├── templates/uploads/
│   │   ├── upload_form.html        # ✅ Upload form (UI ready)
│   │   ├── upload_list.html        # 🔴 View uploads (TODO: create template)
│   │   ├── upload_detail.html      # 🔴 Single upload (TODO: create template)
│   │   └── link_to_inventory.html  # 🔴 Manual linking (TODO: create template)
│   ├── __init__.py
│   ├── admin.py                    # 🔴 TODO: Register Upload model
│   ├── apps.py
│   ├── models.py                   # 🔴 CRITICAL: Empty - define Upload model
│   ├── forms.py                    # 🔴 CRITICAL: Missing - file upload form
│   ├── urls.py                     # ✅ Complete (upload, list, detail, delete, link)
│   ├── views.py                    # ✅ View functions added
│   └── tests.py                    # 🔴 Empty
│
├── 📁 templates/                   # 🎨 Global Templates (Phase 7)
│   ├── base.html                   # ✅ Base template (Tailwind, GSAP, Swiper loaded)
│   ├── navbar.html                 # ✅ Navigation (all links including Logs, Profile, Logout)
│   └── dashboard.html              # ✅ Landing page (widgets ready, needs dynamic data)
│
├── 📁 static/                      # Static Assets
│   ├── css/
│   │   └── tailwind.css            # ✅ Tailwind CSS
│   ├── js/
│   │   ├── main.js                 # 🔴 TODO: Custom JavaScript
│   │   └── animations.js           # 🔴 TODO: GSAP animations
│   └── images/                     # Logo, icons
│
├── 📁 media/                       # 🔴 TODO: Create for file uploads
│   └── uploads/                    # User uploaded images
│
├── 📁 myenv/                       # Python Virtual Environment
│
├── 📁 node_modules/                # ✅ Node.js packages (GSAP, Swiper, Framer Motion)
│
├── 📄 manage.py                    # ✅ Django CLI
├── 📄 db.sqlite3                   # ✅ SQLite database
├── 📄 requirements.txt             # ✅ Python dependencies
├── 📄 package.json                 # ✅ Node.js dependencies (GSAP, Swiper, Framer Motion)
├── 📄 target.json                  # ✅ Hackathon requirements
├── 📄 .gitignore                   # ✅ Git ignore
├── 📄 PROJECT_STRUCTURE.md         # ✅ This file - Complete documentation
└── 📄 README.md                    # 🔴 TODO: Write comprehensive setup guide
```

---

## 🔗 Complete URL Mapping (29 Endpoints)

### **Main Routes**

| URL Path | View | Template | Status | Purpose |
|----------|------|----------|--------|---------|
| `/` | `dashboard_view` | `dashboard.html` | ✅ | Landing page with overview widgets |

---

### **👥 User Routes** (`/users/`)

| URL Path | View | Template | Status | Purpose |
|----------|------|----------|--------|---------|
| `/users/login/` | `login_view` | `users/login.html` | ✅ UI / 🔴 Logic | User login |
| `/users/register/` | `register_view` | `users/register.html` | ✅ UI / 🔴 Logic | New user registration (household details) |
| `/users/profile/` | `profile_view` | `users/profile.html` | 🔴 | View profile (dietary prefs, budget) |
| `/users/profile/edit/` | `profile_edit_view` | `users/profile_edit.html` | 🔴 | Edit user details |
| `/users/logout/` | `logout_view` | *Redirect* | 🔴 | Logout user |

**Priority:** 🔴 **HIGH** - Authentication logic needed immediately  
**Blockers:** User model not defined, forms missing  
**Time Estimate:** 3 hours (model + forms + auth logic)

---

### **🍎 Food/Inventory Routes** (`/food/`)

| URL Path | View | Template | Status | Purpose |
|----------|------|----------|--------|---------|
| `/food/inventory/` | `inventory_list` | `food/inventory_list.html` | 🔴 | Display all food items with filters |
| `/food/inventory/add/` | `inventory_form` | `food/inventory_form.html` | 🔴 | Add new food item manually |
| `/food/inventory/edit/<int:id>/` | `inventory_edit` | `food/inventory_edit.html` | 🔴 | Edit existing item (expiry, quantity) |
| `/food/inventory/delete/<int:id>/` | `inventory_delete` | *Redirect* | 🔴 | Delete inventory item |
| `/food/logs/` | `consumption_logs_list` | `food/logs_list.html` | 🔴 | Daily consumption logs |
| `/food/logs/add/` | `consumption_log_form` | `food/log_form.html` | 🔴 | Manually log consumed food |
| `/food/logs/delete/<int:id>/` | `consumption_log_delete` | *Redirect* | 🔴 | Delete consumption entry |
| `/food/history/` | `consumption_history` | `food/history.html` | 🔴 | Historical consumption data (for AI - Part 2) |

**Priority:** 🔴 **CRITICAL** - Core functionality blocker  
**Blockers:** FoodItem model missing, database empty (seed script needed), forms missing  
**Time Estimate:** 8 hours (models + CRUD + seeding + templates)

---

### **📚 Educational Resources Routes** (`/resources/`)

| URL Path | View | Template | Status | Purpose |
|----------|------|----------|--------|---------|
| `/resources/` | `resources_list` | `resources/resources_list.html` | ✅ UI / 🔴 DB | List all resources (4 categories) |
| `/resources/category/<str:category>/` | `resources_by_category` | `resources/resources_by_category.html` | 🔴 | Filter by category (Recipes, Nutrition, Storage, Sustainability) |
| `/resources/detail/<int:id>/` | `resource_detail` | `resources/resource_detail.html` | 🔴 | Full resource details |
| `/resources/recommendations/` | `recommended_resources` | `resources/recommendations.html` | 🔴 | Rule-based recommendations |

**Priority:** 🟡 **MEDIUM** - Non-blocking but visible feature  
**Blockers:** Resource model empty, seed script missing (15-20 resources needed), recommendation engine not implemented  
**Time Estimate:** 6 hours (model + seeding + rule logic + templates)

---

### **📸 Image Upload Routes** (`/uploads/`)

| URL Path | View | Template | Status | Purpose |
|----------|------|----------|--------|---------|
| `/uploads/` | `upload_form` | `uploads/upload_form.html` | ✅ UI / 🔴 Logic | Upload receipt/food images |
| `/uploads/list/` | `upload_list` | `uploads/upload_list.html` | 🔴 | View all uploaded images |
| `/uploads/detail/<int:id>/` | `upload_detail` | `uploads/upload_detail.html` | 🔴 | Single upload details |
| `/uploads/delete/<int:id>/` | `upload_delete` | *Redirect* | 🔴 | Delete uploaded image |
| `/uploads/link/<int:upload_id>/` | `link_to_inventory` | `uploads/link_to_inventory.html` | 🔴 | Manually link upload to inventory item |

**Priority:** 🟡 **LOW** - Optional for Part 1  
**Blockers:** Upload model empty, file handling not implemented, forms missing  
**Time Estimate:** 5 hours (model + file upload + linking logic + media folder setup)

---

## 📝 Complete Implementation Checklist

### **Phase 1: Setup & Database Models** (3 hours) - 70% Complete
- [x] ✅ Virtual environment configured
- [x] ✅ Django project created
- [x] ✅ 4 apps created (users, food, resources, uploads)
- [x] ✅ `settings.py` configured (INSTALLED_APPS, TEMPLATES, STATIC)
- [ ] 🔴 **CRITICAL:** Define models in `users/models.py` (User with household_size, dietary_preferences, budget_range)
- [ ] 🔴 **CRITICAL:** Define models in `food/models.py` (FoodItem, ConsumptionLog)
- [ ] 🔴 **CRITICAL:** Define models in `resources/models.py` (Resource with category, title, content)
- [ ] 🔴 **CRITICAL:** Define models in `uploads/models.py` (Upload with image, linked_inventory_item)
- [ ] 🔴 Run `python manage.py makemigrations` and `migrate`

**Blockers:** All models.py files are currently empty - **MANDATORY BEFORE PROCEEDING**

---

### **Phase 2: Authentication System** (4 hours) - 30% Complete
- [x] ✅ `users/urls.py` configured (login, register, profile, logout)
- [x] ✅ `users/templates/` created (login.html, register.html UI ready)
- [ ] 🔴 Create `users/forms.py` (RegistrationForm, LoginForm, ProfileEditForm)
- [ ] 🔴 Implement `login_view` logic (authenticate, create session)
- [ ] 🔴 Implement `register_view` logic (validate, save user)
- [ ] 🔴 Implement `profile_view` logic (display user data)
- [ ] 🔴 Implement `profile_edit_view` logic (update dietary prefs, budget)
- [ ] 🔴 Implement `logout_view` logic (destroy session)
- [ ] 🔴 Add `@login_required` decorators to protected views

**Blockers:** User model not defined, forms missing  
**Critical Path:** Must complete Phase 1 first

---

### **Phase 3: Database Seeding** (2 hours) - 0% Complete
- [ ] 🔴 **MANDATORY:** Create `food/management/commands/seed_food.py`
  - Seed 15-20 food items across categories (Grains, Vegetables, Fruits, Dairy, Protein, Snacks)
  - Include realistic expiry dates, costs, quantities
- [ ] 🔴 **MANDATORY:** Create `resources/management/commands/seed_resources.py`
  - Seed 15-20 resources across 4 categories:
    - **Recipes:** 5 resources (Zero-Waste Recipes, Quick Meals)
    - **Nutrition Tips:** 5 resources (Balanced Diet, Portion Control)
    - **Storage Tips:** 5 resources (Proper Storage Methods)
    - **Sustainability Practices:** 5 resources (Reduce Food Waste, Composting)
- [ ] 🔴 Run `python manage.py seed_food` and `seed_resources`
- [ ] 🔴 Verify data in admin panel

**Blockers:** Models not migrated  
**Urgency:** **CRITICAL** - Database is empty, UI cannot function without data

---

### **Phase 4: Core Food Features** (8 hours) - 40% Complete
- [x] ✅ `food/urls.py` configured (inventory CRUD, logs, history)
- [x] ✅ View functions created with TODO comments
- [ ] 🔴 Create `food/forms.py` (FoodItemForm, ConsumptionLogForm)
- [ ] 🔴 Implement `inventory_list` (query FoodItem, apply filters by category/expiry)
- [ ] 🔴 Implement `inventory_form` (validate, save new item)
- [ ] 🔴 Implement `inventory_edit` (load item, update fields)
- [ ] 🔴 Implement `inventory_delete` (delete with confirmation)
- [ ] 🔴 Implement `consumption_logs_list` (display logs with date filters)
- [ ] 🔴 Implement `consumption_log_form` (validate, save log entry)
- [ ] 🔴 Implement `consumption_log_delete` (delete log)
- [ ] 🔴 Implement `consumption_history` (query historical data for charts)
- [ ] 🔴 Create all templates in `food/templates/food/`
- [ ] 🔴 Add AJAX for dynamic updates (optional)

**Blockers:** Forms missing, database empty  
**Critical Path:** Must complete Phases 1-3 first

---

### **Phase 5: Rule-Based Recommendation Engine** (5 hours) - 10% Complete
- [ ] 🔴 Create `resources/utils.py` for recommendation logic
- [ ] 🔴 Implement rule-based algorithm:
  ```python
  # Example Rules:
  - IF user has expired items → Recommend "Storage Tips" resources
  - IF user logs wasted food frequently → Recommend "Reduce Food Waste" resources
  - IF user has limited budget → Recommend "Budget-Friendly Recipes"
  - IF user has specific dietary preference (vegetarian) → Filter recipes
  ```
- [ ] 🔴 Integrate recommendation engine into `recommended_resources` view
- [ ] 🔴 Create `resources/recommendations.html` template
- [ ] 🔴 Test with various user scenarios

**Dependencies:** Requires Phase 3 (seeded resources) and Phase 4 (consumption data)  
**Urgency:** **MEDIUM** - Visible feature but not blocking

---

### **Phase 6: Image Upload System** (5 hours) - 30% Complete
- [x] ✅ `uploads/urls.py` configured
- [x] ✅ View functions created
- [ ] 🔴 Configure `MEDIA_ROOT` and `MEDIA_URL` in `settings.py`
- [ ] 🔴 Create `media/uploads/` directory
- [ ] 🔴 Create `uploads/forms.py` (UploadForm with FileField)
- [ ] 🔴 Implement `upload_form` (handle file upload, validate image types)
- [ ] 🔴 Implement `upload_list` (display thumbnails)
- [ ] 🔴 Implement `upload_detail` (show full image)
- [ ] 🔴 Implement `upload_delete` (delete file from filesystem)
- [ ] 🔴 Implement `link_to_inventory` (manual linking dropdown)
- [ ] 🔴 Create all templates in `uploads/templates/uploads/`
- [ ] 🔴 Test file upload/delete

**Note:** OCR/AI extraction is **Part 2** - for now, only manual upload and linking  
**Priority:** **LOW** - Optional for Part 1

---

### **Phase 7: Dashboard & UI Polish** (4 hours) - 80% Complete
- [x] ✅ `templates/base.html` created (Tailwind, GSAP, Swiper)
- [x] ✅ `templates/navbar.html` enhanced (greenish theme, animations, all links)
- [x] ✅ `templates/dashboard.html` created (widgets layout)
- [ ] 🔴 Make dashboard widgets dynamic:
  - **Total Inventory Items:** Query `FoodItem.objects.count()`
  - **Expiring Soon:** Filter items with `expiry_date <= today + 3 days`
  - **Logged Consumption:** Query `ConsumptionLog.objects.filter(date_logged=today).count()`
- [ ] 🔴 Add charts (consumption trends) using Chart.js
- [ ] 🔴 Test responsive design on mobile
- [ ] 🔴 Add loading animations with GSAP

**Blockers:** Database empty, models not migrated  
**Priority:** **MEDIUM** - Visual polish depends on working backend

---

### **Phase 8: Testing & Documentation** (2 hours) - 60% Complete
- [x] ✅ `PROJECT_STRUCTURE.md` created (this file)
- [ ] 🔴 Write comprehensive `README.md`:
  - Setup instructions (venv, install dependencies, migrations)
  - Feature overview with screenshots
  - API documentation (if applicable)
  - Troubleshooting guide
- [ ] 🔴 Write unit tests in `tests.py` files
- [ ] 🔴 Run `python manage.py test` and fix failures
- [ ] 🔴 Test all user flows (registration → login → add item → log consumption → view recommendations)
- [ ] 🔴 Prepare hackathon demo script

**Time Estimate:** 2 hours  
**Priority:** **HIGH** - Required for submission

---

## 🚀 Quick Start Command Reference

### **Environment Setup**
```powershell
# Activate virtual environment
myenv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Install Node.js packages (if needed)
npm install
```

### **Database Operations**
```powershell
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser

# Seed database (after creating seed scripts)
python manage.py seed_food
python manage.py seed_resources
```

### **Run Development Server**
```powershell
# Start Django server
python manage.py runserver

# Access at: http://127.0.0.1:8000/
# Admin panel: http://127.0.0.1:8000/admin/
```

### **Testing**
```powershell
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test food
```

---

## ⚠️ Critical Blockers & Priorities

### **🔴 IMMEDIATE ACTION REQUIRED (Today)**
1. **Define all models** (`users`, `food`, `resources`, `uploads`) - **1.5 hours**
2. **Run migrations** (`makemigrations` + `migrate`) - **15 min**
3. **Create database seeding scripts** (`seed_food.py`, `seed_resources.py`) - **2 hours**
4. **Seed database** (run commands) - **5 min**

**Total Time: 4 hours** → **UNBLOCKS ALL OTHER WORK**

### **🟡 HIGH PRIORITY (This Week)**
5. **Authentication system** (forms + logic) - **4 hours**
6. **Food inventory CRUD** (forms + views + templates) - **6 hours**
7. **Recommendation engine** (rule-based logic) - **3 hours**

### **🟢 LOWER PRIORITY (Optional for Part 1)**
8. Image upload system - **5 hours**
9. Advanced UI animations - **2 hours**
10. Unit tests - **2 hours**

---

## 📊 Model Definitions (Reference)

### **Users Model** (`users/models.py`)
```python
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    household_size = models.IntegerField(default=1)
    dietary_preferences = models.CharField(max_length=100, blank=True)  # "Vegetarian", "Vegan", etc.
    location = models.CharField(max_length=100)
    budget_range = models.CharField(max_length=50)  # "Low", "Medium", "High"
```

### **Food Models** (`food/models.py`)
```python
class FoodItem(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200)
    category = models.CharField(max_length=50)  # Grains, Vegetables, Fruits, Dairy, Protein, Snacks
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=20)  # kg, liters, pieces
    expiry_date = models.DateField()
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    added_on = models.DateTimeField(auto_now_add=True)

class ConsumptionLog(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    item_name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    date_logged = models.DateField(auto_now_add=True)
```

### **Resources Model** (`resources/models.py`)
```python
class Resource(models.Model):
    CATEGORY_CHOICES = [
        ('Recipes', 'Recipes'),
        ('Nutrition', 'Nutrition Tips'),
        ('Storage', 'Storage Tips'),
        ('Sustainability', 'Sustainability Practices'),
    ]
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    content = models.TextField()
    external_link = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
```

### **Uploads Model** (`uploads/models.py`)
```python
class Upload(models.Model):
    user = models.ForeignKey('users.CustomUser', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    linked_inventory_item = models.ForeignKey('food.FoodItem', on_delete=models.SET_NULL, null=True, blank=True)
```

---

## 🎯 Next Steps (Ordered by Priority)

1. **[TODAY]** Define all models and migrate database
2. **[TODAY]** Create and run seeding scripts
3. **[TOMORROW]** Implement authentication system (login/register logic)
4. **[TOMORROW]** Build food inventory CRUD functionality
5. **[DAY 3]** Implement recommendation engine
6. **[DAY 4]** Polish dashboard with dynamic data
7. **[DAY 5]** Write README and prepare demo

---

## 📞 Support & Resources

- **Django Docs:** https://docs.djangoproject.com/
- **Tailwind CSS:** https://tailwindcss.com/docs
- **GSAP Animations:** https://gsap.com/docs/
- **Swiper Slider:** https://swiperjs.com/get-started

---

**Last Updated:** December 2024  
**Maintainer:** MRSHAKILS  
**Hackathon:** Innovatex Part 1
│   ├── views.py                    # Inventory & consumption logic
│   └── tests.py
│
├── 📁 resources/                   # Educational Resources App (Phase 3 & 5)
│   ├── migrations/
│   ├── templates/resources/
│   │   ├── resources_list.html     # All resources with filters
│   │   ├── resources_by_category.html  # Filtered by category
│   │   ├── resource_detail.html    # Single resource view
│   │   └── recommendations.html    # Rule-based recommendations (Phase 5)
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                   # Resource (title, description_or_url, category, type [article/video])
│   ├── urls.py                     # Resource routes (list, filter, recommendations)
│   ├── views.py                    # Resource logic + recommendation engine
│   └── tests.py
│
├── 📁 uploads/                     # Image Upload App (Phase 6: Infrastructure)
│   ├── migrations/
│   ├── templates/uploads/
│   │   ├── upload_form.html        # Upload food labels/receipts (JPG/PNG)
│   │   ├── upload_list.html        # View all uploads
│   │   ├── upload_detail.html      # Single upload view
│   │   └── link_to_inventory.html  # Manual linking to inventory/logs
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py                   # Upload (file_path, uploaded_at, linked_item_id, user_id)
│   ├── urls.py                     # Upload routes (create, list, delete, link)
│   ├── views.py                    # File handling (NO OCR yet)
│   └── tests.py
│
├── 📁 templates/                   # Global Templates (Phase 7: Dashboard)
│   ├── base.html                   # Base template with navbar, footer
│   ├── navbar.html                 # Navigation (Dashboard, Logs, Inventory, Resources, Profile, Logout)
│   └── dashboard.html              # Landing page after login (widgets: profile, activity, inventory summary, recommendations)
│
├── 📁 static/                      # Static Files
│   ├── css/
│   │   └── tailwind.css            # Tailwind CSS
│   ├── js/
│   │   ├── main.js                 # Custom JavaScript
│   │   └── animations.js           # GSAP/Swiper animations
│   └── images/                     # Logo, icons, etc.
│
├── 📁 myenv/                       # Virtual Environment (Python dependencies)
│
├── 📁 node_modules/                # Node.js packages (GSAP, Swiper, Framer Motion)
│
├── 📄 manage.py                    # Django management script
├── 📄 db.sqlite3                   # SQLite database file
├── 📄 requirements.txt             # Python dependencies
├── 📄 package.json                 # Node.js dependencies
├── 📄 target.json                  # Project requirements & roadmap
├── 📄 .gitignore                   # Git ignore file
└── 📄 README.md                    # Project documentation (Phase 8)
```

---

## 🗂️ Key Files & Their Roles

### **Configuration Files**

| File | Location | Purpose |
|------|----------|---------|
| `settings.py` | `Platform/` | Django configuration (DB, apps, middleware, static files) |
| `urls.py` | `Platform/` | Main URL router - includes all app URLs |
| `manage.py` | Root | Django CLI tool (runserver, migrate, createsuperuser) |
| `target.json` | Root | Hackathon requirements & implementation roadmap |

### **Models (Database Schema - Phase 1)**

| Model | App | File | Fields | Purpose |
|-------|-----|------|--------|---------|
| `User` | users | `users/models.py` | full_name, email, password_hash, household_size, dietary_preferences, location, budget_range | User authentication & profile |
| `FoodItem` | food | `food/models.py` | item_name, category, quantity, expiry_date, cost_per_unit, user_id, image_url | Inventory management |
| `ConsumptionLog` | food | `food/models.py` | item_name, quantity, category, date_logged, user_id | Daily food usage tracking |
| `Resource` | resources | `resources/models.py` | title, description_or_url, category, type | Educational content |
| `Upload` | uploads | `uploads/models.py` | file_path, uploaded_at, linked_item_id, user_id | Image storage |

### **Views (Business Logic)**

| View Function | App | Purpose | Template |
|---------------|-----|---------|----------|
| `dashboard_view` | users | Landing page after login | `dashboard.html` |
| `login_view` | users | User authentication | `users/login.html` |
| `register_view` | users | User registration | `users/register.html` |
| `profile_view` | users | Display user profile | `users/profile.html` |
| `profile_edit_view` | users | Edit profile details | `users/profile_edit.html` |
| `logout_view` | users | User logout | Redirect to login |
| `inventory_list` | food | List all food items with filters | `food/inventory_list.html` |
| `inventory_form` | food | Add new food item | `food/inventory_form.html` |
| `inventory_edit` | food | Edit existing item | `food/inventory_edit.html` |
| `inventory_delete` | food | Delete food item | Redirect to inventory |
| `consumption_logs_list` | food | View consumption logs | `food/logs_list.html` |
| `consumption_log_form` | food | Log daily food usage | `food/log_form.html` |
| `consumption_history` | food | Historical data for AI | `food/history.html` |
| `resources_list` | resources | Display all resources | `resources/resources_list.html` |
| `resources_by_category` | resources | Filter by category | `resources/resources_by_category.html` |
| `recommended_resources` | resources | Rule-based recommendations | `resources/recommendations.html` |
| `upload_form` | uploads | Upload images | `uploads/upload_form.html` |
| `upload_list` | uploads | View all uploads | `uploads/upload_list.html` |
| `link_to_inventory` | uploads | Link image to item/log | `uploads/link_to_inventory.html` |

### **URL Patterns**

| URL Pattern | App | View | Name |
|-------------|-----|------|------|
| `/` | - | dashboard_view | dashboard |
| `/admin/` | - | Django Admin | - |
| `/users/login/` | users | login_view | users:login |
| `/users/register/` | users | register_view | users:register |
| `/users/profile/` | users | profile_view | users:profile |
| `/users/profile/edit/` | users | profile_edit_view | users:profile_edit |
| `/users/logout/` | users | logout_view | users:logout |
| `/food/inventory/` | food | inventory_list | food:inventory_list |
| `/food/inventory/add/` | food | inventory_form | food:inventory_form |
| `/food/inventory/<pk>/edit/` | food | inventory_edit | food:inventory_edit |
| `/food/inventory/<pk>/delete/` | food | inventory_delete | food:inventory_delete |
| `/food/logs/` | food | consumption_logs_list | food:logs_list |
| `/food/logs/add/` | food | consumption_log_form | food:log_form |
| `/food/history/` | food | consumption_history | food:history |
| `/resources/` | resources | resources_list | resources:resources_list |
| `/resources/category/<category>/` | resources | resources_by_category | resources:resources_by_category |
| `/resources/recommendations/` | resources | recommended_resources | resources:recommendations |
| `/uploads/` | uploads | upload_form | uploads:upload_form |
| `/uploads/list/` | uploads | upload_list | uploads:upload_list |
| `/uploads/<pk>/link/` | uploads | link_to_inventory | uploads:link_to_inventory |

---

## 🎯 Implementation Status by Phase

### ✅ Phase 1: Project Setup & Database Modeling
- [x] Django project initialized
- [x] Apps created (users, food, resources, uploads)
- [ ] **TODO:** Define models in each app
- [ ] **TODO:** Run migrations

### ✅ Phase 2: Authentication & User Management
- [x] Login/Register URLs created
- [x] View placeholders ready
- [ ] **TODO:** Implement authentication logic
- [ ] **TODO:** Add form validation
- [ ] **TODO:** Session/token management

### ❌ Phase 3: Database Seeding (CRITICAL)
- [ ] **TODO:** Create seed script (`python manage.py seed_data`)
- [ ] **TODO:** Seed 15-20 food items
- [ ] **TODO:** Seed 15-20 resources (4 categories)

### 🟡 Phase 4: Core Features
- [x] Inventory URLs & views created
- [x] Consumption log URLs & views created
- [ ] **TODO:** Implement CRUD operations
- [ ] **TODO:** Add filters (Category, Expiration)
- [ ] **TODO:** Store consumption data structurally

### ❌ Phase 5: Rule-Based Logic
- [x] Recommendation URL created
- [ ] **TODO:** Implement matching algorithm
- [ ] **TODO:** Display "Why this is recommended"

### 🟡 Phase 6: Image Upload Infrastructure
- [x] Upload URLs & views created
- [ ] **TODO:** Implement file storage
- [ ] **TODO:** Add manual linking functionality
- [ ] **TODO:** Validate JPG/PNG only

### ✅ Phase 7: Dashboard & UI
- [x] Dashboard template created
- [x] Navbar with all links
- [ ] **TODO:** Integrate widgets (profile, activity, summary, recommendations)
- [ ] **TODO:** Ensure mobile responsiveness

### ❌ Phase 8: Documentation & Delivery
- [x] Project structure documented
- [ ] **TODO:** Write comprehensive README.md
- [ ] **TODO:** Add .env.example
- [ ] **TODO:** Test on fresh machine

---

## 🚨 Missing Critical Components

### **High Priority (Must Complete Before Hackathon)**

1. **Database Models** (`models.py` in each app)
   - All models are currently empty
   - Need to implement schema from target.json

2. **Database Seeding** (Phase 3 - MANDATORY)
   - No seed data exists
   - Create `management/commands/seed_data.py` in each app

3. **Authentication Logic** (Phase 2)
   - Views are placeholders only
   - Implement Django's auth system or JWT

4. **Form Validation** (Phase 2, 4)
   - No forms.py files exist
   - Create forms for registration, inventory, logs

5. **CRUD Operations** (Phase 4)
   - Views have TODO comments
   - Implement actual database queries

6. **Recommendation Engine** (Phase 5)
   - Rule-based matching logic needed
   - Example: Dairy → Dairy storage tips

### **Medium Priority**

7. **File Upload Handler** (Phase 6)
   - Storage location not configured
   - Need to handle file validation

8. **Dashboard Widgets** (Phase 7)
   - Currently static HTML
   - Need dynamic data from database

9. **API Endpoints** (Future-proofing)
   - Consider adding `/api/` endpoints for Part 2

### **Low Priority (Nice to Have)**

10. **Unit Tests** (`tests.py`)
    - All test files empty
    - Write tests for critical logic

11. **Admin Panel Configuration** (`admin.py`)
    - Need to register models

---

## 🏗️ Suggested File Structure Improvements

### **Industry Best Practices**

1. **Create `forms.py` in each app**
```
users/forms.py       # UserRegistrationForm, LoginForm, ProfileForm
food/forms.py        # FoodItemForm, ConsumptionLogForm
uploads/forms.py     # ImageUploadForm
```

2. **Create `serializers.py` for API (Part 2 prep)**
```
users/serializers.py
food/serializers.py
resources/serializers.py
```

3. **Add `management/commands/` for seed scripts**
```
food/management/commands/seed_food.py
resources/management/commands/seed_resources.py
```

4. **Create `utils.py` for helper functions**
```
food/utils.py        # Expiration checker, recommendation matcher
resources/utils.py   # Category filtering logic
```

5. **Add `middleware.py` for custom middleware**
```
users/middleware.py  # Authentication middleware
```

6. **Create `.env` for environment variables**
```
SECRET_KEY=your-secret-key
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
MEDIA_ROOT=/media/
```

7. **Separate settings for dev/prod**
```
Platform/settings/
├── __init__.py
├── base.py       # Common settings
├── development.py
└── production.py
```

---

## 🔄 Data Flow

### **User Registration Flow**
```
User fills form → register_view → Validate data → Create User model → Redirect to login
```

### **Inventory Management Flow**
```
User adds item → inventory_form → Validate → Create FoodItem → List view with filters
```

### **Consumption Logging Flow**
```
User logs usage → log_form → Create ConsumptionLog → Store for AI analysis → History view
```

### **Recommendation Flow (Phase 5)**
```
User logs "Milk" → Rule engine checks category "Dairy" → 
Query resources WHERE category="Dairy Storage" → Display with reason
```

### **Image Upload Flow**
```
User uploads image → upload_form → Store file → Create Upload model → 
Manual link to FoodItem/ConsumptionLog
```

---

## 📊 Database Relationships

```
User (1) ──── (Many) FoodItem
User (1) ──── (Many) ConsumptionLog
User (1) ──── (Many) Upload

FoodItem (1) ──── (Many) Upload
ConsumptionLog (1) ──── (Many) Upload

Resource (Independent - seeded data)
```

---

## 🎨 Frontend Assets

### **Installed Libraries**
- **Tailwind CSS** (via CDN) - Utility-first CSS
- **GSAP 3.13.0** - Advanced animations
- **Swiper 12.0.3** - Touch slider
- **Framer Motion 12.23.24** - React animations (for future use)
- **Inter Font** - Typography

### **Custom Styles**
- Greenish theme (#10b981, #059669)
- Gradient backgrounds
- Hover effects with cubic-bezier transitions
- Mobile-responsive design

---

## 🚀 Next Steps (Prioritized)

1. **Define all database models** (1-2 hours)
2. **Run migrations** (`python manage.py makemigrations && migrate`)
3. **Create seed scripts** (2-3 hours)
4. **Implement authentication** (3-4 hours)
5. **Build inventory CRUD** (4-5 hours)
6. **Implement consumption logging** (3-4 hours)
7. **Add rule-based recommendations** (2-3 hours)
8. **File upload functionality** (2-3 hours)
9. **Dynamic dashboard** (3-4 hours)
10. **Write README.md** (1 hour)

**Total Estimated Time:** 22-30 hours

---

## 📝 Notes

- **No AI processing** required for Part 1 (rule-based logic only)
- Data structures must support **AI integration in Part 2**
- Mobile-responsive design is **essential**
- **Database seeding is MANDATORY** (15-20 items each)
- Project must run on **fresh machine** following README

---

**Last Updated:** November 20, 2025  
**Project Phase:** Part 1 Foundation (Pre-Hackathon)  
**Status:** 40% Complete (Structure ready, logic pending)
