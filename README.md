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

### 🎯 Key Features (Part 1)
- ✅ **Smart Inventory Management** - Track food items with categories, quantities, and expiry dates
- ✅ **User Authentication** - Secure registration and login with household profiles
- ✅ **Consumption Logging** - Record daily food usage for waste analysis
- ✅ **Rule-Based Recommendations** - Get personalized tips based on inventory and dietary preferences
- ✅ **Image Upload Infrastructure** - Upload receipts and food labels (OCR in Part 2)
- ✅ **Interactive Dashboard** - Real-time overview of inventory, expiring items, and statistics
- ✅ **Educational Resources** - Access storage tips, recipes, nutrition guides, and sustainability practices

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
├── 📁 food/                        # Inventory & Consumption Logging
│   ├── models.py                   # FoodItem, ConsumptionLog models
│   ├── views.py                    # CRUD operations for inventory
│   ├── urls.py                     # Inventory routes
│   └── templates/food/             # Inventory list, forms, logs
│
├── 📁 resources/                   # Educational Resources
│   ├── models.py                   # Resource model (title, category, content)
│   ├── views.py                    # Resource list, recommendations
│   ├── urls.py                     # Resource routes
│   └── templates/resources/        # Resource pages
│
├── 📁 uploads/                     # Image Upload Infrastructure
│   ├── models.py                   # Upload model (image, linked_item)
│   ├── views.py                    # File handling
│   ├── urls.py                     # Upload routes
│   └── templates/uploads/          # Upload forms
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
Django==5.2.6
Pillow==10.4.0              # Image handling
python-decouple==3.8        # Environment variables
djangorestframework==3.15.2  # API (optional)
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

### **Step 7: Seed Database (MANDATORY)**

⚠️ **Critical Step:** The platform requires initial data to function properly.

**Seed Food Items (15-20 items):**
```bash
python manage.py seed_food
```

**Seed Educational Resources (15-20 resources):**
```bash
python manage.py seed_resources
```

**What gets seeded:**
- **Food Items:** Vegetables, Fruits, Dairy, Protein, Grains, Snacks (with realistic expiry dates and costs)
- **Resources:** 
  - Recipes (Zero-Waste, Quick Meals)
  - Nutrition Tips (Balanced Diet, Portion Control)
  - Storage Tips (Proper Storage Methods)
  - Sustainability Practices (Reduce Waste, Composting)

**Verify Seeding:**
```bash
# Access Django Admin Panel
python manage.py runserver
# Visit: http://127.0.0.1:8000/admin/
# Login with superuser credentials
# Check: Food > Food Items & Resources > Resources
```

---

### **Step 8: Run Development Server**

```bash
python manage.py runserver
```

**Access the Platform:**
- **Home:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **Inventory:** http://127.0.0.1:8000/food/inventory/
- **Resources:** http://127.0.0.1:8000/resources/

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

### **5. Explore Resources**
- Visit `/resources/` for educational content
- Filter by: Recipes, Nutrition Tips, Storage Tips, Sustainability
- Get personalized recommendations based on your inventory

### **6. Upload Images**
- Go to `/uploads/` to upload receipts or food labels
- Manually link uploads to inventory items
- (OCR/AI extraction coming in Part 2)

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

**FoodItem Table:**
```python
- item_name: CharField
- category: CharField (Vegetables, Fruits, Dairy, Protein, Grains, Snacks)
- quantity: DecimalField
- unit: CharField (kg, g, L, mL, pieces, packets, bottles, cans)
- expiry_date: DateField
- cost_per_unit: DecimalField (optional)
- user_id: ForeignKey (User)
- image_url: URLField (optional)
- added_on: DateTimeField (auto)
```

**ConsumptionLog Table:**
```python
- user: ForeignKey (User)
- item_name: CharField
- quantity: DecimalField
- category: CharField
- date_logged: DateField (auto)
```

**Resource Table:**
```python
- title: CharField
- category: CharField (Recipes, Nutrition, Storage, Sustainability)
- content: TextField
- external_link: URLField (optional)
- created_at: DateTimeField (auto)
```

**Upload Table:**
```python
- user: ForeignKey (User)
- image: ImageField
- uploaded_at: DateTimeField (auto)
- linked_inventory_item: ForeignKey (FoodItem, optional)
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

## 📊 API Endpoints (Future Implementation)

### **Authentication**
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login user
- `POST /api/auth/logout/` - Logout user

### **Inventory**
- `GET /api/inventory/` - List all items
- `POST /api/inventory/` - Add new item
- `PUT /api/inventory/<id>/` - Update item
- `DELETE /api/inventory/<id>/` - Delete item

### **Consumption**
- `GET /api/logs/` - List consumption logs
- `POST /api/logs/` - Add new log
- `GET /api/history/` - Get consumption history

### **Resources**
- `GET /api/resources/` - List all resources
- `GET /api/resources/<id>/` - Get resource details
- `GET /api/recommendations/` - Get personalized recommendations

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
gsap.from('.element', {
    opacity: 0,
    y: 30,
    duration: 0.6, // Change speed
    ease: 'power3.out'
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
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" />
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

### **Upcoming Features:**
- [ ] **AI-Powered OCR** - Extract data from receipt images
- [ ] **Smart Expiry Alerts** - Email/SMS notifications
- [ ] **Recipe Suggestions** - AI-generated recipes based on inventory
- [ ] **Waste Analytics** - ML-powered insights and predictions
- [ ] **Mobile App** - React Native companion app
- [ ] **Social Features** - Share recipes and tips with community
- [ ] **Donation Integration** - Connect with food banks for surplus items
- [ ] **Blockchain Tracking** - Transparent food supply chain

---

## 📈 Project Status

**Part 1 Progress: 95% Complete**

✅ Phase 1: Setup & Database Models (100%)  
✅ Phase 2: Authentication & User Management (100%)  
✅ Phase 3: Database Seeding (100%)  
✅ Phase 4: Core Features - Inventory & Logging (100%)  
✅ Phase 5: Rule-Based Recommendations (90%)  
✅ Phase 6: Image Upload Infrastructure (100%)  
✅ Phase 7: Frontend Dashboard & UI (100%)  
✅ Phase 8: Documentation (95%)

**Ready for Part 2 Onsite Hackathon!** 🚀

---

## 📚 Additional Resources

- **Django Documentation:** https://docs.djangoproject.com/
- **Tailwind CSS Docs:** https://tailwindcss.com/docs
- **GSAP Learning:** https://gsap.com/docs/
- **Python Best Practices:** https://docs.python-guide.org/

---

**Built with 💚 for a sustainable future**  
*Reducing food waste, one meal at a time.*
