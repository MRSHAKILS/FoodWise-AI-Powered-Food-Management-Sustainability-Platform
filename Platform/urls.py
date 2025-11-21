"""
URL configuration for Platform project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from users.views import dashboard_view, landing_view

# Import analytics view
from food.admin import analytics_view_function

urlpatterns = [
    path("admin/food/analytics/", admin.site.admin_view(analytics_view_function), name='food_analytics_dashboard'),
    path("admin/", admin.site.urls),
    path("", landing_view, name='landing'),
    path("dashboard/", dashboard_view, name='dashboard'),
    path("users/", include('users.urls')),
    path("food/", include('food.urls')),
    path("resources/", include('resources.urls')),
    path("uploads/", include('uploads.urls')),
    path("accounts/", include("allauth.urls")),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
