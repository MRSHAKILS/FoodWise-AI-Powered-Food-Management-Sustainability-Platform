from django.shortcuts import render, redirect
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required


def dashboard_view(request):
    # Non-authenticated users should NOT see dashboard
    # Redirect them to landing page
    # Only show dashboard if user is logged in or has test session
    if request.user.is_authenticated or request.session.get('test_user_logged_in'):
        return render(request, 'dashboard.html')
    else:
        # Redirect to login if they try to access dashboard directly
        return redirect('users:login')


def landing_view(request):
    # Public homepage for non-authenticated users
    return render(request, 'home.html')


@login_required(login_url='users:login')
def profile_view(request):
    return render(request, 'users/profile.html')


@login_required(login_url='users:login')
def profile_edit_view(request):
    # TODO: Implement profile editing with form validation
    return render(request, 'users/profile_edit.html')


def login_view(request):
    # If already logged in, redirect to dashboard
    if request.user.is_authenticated or request.session.get('test_user_logged_in'):
        return redirect('dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid username or password'})
    return render(request, 'users/login.html')


def test_login_view(request):
    """Test login without authentication - for development only"""
    if request.method == 'POST':
        # Create a test session to simulate login
        request.session['test_user_logged_in'] = True
        request.session['test_username'] = 'TestUser'
        return redirect('dashboard')
    return redirect('users:login')


def register_view(request):
    # TODO: Implement user registration with validation
    return render(request, 'users/register.html')


def logout_view(request):
    logout(request)
    # Clear test login session
    if 'test_user_logged_in' in request.session:
        del request.session['test_user_logged_in']
    if 'test_username' in request.session:
        del request.session['test_username']
    return redirect('landing')  # Redirect to landing page
