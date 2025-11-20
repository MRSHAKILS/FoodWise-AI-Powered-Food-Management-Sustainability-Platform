from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    # Resources Listing & Filtering
    path('', views.resources_list, name='resources_list'),
    path('category/<str:category>/', views.resources_by_category, name='resources_by_category'),
    path('<int:pk>/', views.resource_detail, name='resource_detail'),
    
    # Recommendations (Phase 5 requirement)
    path('recommendations/', views.recommended_resources, name='recommendations'),
]
