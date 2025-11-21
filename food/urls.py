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
    
    # Waste Analytics (AI Waste Estimation Model)
    path('waste-analytics/', views.waste_analytics, name='waste_analytics'),
    path('waste-analytics/export/<str:format>/', views.export_waste_analytics, name='export_waste_analytics'),
    
    # Priority Consumption (AI Expiration Risk Prediction)
    path('priority-consumption/', views.priority_consumption, name='priority_consumption'),
    path('inventory/<int:pk>/mark-consumed/', views.mark_consumed, name='mark_consumed'),
    
    # API Endpoints
    path('api/priority-alerts/', views.priority_alerts_api, name='priority_alerts_api'),
    
    # Food Items Database (PART 4)
    path('food-items/', views.food_items_list, name='food_items_list'),
    path('food-items/<int:id>/', views.food_item_detail, name='food_item_detail'),
    path('food-database/', views.food_database_list, name='food_database_list'),
    path('food-database/<int:pk>/', views.food_database_detail, name='food_database_detail'),
    path('food-database/search/', views.food_database_search, name='food_database_search'),
    
    # Dashboard & Recommendations API (PART 6)
    path('api/dashboard/summary/', views.dashboard_summary_api, name='dashboard_summary_api'),
    path('api/recommendations/', views.recommendations_api, name='recommendations_api'),
    path('dashboard/', views.enhanced_dashboard, name='enhanced_dashboard'),
    
    # Meal Planning & Optimization (AI Meal Optimization Engine)
    path('meal-plans/', views.meal_plan_list, name='meal_plan_list'),
    path('meal-plans/create/', views.meal_plan_create, name='meal_plan_create'),
    path('meal-plans/<int:pk>/', views.meal_plan_detail, name='meal_plan_detail'),
    path('meal-plans/<int:pk>/delete/', views.meal_plan_delete, name='meal_plan_delete'),
    
    # Recipe Browser
    path('recipes/', views.recipe_list, name='recipe_list'),
    path('recipes/<int:pk>/', views.recipe_detail, name='recipe_detail'),
    
    # SDG Impact Scoring
    path('sdg-impact/', views.sdg_impact_dashboard, name='sdg_impact_dashboard'),
    path('api/sdg-score/', views.sdg_score_api, name='sdg_score_api'),
]
