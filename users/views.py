import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.conf import settings
from django.urls import reverse
from .models import User
from .forms import RegisterForm
from django.http import JsonResponse
from google.oauth2 import id_token
from google.auth.transport import requests

# --------------------------
# PUBLIC VIEWS
# --------------------------

def landing_view(request):
    """Public landing page"""
    return render(request, "home.html")


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    username_value = ""
    password_value = ""

    if request.method == "POST":
        username_value = request.POST.get("username", "")
        password_value = request.POST.get("password", "")

        user = authenticate(request, username=username_value, password=password_value)

        if user is not None:
            login(request, user)
            return redirect("dashboard")
        else:
            return render(request, "users/login.html", {
                "error": "Incorrect username or password.",
                "username_value": "",   # CLEAR ON ERROR
                "password_value": "",   # CLEAR ON ERROR
            })

    return render(request, "users/login.html", {
        "username_value": "",
        "password_value": "",
    })

def register_view(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        household_size = request.POST.get("household_size")
        location = request.POST.get("location")

        dietary_list = request.POST.getlist("dietary_preferences")  
        dietary_preferences = ",".join(dietary_list)

        if password != confirm_password:
            return render(request, "users/register.html", {"error": "Passwords do not match!"})

        # ✔ FIX: prevent duplicate email/username
        if User.objects.filter(email=email).exists():
            return render(request, "users/register.html", {
                "error": "An account already exists with this email."
            })

        user = User.objects.create(
            username=email,
            email=email,
            full_name=full_name,
            household_size=household_size,
            dietary_preferences=dietary_preferences,
            location=location,
            password=make_password(password),
        )

        # Specify backend manually when logging in manually
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)

        return redirect("dashboard")

    return render(request, "users/register.html")

def logout_view(request):
    """Logs the user out"""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("landing")


# --------------------------
# PROTECTED VIEWS
# --------------------------

@login_required(login_url="users:login")
def dashboard_view(request):
    """Dashboard shown ONLY to logged-in users (allauth and normal)"""
    return render(request, "dashboard.html")


@login_required(login_url="users:login")
def profile_view(request):
    """Show logged-in user's profile with inventory and consumption logs"""
    from food.models import FoodItem, ConsumptionLog
    from .forms import ProfileEditForm, FoodItemForm, ConsumptionLogForm
    
    # Handle profile edit form submission
    if request.method == 'POST':
        profile_form = ProfileEditForm(request.POST, instance=request.user)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        profile_form = ProfileEditForm(instance=request.user)
    
    # Get user's data
    food_items = FoodItem.objects.filter(user=request.user).order_by('-created_at')[:10]
    consumption_logs = ConsumptionLog.objects.filter(user=request.user).order_by('-consumption_date', '-created_at')[:10]
    
    # Initialize other forms
    food_form = FoodItemForm()
    log_form = ConsumptionLogForm()
    
    context = {
        'profile_form': profile_form,
        'food_form': food_form,
        'log_form': log_form,
        'food_items': food_items,
        'consumption_logs': consumption_logs,
    }
    
    return render(request, "users/profile.html", context)


@login_required(login_url="users:login")
def profile_edit_view(request):
    """Profile editing page with form handling"""
    from .forms import ProfileEditForm
    
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, "users/profile_edit.html", {'form': form})

def test_login_view(request):
    """Test login without authentication - for development only"""
    if request.method == 'POST':
        # Create a test session to simulate login
        request.session['test_user_logged_in'] = True
        request.session['test_username'] = 'TestUser'
        return redirect('dashboard')
    return redirect('users:login')

def google_auth_view(request):
    if request.method == "POST":
        data = json.loads(request.body)
        token = data.get("credential")

        try:
            google_user = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            email = google_user["email"]
            name = google_user.get("name", "")

            user, created = User.objects.get_or_create(
                email=email,
                defaults={"username": email, "full_name": name}
            )

            user.backend = "django.contrib.auth.backends.ModelBackend"
            login(request, user)

            return JsonResponse({"status": "ok"})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "invalid"})