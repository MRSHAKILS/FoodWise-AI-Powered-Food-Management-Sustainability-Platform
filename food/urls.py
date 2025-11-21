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
    path('analysis/', views.consumption_analysis_dashboard, name='consumption_analysis'),
    
    # Food Items Database (PART 4)
    path('food-items/', views.food_items_list, name='food_items_list'),
    path('food-items/<int:id>/', views.food_item_detail, name='food_item_detail'),
    path('food-database/', views.food_database_list, name='food_database_list'),
    path('food-database/<int:pk>/', views.food_database_detail, name='food_database_detail'),
    path('food-database/search/', views.food_database_search, name='food_database_search'),
    
    # AI Consumption Pattern Analyzer API (Advanced)
    path('api/consumption-insights/', views.consumption_insights, name='consumption_insights'),
    
    # Dashboard & Recommendations API (PART 6)
    path('api/dashboard/summary/', views.dashboard_summary_api, name='dashboard_summary_api'),
    path('api/recommendations/', views.recommendations_api, name='recommendations_api'),
    path('dashboard/', views.enhanced_dashboard, name='enhanced_dashboard'),
]
