from django.urls import path
from . import views

app_name = 'food'

urlpatterns = [
    # Inventory Management
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_form, name='inventory_form'),
    path('inventory/<int:pk>/edit/', views.inventory_edit, name='inventory_edit'),
    path('inventory/<int:pk>/delete/', views.inventory_delete, name='inventory_delete'),
    
    # Consumption Logs (Phase 4 requirement)
    path('logs/', views.consumption_logs_list, name='logs_list'),
    path('logs/add/', views.consumption_log_form, name='log_form'),
    path('logs/<int:pk>/delete/', views.consumption_log_delete, name='log_delete'),
    
    # History & Analytics (Phase 4 requirement)
    path('history/', views.consumption_history, name='history'),
]
