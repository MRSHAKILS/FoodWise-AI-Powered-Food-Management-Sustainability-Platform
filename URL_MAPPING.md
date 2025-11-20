# 🔗 Complete URL Mapping - AI Food Management Platform

## 📌 Quick Reference

| Status | URL | App | View | Template | Purpose |
|--------|-----|-----|------|----------|---------|
| ✅ | `/` | - | dashboard_view | `dashboard.html` | Landing page after login |
| ✅ | `/admin/` | - | Django Admin | - | Admin panel |

---

## 👥 Users App (`/users/`)

### Authentication & Profile

| Status | URL | Method | View | Template | Purpose | Phase |
|--------|-----|--------|------|----------|---------|-------|
| 🟡 | `/users/register/` | GET, POST | register_view | `users/register.html` | User registration with household details | Phase 2 |
| 🟡 | `/users/login/` | GET, POST | login_view | `users/login.html` | User authentication | Phase 2 |
| 🔴 | `/users/logout/` | POST | logout_view | Redirect | Logout and clear session | Phase 2 |
| 🟡 | `/users/profile/` | GET | profile_view | `users/profile.html` | Display user profile | Phase 2 |
| 🔴 | `/users/profile/edit/` | GET, POST | profile_edit_view | `users/profile_edit.html` | Edit dietary preferences, budget, etc. | Phase 2 |

**Legend:** ✅ Complete | 🟡 Partial (URL exists, logic pending) | 🔴 Missing implementation

### Required Form Fields

**Registration Form:**
- full_name (required)
- email (required, unique, validated)
- password (required, min 8 chars)
- confirm_password (required, must match)
- household_size (integer)
- dietary_preferences (text/choices)
- location (text)
- budget_range (choices: Low/Medium/High)

**Login Form:**
- email (required)
- password (required)
- remember_me (optional checkbox)

---

## 🍎 Food App (`/food/`)

### Inventory Management (Phase 4)

| Status | URL | Method | View | Template | Purpose | Implementation Status |
|--------|-----|--------|------|----------|---------|---------------------|
| 🟡 | `/food/inventory/` | GET | inventory_list | `food/inventory_list.html` | List all food items with filters | Query FoodItem model |
| 🔴 | `/food/inventory/add/` | GET, POST | inventory_form | `food/inventory_form.html` | Add new food item | Form validation needed |
| 🔴 | `/food/inventory/<int:pk>/edit/` | GET, POST | inventory_edit | `food/inventory_edit.html` | Edit existing food item | CRUD logic needed |
| 🔴 | `/food/inventory/<int:pk>/delete/` | POST | inventory_delete | Redirect | Delete food item with confirmation | Delete logic needed |

**Query Parameters for `/food/inventory/`:**
- `?category=dairy` - Filter by category
- `?expiring=7` - Items expiring in next 7 days
- `?sort=expiry_date` - Sort by expiration

### Consumption Logs (Phase 4)

| Status | URL | Method | View | Template | Purpose | Implementation Status |
|--------|-----|--------|------|----------|---------|---------------------|
| 🔴 | `/food/logs/` | GET | consumption_logs_list | `food/logs_list.html` | View all consumption logs | Query ConsumptionLog model |
| 🔴 | `/food/logs/add/` | GET, POST | consumption_log_form | `food/log_form.html` | Manual entry: log daily food usage | Form: item, quantity, category |
| 🔴 | `/food/logs/<int:pk>/delete/` | POST | consumption_log_delete | Redirect | Delete consumption log | Delete logic needed |
| 🔴 | `/food/history/` | GET | consumption_history | `food/history.html` | Historical consumption data | Data visualization for AI prep |

**Consumption Log Form Fields:**
- item_name (required, text or dropdown)
- quantity (required, decimal with unit)
- category (required, choices from FoodItem)
- date_logged (auto or manual)
- notes (optional)

---

## 📚 Resources App (`/resources/`)

### Educational Content (Phase 3 & 5)

| Status | URL | Method | View | Template | Purpose | Implementation Status |
|--------|-----|--------|------|----------|---------|---------------------|
| 🟡 | `/resources/` | GET | resources_list | `resources/resources_list.html` | Display all resources (15-20 seeded) | Query Resource model |
| 🔴 | `/resources/category/<str:category>/` | GET | resources_by_category | `resources/resources_by_category.html` | Filter by category | Category filtering logic |
| 🔴 | `/resources/<int:pk>/` | GET | resource_detail | `resources/resource_detail.html` | Single resource detailed view | Display full content |
| 🔴 | `/resources/recommendations/` | GET | recommended_resources | `resources/recommendations.html` | Rule-based recommendations | Phase 5 matching algorithm |

**Resource Categories (Must Seed):**
1. Waste Reduction
2. Budget Tips
3. Meal Planning
4. Storage Tips

**Recommendation Logic Example:**
```python
# IF user logs item with category "Dairy"
# THEN suggest resources WHERE category="Dairy Storage" 
# DISPLAY: "Recommended because: You recently logged Milk (Dairy)"
```

---

## 📸 Uploads App (`/uploads/`)

### Image Upload Infrastructure (Phase 6)

| Status | URL | Method | View | Template | Purpose | Implementation Status |
|--------|-----|--------|------|----------|---------|---------------------|
| 🟡 | `/uploads/` | GET, POST | upload_form | `uploads/upload_form.html` | Upload food label/receipt (JPG/PNG) | File storage only, NO OCR |
| 🔴 | `/uploads/list/` | GET | upload_list | `uploads/upload_list.html` | View all user uploads | Query Upload model |
| 🔴 | `/uploads/<int:pk>/` | GET | upload_detail | `uploads/upload_detail.html` | View single upload with metadata | Display image + info |
| 🔴 | `/uploads/<int:pk>/delete/` | POST | upload_delete | Redirect | Delete uploaded file | File + DB deletion |
| 🔴 | `/uploads/<int:pk>/link/` | GET, POST | link_to_inventory | `uploads/link_to_inventory.html` | Manually link image to item/log | Linking logic |

**Upload Form Fields:**
- file (required, JPG/PNG only)
- description (optional)
- upload_type (choices: Label, Receipt, Other)
- link_to (optional, dropdown of FoodItems/Logs)

**Storage Configuration Needed:**
```python
# settings.py
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## 🔒 Authentication Flow

### Login Required Decorator
All URLs except `/users/login/` and `/users/register/` should require authentication:

```python
from django.contrib.auth.decorators import login_required

@login_required(login_url='users:login')
def dashboard_view(request):
    ...
```

### Redirect Logic
- After login → `/` (dashboard)
- After logout → `/users/login/`
- After registration → `/users/login/` (with success message)
- Unauthorized access → `/users/login/?next=/food/inventory/`

---

## 📊 Dashboard Widgets (Phase 7)

The dashboard (`/`) should display:

1. **Quick Profile View**
   - User's name
   - Household size
   - Dietary preferences

2. **Recent Activity**
   - Last 5 consumption logs
   - Recently added inventory items

3. **Inventory Summary**
   - Total items count
   - Items expiring soon (next 7 days)
   - Low stock alerts

4. **Recommended Resources** (from Phase 5 logic)
   - Based on recent consumption logs
   - Matched by category

---

## 🔍 Filter & Search Parameters

### Inventory Filters
```
/food/inventory/?category=dairy
/food/inventory/?expiring=7
/food/inventory/?sort=expiry_date
/food/inventory/?search=milk
```

### Resource Filters
```
/resources/?category=waste-reduction
/resources/?type=article
/resources/?type=video
```

### Logs Filters
```
/food/logs/?date_from=2025-01-01
/food/logs/?date_to=2025-12-31
/food/logs/?category=dairy
```

---

## 📱 Navbar Structure (Phase 7 Requirement)

The navbar should include:
- ✅ Dashboard (`/`)
- ✅ Inventory (`/food/inventory/`)
- 🔴 Logs (`/food/logs/`) - **MISSING FROM NAVBAR**
- ✅ Resources (`/resources/`)
- ✅ Upload (`/uploads/`)
- 🔴 Profile (`/users/profile/`) - **MISSING FROM NAVBAR**
- 🔴 Logout (`/users/logout/`) - **MISSING FROM NAVBAR**

**Action Required:** Update `templates/navbar.html` to include Logs, Profile, and Logout links.

---

## 🚨 Critical Missing URLs (Must Add)

### **URGENT - Phase 4 Requirements**

1. **Consumption Logs** ❌
   - Need prominent link in navbar
   - Core feature for Part 1 completion

2. **Profile Management** ❌
   - User should be able to edit dietary preferences
   - Required for Phase 2 completion

3. **Logout** ❌
   - Basic security requirement
   - Must clear session

### **HIGH PRIORITY - Phase 5**

4. **Recommendations Page** ❌
   - Rule-based matching not implemented
   - Need to show "why" for each suggestion

### **MEDIUM PRIORITY - Phase 6**

5. **Upload List View** ❌
   - Users can't see their uploads
   - Linking functionality incomplete

---

## 🧪 Testing Checklist

### Registration & Login
- [ ] Can create new user with all required fields
- [ ] Email validation works
- [ ] Password strength validation
- [ ] Login with valid credentials
- [ ] Login fails with invalid credentials
- [ ] Redirect to dashboard after login

### Inventory Management
- [ ] Can view empty inventory
- [ ] Can add new food item
- [ ] Can edit existing item
- [ ] Can delete item with confirmation
- [ ] Filters work (category, expiration)
- [ ] Pagination for large lists

### Consumption Logs
- [ ] Can log daily usage
- [ ] Form validates quantity
- [ ] History displays correctly
- [ ] Can delete logs

### Resources
- [ ] All 15-20 resources display
- [ ] Category filter works
- [ ] Detail page shows full content
- [ ] Recommendations match user logs

### Uploads
- [ ] Can upload JPG/PNG only
- [ ] Other formats rejected
- [ ] Can view upload list
- [ ] Can link to inventory item
- [ ] Can delete upload

---

## 🔐 Security Considerations

### CSRF Protection
All POST requests must include `{% csrf_token %}` in forms.

### File Upload Security
```python
# Validate file type
ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png']

# Limit file size
MAX_UPLOAD_SIZE = 5242880  # 5MB
```

### SQL Injection Prevention
Always use Django ORM, never raw SQL without parameterization.

### XSS Protection
Templates auto-escape by default. Use `|safe` only when necessary.

---

## 📚 API Endpoints (Future - Part 2)

Consider adding REST API for Part 2:

```
GET    /api/inventory/           # List all items
POST   /api/inventory/           # Create item
GET    /api/inventory/<pk>/      # Get single item
PUT    /api/inventory/<pk>/      # Update item
DELETE /api/inventory/<pk>/      # Delete item

GET    /api/logs/                # List logs
POST   /api/logs/                # Create log

GET    /api/resources/           # List resources
GET    /api/recommendations/     # AI recommendations
```

**Framework:** Django REST Framework

---

## 📝 Next Steps for URL Completion

1. **Update navbar** to include Logs, Profile, Logout
2. **Implement missing views** (17 functions have TODO comments)
3. **Create forms.py** for all input validation
4. **Add login_required** decorators
5. **Test all URL patterns** with `python manage.py show_urls`
6. **Add unit tests** for each URL endpoint

---

**Last Updated:** November 20, 2025  
**Total URLs:** 29 endpoints  
**Implemented:** 8 (28%)  
**Pending Logic:** 21 (72%)  
**Critical Missing:** Logs, Profile Edit, Logout, Recommendations
