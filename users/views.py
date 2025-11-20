from django.shortcuts import render


def dashboard_view(request):
    return render(request, 'dashboard.html')


def profile_view(request):
    return render(request, 'users/profile.html')


def login_view(request):
    return render(request, 'users/login.html')


def register_view(request):
    return render(request, 'users/register.html')
