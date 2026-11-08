# 🍽️ FoodWise - AI-Powered Food Management & Sustainability Platform

> **Innovatex Hackathon - Part 1: Pre-Hack Foundation**  
> Reducing food waste, promoting responsible consumption, and supporting SDG 2 (Zero Hunger) & SDG 12 (Responsible Consumption)

[![Django](https://img.shields.io/badge/Django-5.2.6-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.13-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Part%201%20Complete-success.svg)](https://github.com/MRSHAKILS/AI-Powered-Food-Management-Sustainability-Platform)

---

## 📋 Project Overview

**FoodWise** is a full-stack food management platform designed to help households track their food inventory, monitor expiry dates, log daily consumption, and reduce food waste through intelligent recommendations. Built for the **Innovatex Hackathon**, this project addresses critical sustainability challenges by empowering users to make informed decisions about their food consumption patterns.

### 🎯 Key Features (Part 1 - COMPLETE)

- ✅ **User Authentication System** - Secure registration/login with household profiles and budget tracking
- ✅ **Smart Inventory Management** - Track food items with categories, quantities, expiry dates, and costs
- ✅ **Consumption Logging** - Record daily food usage with detailed history and statistics
- ✅ **Food Items Database (PART 4)** - 20+ pre-seeded common food items with nutritional info
- ✅ **Educational Resources (PART 5)** - 20+ pre-seeded resources for waste reduction and sustainability
- ✅ **Rule-Based Recommendations (PART 6)** - 5 intelligent rules for personalized resource suggestions
- ✅ **Dashboard Analytics (PART 6)** - Real-time summary with expiring items alerts and category breakdowns
- ✅ **Image Upload Infrastructure (PART 7)** - Upload receipts/food labels with drag-and-drop interface
- ✅ **Interactive Dashboard** - Beautiful UI with GSAP animations, charts, and responsive design

---

## 🛠️ Tech Stack

### **Backend**

- **Framework:** Django 5.2.6 (Python 3.13.1)
- **Database:** SQLite (Development) / PostgreSQL (Production-ready)
- **Authentication:** Django's built-in auth system with session management
- **API:** Django REST Framework (optional for future mobile app)

### **Frontend**

- **Templating:** Django Templates (Jinja2 syntax)
- **Styling:** Tailwind CSS 3.x (CDN)
- **Animations:** GSAP 3.12.2 + ScrollTrigger
- **Components:** Swiper.js 11.x (Sliders/Carousels)
- **Motion:** Framer Motion 12.23.24 (React-style animations)

### **Development Tools**

- **Version Control:** Git + GitHub
- **Virtual Environment:** Python venv
- **Package Management:** pip + npm
- **Code Editor:** VS Code (recommended)

---

## 📂 Project Structure

```
AI-Powered-Food-Management-Sustainability-Platform/
│
├── 📁 Platform/                    # Django Project Configuration
│   ├── settings.py                 # Core settings (DB, APPS, MIDDLEWARE)
│   ├── urls.py                     # Main URL router
│   ├── wsgi.py / asgi.py          # Deployment configs
│
├── 📁 users/                       # User Management App
│   ├── models.py                   # User model (household_size, dietary_preferences, etc.)
│   ├── views.py                    # Authentication logic (login, register, profile)
│   ├── urls.py                     # User routes
│   └── templates/users/            # Login, register, profile pages
│
├── 📁 food/                        # Inventory & Consumption Logging (PART 4 & 6)
│   ├── models.py                   # FoodItem, ConsumptionLog, FoodItemDatabase models
│   ├── views.py                    # CRUD operations, dashboard API, recommendations API
│   ├── utils.py                    # calculate_dashboard_summary(), generate_recommendations()
│   ├── urls.py                     # Inventory routes + API endpoints
│   ├── templates/food/             # Inventory list, forms, logs, history
│   └── management/commands/        # seed_food.py (20 items with nutritional data)
│
├── 📁 resources/                   # Educational Resources (PART 5)
│   ├── models.py                   # Resource model (title, description, category, type, tags)
│   ├── views.py                    # Resource list with filters and search
│   ├── urls.py                     # Resource routes
│   ├── templates/resources/        # Resource pages with filtering
│   └── management/commands/        # seed_resources.py (20 resources)
│
├── 📁 uploads/                     # Image Upload Infrastructure (PART 7)
│   ├── models.py                   # Upload model (file, file_type, associations, validation)
│   ├── forms.py                    # UploadForm with file validation (JPG/PNG, max 5MB)
│   ├── views.py                    # File handling, gallery, associations, API
│   ├── urls.py                     # Upload routes + API endpoint
│   └── templates/uploads/          # upload_form.html (drag-and-drop), uploads_list.html (gallery)
│
├── 📁 templates/                   # Global Templates
│   ├── base.html                   # Base template (navbar, footer)
│   ├── navbar.html                 # Navigation component
│   ├── footer.html                 # Footer component
│   └── dashboard.html              # Landing page
│
├── 📁 static/                      # Static Assets
│   ├── css/                        # Custom CSS
│   ├── js/                         # Custom JavaScript
│   └── images/                     # Logos, icons
│
├── 📁 media/                       # User Uploads (Created on first upload)
│   └── uploads/                    # Receipt/food images
│
├── 📁 myenv/                       # Python Virtual Environment
│
├── 📄 manage.py                    # Django CLI
├── 📄 db.sqlite3                   # SQLite Database
├── 📄 requirements.txt             # Python Dependencies
├── 📄 package.json                 # Node.js Dependencies
├── 📄 target.json                  # Hackathon Requirements
├── 📄 PROJECT_STRUCTURE.md         # Detailed Documentation
└── 📄 README.md                    # This File
```

---

## 🚀 Setup Instructions

### **Prerequisites**

Before you begin, ensure you have the following installed:

- **Python 3.11+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** (Optional, for frontend tooling) ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/downloads))

---

### **Step 1: Clone the Repository**

```bash
git clone https://github.com/MRSHAKILS/AI-Powered-Food-Management-Sustainability-Platform.git
cd AI-Powered-Food-Management-Sustainability-Platform
```

---

### **Step 2: Create Virtual Environment**

**Windows (PowerShell):**

```powershell
python -m venv myenv
myenv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv myenv
source myenv/bin/activate
```

---

### **Step 3: Install Python Dependencies**

```bash
pip install -r requirements.txt
```

**Core Dependencies:**

```
Django==5.2.6               # Web framework
Pillow==10.4.0              # Image handling for ImageField
python-decouple==3.8        # Environment variables (optional)
djangorestframework==3.15.2 # API (optional for future)
```

**Installed Successfully:**

```bash
pip list | grep -E "Django|Pillow"
# Django    5.2.6
# Pillow    10.4.0
```

---

### **Step 4: Install Node.js Dependencies (Optional)**

```bash
npm install
```

**Packages (Already included via CDN):**

- GSAP 3.12.2
- Swiper.js 11.x
- Framer Motion 12.23.24

---

### **Step 5: Environment Configuration**

Create a `.env` file in the root directory:

```env
# .env
DEBUG=True
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=sqlite:///db.sqlite3

# Google OAuth (django-allauth)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

# Google Gemini AI (for OCR food item extraction)
# Get your API key from: https://makersuite.google.com/app/apikey
GEMINI_API_KEY=your-gemini-api-key-here

# Email Configuration (Optional for Part 1)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Media Settings
MEDIA_ROOT=media/
MEDIA_URL=/media/
```

**Generate a new SECRET_KEY:**

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Get Gemini API Key:**

1. Visit https://makersuite.google.com/app/apikey
2. Create a new API key
3. Copy and add to `.env` as `GEMINI_API_KEY`

---

### **Step 6: Database Setup**

**Run Migrations:**

```bash
python manage.py makemigrations
python manage.py migrate
```

**Create Superuser (Admin Access):**

```bash
python manage.py createsuperuser
# Follow prompts to set username, email, password
```

---

### **Step 7: Seed Database (MANDATORY - PART 4 & 5)**

⚠️ **Critical Step:** The platform requires initial data to function properly.

**Seed Food Items Database (PART 4 - 20 items):**

```bash
python manage.py seed_food
```

**Seed Educational Resources (PART 5 - 20 resources):**

```bash
python manage.py seed_resources
```

**What gets seeded:**

**PART 4 - Food Items Database (20 items):**

- **Dairy:** Milk, Eggs, Yogurt, Cheese (Cheddar), Butter
- **Protein:** Chicken Breast, Lentils (Red)
- **Grains:** Rice (White), Bread (Whole Wheat), Pasta
- **Fruits:** Bananas, Apples
- **Vegetables:** Tomatoes, Potatoes, Onions, Carrots, Spinach, Cucumber
- **Beverages:** Orange Juice
- **Other:** Cooking Oil
- **Each item includes:** category, typical_expiration_days, sample_cost_per_unit, unit, storage_instructions, nutritional_info (calories, protein, carbs, fat)

**PART 5 - Resources Database (20 resources):**

- **Storage Tips (6):** Dairy Storage, Vegetable Storage, Freezing Guide, Fruit Ripening, Grain Storage, Herb/Spice Storage
- **Budget Tips (3):** Meal Planning, Protein on Budget, Vegetarian Meals
- **Waste Reduction (5):** Food Waste Reduction, Expiration Dates, Composting, Leftover Ideas, FIFO Method
- **Meal Planning (2):** Batch Cooking, Shopping Lists
- **Nutrition (3):** Nutritional Labels, Portion Control, Hydration Basics
- **Sustainability (1):** Seasonal Eating Guide
- **Each resource includes:** title, description (100-500 chars), category, type (article/video/guide/tip), tags, relevant_food_categories, read_time

**Verify Seeding:**

```bash
# Check counts
python manage.py shell -c "from food.models import FoodItemDatabase; print(f'Food Items: {FoodItemDatabase.objects.count()}')"
python manage.py shell -c "from resources.models import Resource; print(f'Resources: {Resource.objects.count()}')"

# Expected output:
# Food Items: 20
# Resources: 20

# Or access Django Admin Panel
python manage.py runserver
# Visit: http://127.0.0.1:8000/admin/
# Login with superuser credentials
# Check: Food > Food Item Database & Resources > Resources
```

---

### **Step 8: Run Development Server**

```bash
python manage.py runserver
```

**Access the Platform:**

- **Home/Landing:** http://127.0.0.1:8000/
- **Dashboard:** http://127.0.0.1:8000/dashboard/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **User Profile:** http://127.0.0.1:8000/users/profile/
- **Inventory:** http://127.0.0.1:8000/food/inventory/
- **Consumption Logs:** http://127.0.0.1:8000/food/logs/
- **Food Items Database (PART 4):** http://127.0.0.1:8000/food/items/
- **Resources (PART 5):** http://127.0.0.1:8000/resources/
- **Uploads (PART 7):** http://127.0.0.1:8000/uploads/

**API Endpoints (PART 6):**

- **Dashboard Summary:** http://127.0.0.1:8000/food/api/dashboard/summary/
- **Recommendations:** http://127.0.0.1:8000/food/api/recommendations/

---

### **Step 9: Create Media Directory (For Uploads)**

```bash
# Windows
mkdir media\uploads

# macOS/Linux
mkdir -p media/uploads
```

---

## 📱 Usage Guide

### **1. Register/Login**

- Navigate to `/users/register/` to create an account
- Provide household size, dietary preferences, location, budget range
- Login at `/users/login/`

### **2. Add Food Items**

- Go to "Inventory" → "Add New Item"
- Fill in: Item name, category, quantity, unit, expiry date, cost (optional)
- Select category: Vegetables, Fruits, Dairy, Protein, Grains, or Snacks

### **3. View Inventory**

- Access `/food/inventory/` to see all items
- Filter by category or search by name
- Sort by expiry date, quantity, or category
- View stats: Total items, expiring soon, fresh items, total value

### **4. Log Consumption**

- Navigate to `/food/logs/` to record daily usage
- Enter item name, quantity consumed, category
- View consumption history at `/food/history/`

### **5. Browse Food Items Database (PART 4)**

- Visit `/food/items/` to browse 20 pre-seeded food items
- Search by name or filter by category
- View detailed nutritional info, storage instructions, and typical expiration days
- Use as reference when adding inventory items

### **6. Explore Educational Resources (PART 5)**

- Visit `/resources/` for 20 pre-seeded educational resources
- Filter by category: Waste Reduction, Budget Tips, Meal Planning, Storage Tips, Nutrition, Sustainability
- Filter by type: Article, Video, Infographic, Guide, Tip
- Search by keywords in title or description
- View read time estimates

### **7. View Dashboard Analytics (PART 6)**

- Access `/dashboard/` for real-time summary
- See statistics: Total inventory items, total value, recent logs count, items expiring soon
- Get expiring items alerts with urgency levels (urgent: ≤2 days, warning: 3-7 days)
- View category breakdown of consumption logs
- See most logged category
- Get personalized resource recommendations based on 5 rules

### **8. Upload Images (PART 7)**

- Go to `/uploads/` to see your uploads gallery
- Click "Upload New Image" for drag-and-drop interface
- Upload receipts or food labels (JPG/PNG only, max 5MB)
- View image preview before upload
- Add file type (receipt/food_label/other) and notes
- **🤖 NEW: Check "Process with AI" to automatically extract food items using Google Gemini Vision**
- AI will detect food items, quantities, expiration dates, and automatically add them to your inventory
- View uploads list with filters and statistics
- Manually link uploads to inventory items or consumption logs
- Delete uploads with confirmation
- Process uploaded images anytime from detail view

**AI OCR Features:**

- **Automatic Food Detection:** Gemini AI recognizes food items in images
- **Quantity Extraction:** Detects amounts and units (kg, liters, pieces, etc.)
- **Expiration Date Recognition:** Reads expiry dates from labels
- **Category Classification:** Auto-categorizes items (dairy, vegetable, fruit, etc.)
- **Instant Inventory:** Creates `FoodItem` entries automatically
- **Processing Status:** See which uploads have been AI-processed

---

## 🔧 Configuration Details

### **Database Schema**

**Users Table:**

```python
- full_name: CharField
- email: EmailField (unique)
- password_hash: CharField (hashed)
- household_size: IntegerField
- dietary_preferences: CharField (e.g., "Vegetarian", "Vegan")
- location: CharField
- budget_range: CharField (e.g., "Low", "Medium", "High")
```

**FoodItem Table (Inventory):**

```python
- user: ForeignKey (User)
- name: CharField
- quantity: DecimalField
- unit: CharField (kg, g, liter, ml, piece, etc.)
- category: CharField (vegetable, fruit, dairy, meat, grain, beverage, snack, other)
- purchase_date: DateField
- expiration_date: DateField (nullable)
- price: DecimalField (nullable)
- notes: TextField
- created_at: DateTimeField (auto)
- updated_at: DateTimeField (auto)
```

**FoodItemDatabase Table (PART 4 - Master Database):**

```python
- item_name: CharField (unique)
- category: CharField (fruit, dairy, grain, vegetable, protein, snacks, beverages, other)
- typical_expiration_days: IntegerField
- sample_cost_per_unit: DecimalField
- unit: CharField (kg, g, liter, ml, dozen, piece, loaf, bunch, 500g)
- nutritional_info: JSONField (calories, protein, carbs, fat)
- storage_instructions: TextField
- image_url: URLField (optional)
- created_at: DateTimeField (auto)
```

**ConsumptionLog Table:**

```python
- user: ForeignKey (User)
- item_name: CharField
- quantity: DecimalField
- unit: CharField
- category: CharField (vegetable, fruit, dairy, meat, grain, beverage, snack, other)
- consumption_date: DateField
- notes: TextField
- created_at: DateTimeField (auto)
```

**Resource Table (PART 5 - Educational Resources):**

```python
- title: CharField (max 200)
- description: TextField (100-500 chars)
- url: URLField (optional external link)
- category: CharField (waste_reduction, budget_tips, meal_planning, storage_tips, nutrition, sustainability)
- type: CharField (article, video, infographic, guide, tip)
- tags: JSONField (array of keywords)
- relevant_food_categories: JSONField (array: dairy, vegetable, fruit, grain, protein, all)
- read_time: IntegerField (minutes, nullable)
- created_at: DateTimeField (auto)
```

**Upload Table (PART 7 - Image Upload):**

```python
- user: ForeignKey (User)
- file_name: CharField (original filename)
- file: ImageField (upload_to='uploads/', validators: JPG/PNG only, max 5MB)
- file_type: CharField (receipt, food_label, other)
- mime_type: CharField (auto-detected)
- file_size: IntegerField (bytes, auto-set)
- associated_inventory: ForeignKey (FoodItem, nullable)
- associated_log: ForeignKey (ConsumptionLog, nullable)
- upload_date: DateTimeField (auto)
- notes: TextField
- processed: BooleanField (default False, for future AI processing)
```

---

## 🧪 Running Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test users
python manage.py test food
python manage.py test resources
python manage.py test uploads

# Run with verbose output
python manage.py test --verbosity=2
```

---

## 📊 API Endpoints

### **PART 6 - Dashboard & Recommendations (IMPLEMENTED)**

**Dashboard Summary API:**

```http
GET /food/api/dashboard/summary/
Authentication: Required (login_required)

Response (200 OK):
{
    "total_inventory_items": 12,
    "total_inventory_value": 1250.50,
    "recent_logs_count": 8,
    "items_expiring_soon": 3,
    "expiring_items": [
        {
            "id": 5,
            "name": "Milk",
            "quantity": "2.00",
            "unit": "liter",
            "category": "dairy",
            "expiration_date": "2025-11-23",
            "days_left": 2,
            "urgency": "urgent"
        }
    ],
    "most_logged_category": "vegetable",
    "category_breakdown": {
        "vegetable": 15,
        "fruit": 10,
        "dairy": 8
    }
}
```

**Recommendations API:**

```http
GET /food/api/recommendations/
Authentication: Required (login_required)

Response (200 OK):
[
    {
        "resource": {
            "id": 1,
            "title": "How to Store Dairy Products Properly",
            "description": "Learn the best practices...",
            "category": "storage_tips",
            "category_display": "Storage Tips",
            "type": "article",
            "type_display": "Article",
            "url": "",
            "tags": ["dairy", "storage", "refrigeration"],
            "read_time": 5
        },
        "reason": "You have dairy products - learn proper storage techniques",
        "relevance_score": 9,
        "matched_rule": "category_match"
    }
]
```

**Upload Association API:**

```http
POST /uploads/api/<int:pk>/associate/
Authentication: Required (login_required)
Content-Type: application/json

Request Body:
{
    "link_type": "inventory",  // or "log"
    "item_id": 5
}

Response (200 OK):
{
    "success": true,
    "message": "Upload linked to inventory item successfully"
}
```

### **Future Implementation (Part 2)**

**Authentication:**

- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user

**Inventory:**

- `GET /api/inventory/` - List all items
- `POST /api/inventory/` - Add new item
- `PUT /api/inventory/<id>/` - Update item
- `DELETE /api/inventory/<id>/` - Delete item

**Resources:**

- `GET /api/resources/` - List all resources
- `GET /api/resources/<id>/` - Get resource details

---

## 🎨 Customization

### **Change Theme Colors**

Edit `base.html` or create custom CSS in `static/css/`:

```css
/* Primary Color (Green Theme) */
--primary: #10b981;
--primary-dark: #059669;
--primary-light: #34d399;

/* Accent Colors */
--accent-blue: #3b82f6;
--accent-purple: #8b5cf6;
--accent-red: #ef4444;
```

### **Modify Animations**

Edit animation scripts in templates:

```javascript
// Adjust GSAP timing
gsap.from(".element", {
  opacity: 0,
  y: 30,
  duration: 0.6, // Change speed
  ease: "power3.out",
});
```

---

## 🐛 Troubleshooting

### **Issue: ModuleNotFoundError**

```bash
# Ensure virtual environment is activated
myenv\Scripts\activate  # Windows
source myenv/bin/activate  # macOS/Linux

# Reinstall dependencies
pip install -r requirements.txt
```

### **Issue: Database Locked**

```bash
# Close all Django shells/servers
# Delete db.sqlite3
rm db.sqlite3

# Recreate database
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_food
python manage.py seed_resources
```

### **Issue: Static Files Not Loading**

```bash
# Collect static files
python manage.py collectstatic --noinput

# Verify STATIC_URL in settings.py
STATIC_URL = '/static/'
```

### **Issue: Tailwind CSS Not Working**

Ensure CDN link in `base.html`:

```html
<script src="https://cdn.tailwindcss.com"></script>
```

### **Issue: GSAP/Swiper Not Animating**

Check console for errors. Verify CDN links:

```html
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
<link
  rel="stylesheet"
  href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css"
/>
```

---

## 🚢 Deployment Guide

### **Heroku Deployment**

1. **Install Heroku CLI** ([Download](https://devcenter.heroku.com/articles/heroku-cli))

2. **Create `Procfile`:**

```
web: gunicorn Platform.wsgi --log-file -
```

3. **Install Gunicorn:**

```bash
pip install gunicorn
pip freeze > requirements.txt
```

4. **Update `settings.py`:**

```python
import dj_database_url

ALLOWED_HOSTS = ['your-app-name.herokuapp.com', 'localhost']

# Database
DATABASES['default'] = dj_database_url.config(conn_max_age=600, ssl_require=True)

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
```

5. **Deploy:**

```bash
heroku login
heroku create your-app-name
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
heroku run python manage.py seed_food
heroku run python manage.py seed_resources
```

---

### **PythonAnywhere Deployment**

1. **Upload code** to PythonAnywhere
2. **Create virtual environment:**

```bash
mkvirtualenv myenv --python=/usr/bin/python3.11
pip install -r requirements.txt
```

3. **Configure WSGI:**

```python
import sys
path = '/home/yourusername/AI-Powered-Food-Management-Sustainability-Platform'
if path not in sys.path:
    sys.path.append(path)

os.environ['DJANGO_SETTINGS_MODULE'] = 'Platform.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

4. **Run migrations and seed data**

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. **Fork** the repository
2. **Create** a feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** your changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to the branch (`git push origin feature/AmazingFeature`)
5. **Open** a Pull Request

### **Code Style**

- Follow PEP 8 for Python code
- Use meaningful variable names
- Add comments for complex logic
- Write docstrings for functions/classes

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**Developer:** MRSHAKILS  
**Hackathon:** Innovatex 2025  
**Repository:** [GitHub](https://github.com/MRSHAKILS/AI-Powered-Food-Management-Sustainability-Platform)

---

## 🙏 Acknowledgments

- **UN SDG 2 & 12** for inspiring sustainable solutions
- **Django Community** for excellent documentation
- **Tailwind CSS** for rapid UI development
- **GSAP** for smooth animations
- **Swiper.js** for interactive components

---

## 📞 Support

For questions or issues:

- **GitHub Issues:** [Create an issue](https://github.com/MRSHAKILS/AI-Powered-Food-Management-Sustainability-Platform/issues)
- **Email:** support@foodwise.com
- **Documentation:** See `PROJECT_STRUCTURE.md` for detailed info

---

## 🗺️ Roadmap (Part 2 - Onsite Hackathon)

### **Part 1 Completion Summary:**

✅ All 8 core parts implemented from `.github/copilot-instructions.md`:

- ✅ PART 1: Authentication & User Management
- ✅ PART 2: User Profile & Food Logging
- ✅ PART 3: Inventory Management
- ✅ PART 4: Food Items Database (20 items seeded)
- ✅ PART 5: Resources Database (20 resources seeded)
- ✅ PART 6: Basic Tracking Logic (5 rules, 2 APIs)
- ✅ PART 7: Image Upload Infrastructure (drag-and-drop, gallery)
- ✅ PART 8: Documentation & Code Quality

### **Part 2 - Upcoming AI Features:**

- [x] **AI-Powered OCR** - Extract food data from images using Google Gemini Vision ✅
- [ ] **Smart Recipe Generation** - GPT-based recipes from current inventory
- [ ] **Expiry Prediction ML** - Predict waste patterns using historical data
- [ ] **Smart Expiry Alerts** - Email/SMS notifications for urgent items
- [ ] **Waste Analytics Dashboard** - ML-powered insights and trend analysis
- [ ] **Chatbot Assistant** - AI chatbot for cooking tips and substitutions
- [ ] **Mobile App** - React Native companion app
- [ ] **Social Features** - Share recipes and tips with community
- [ ] **Donation Integration** - Connect with food banks for surplus items
- [ ] **Blockchain Tracking** - Transparent food supply chain verification

---

## 📈 Project Status

**Part 1 Progress: 100% COMPLETE ✅**

✅ **PART 1: Authentication & User Management** (100%)

- User registration/login with Django auth
- Household profiles with size, dietary preferences, budget tracking
- Profile management with update functionality

✅ **PART 2: User Profile & Food Logging** (100%)

- Profile view and edit pages
- Consumption logging with CRUD operations
- Historical data view with statistics

✅ **PART 3: Inventory Management** (100%)

- Full CRUD for food items
- Category filtering and search
- Expiry date tracking with alerts

✅ **PART 4: Food Items Database** (100%)

- FoodItemDatabase model with 11 fields
- 20 pre-seeded items with nutritional data
- Browse/search interface with filters
- Seed command: `python manage.py seed_food`

✅ **PART 5: Resources Database** (100%)

- Resource model with 9 fields
- 20 pre-seeded educational resources
- Category/type filtering and search
- Seed command: `python manage.py seed_resources`

✅ **PART 6: Basic Tracking Logic** (100%)

- `calculate_dashboard_summary()` - 7 metrics calculation
- `generate_recommendations()` - 5 intelligent rules
- Dashboard summary API endpoint
- Recommendations API endpoint
- Urgency-based expiring items alerts
- Category-based resource matching

✅ **PART 7: Image Upload Infrastructure** (100%)

- Upload model with 11 fields + validation
- UploadForm with file type/size validation (JPG/PNG, max 5MB)
- Drag-and-drop upload interface with preview
- Gallery view with filters and statistics
- Association API for linking to inventory/logs
- 6 views: upload_form, upload_list, upload_detail, upload_delete, link_to_inventory, upload_associate_api

✅ **Frontend & UI** (100%)

- Responsive dashboard with GSAP animations
- Tailwind CSS styling throughout
- Interactive charts and statistics
- Real-time API data integration

✅ **Documentation** (100%)

- Comprehensive README with setup guide
- API documentation
- Database schema reference
- Troubleshooting guide

**All 8 Parts Implemented - Ready for Part 2 Onsite Hackathon!** 🚀

---

## ✅ Implementation Verification

### **Verify PART 4: Food Items Database**

```bash
# Check FoodItemDatabase model has all required fields
python manage.py shell -c "from food.models import FoodItemDatabase; print([f.name for f in FoodItemDatabase._meta.get_fields()])"

# Expected fields: id, item_name, category, typical_expiration_days, sample_cost_per_unit,
# unit, nutritional_info, storage_instructions, image_url, created_at

# Verify 20 items seeded
python manage.py shell -c "from food.models import FoodItemDatabase; print(f'Count: {FoodItemDatabase.objects.count()}')"
# Expected: Count: 20

# List all seeded items
python manage.py shell -c "from food.models import FoodItemDatabase; [print(f'{i.item_name} ({i.category})') for i in FoodItemDatabase.objects.all()]"
```

### **Verify PART 5: Resources Database**

```bash
# Check Resource model has all required fields
python manage.py shell -c "from resources.models import Resource; print([f.name for f in Resource._meta.get_fields()])"

# Expected fields: id, title, description, url, category, type, tags,
# relevant_food_categories, read_time, created_at

# Verify 20 resources seeded
python manage.py shell -c "from resources.models import Resource; print(f'Count: {Resource.objects.count()}')"
# Expected: Count: 20

# List all seeded resources by category
python manage.py shell -c "from resources.models import Resource; [print(f'{r.title} ({r.category})') for r in Resource.objects.all()]"
```

### **Verify PART 6: Tracking Logic**

```bash
# Test dashboard summary calculation
python manage.py shell
>>> from django.contrib.auth import get_user_model
>>> from food.utils import calculate_dashboard_summary
>>> User = get_user_model()
>>> user = User.objects.first()  # Get any user
>>> summary = calculate_dashboard_summary(user)
>>> print(summary.keys())
# Expected: dict_keys(['total_inventory_items', 'total_inventory_value', 'recent_logs_count',
# 'items_expiring_soon', 'expiring_items', 'most_logged_category', 'category_breakdown'])

# Test recommendations engine
>>> from food.utils import generate_recommendations
>>> recommendations = generate_recommendations(user)
>>> print(f'Recommendations count: {len(recommendations)}')
>>> print(f'First recommendation rule: {recommendations[0]["matched_rule"]}')
# Expected: One of: category_match, expiration_warning, frequent_category, waste_reduction, storage_tips
```

### **Verify PART 7: Upload Infrastructure**

```bash
# Check Upload model has all required fields
python manage.py shell -c "from uploads.models import Upload; print([f.name for f in Upload._meta.get_fields()])"

# Expected fields: id, user, file_name, file, file_type, mime_type, file_size,
# associated_inventory, associated_log, upload_date, notes, processed

# Test file validation
python manage.py shell
>>> from uploads.models import validate_file_size
>>> from django.core.exceptions import ValidationError
>>> class MockFile:
...     size = 6 * 1024 * 1024  # 6MB (exceeds 5MB limit)
>>> try:
...     validate_file_size(MockFile())
... except ValidationError as e:
...     print("Validation works:", e)
# Expected: ValidationError about file size

# Verify upload views exist
python manage.py shell -c "from uploads import views; print([name for name in dir(views) if not name.startswith('_')])"
# Expected: upload_form, upload_list, upload_detail, upload_delete, link_to_inventory, upload_associate_api
```

### **API Endpoints Testing**

```bash
# Start server
python manage.py runserver

# In another terminal, test APIs (requires logged-in user)
curl http://127.0.0.1:8000/food/api/dashboard/summary/
curl http://127.0.0.1:8000/food/api/recommendations/

# Expected: JSON responses with dashboard data and recommendations
```

### **Database Migrations Check**

```bash
# Verify all migrations applied
python manage.py showmigrations

# Expected output should show [X] for all migrations:
# food
#  [X] 0001_initial
# resources
#  [X] 0001_initial
# uploads
#  [X] 0001_initial
# users
#  [X] 0001_initial
#  [X] 0002_user_budget_limit

# Check for pending migrations
python manage.py makemigrations --dry-run
# Expected: No changes detected
```

---

## 📚 Additional Resources

- **Django Documentation:** https://docs.djangoproject.com/
- **Tailwind CSS Docs:** https://tailwindcss.com/docs
- **GSAP Learning:** https://gsap.com/docs/
- **Python Best Practices:** https://docs.python-guide.org/
- **Pillow (Image Processing):** https://pillow.readthedocs.io/
- **Django Model Fields:** https://docs.djangoproject.com/en/5.2/ref/models/fields/

---

## 🎯 Quick Start Checklist

- [ ] Clone repository
- [ ] Create virtual environment and activate
- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Run migrations (`python manage.py migrate`)
- [ ] Create superuser (`python manage.py createsuperuser`)
- [ ] **Seed food items** (`python manage.py seed_food`)
- [ ] **Seed resources** (`python manage.py seed_resources`)
- [ ] Verify seeding (check counts = 20 each)
- [ ] Create media directory (`mkdir media/uploads`)
- [ ] Run server (`python manage.py runserver`)
- [ ] Register user at `/users/register/`
- [ ] Test all features (inventory, logs, resources, uploads, dashboard)

---

**Built with 💚 for a sustainable future**  
_Reducing food waste, one meal at a time._

**Project Status:** ✅ Part 1 Complete - All 8 Parts Implemented  
**Last Updated:** November 21, 2025  
**Next Phase:** Part 2 - AI Integration (Onsite Hackathon)
