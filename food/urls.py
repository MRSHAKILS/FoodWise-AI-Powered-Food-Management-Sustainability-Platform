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
    
    # AI-Powered Features API (PART 2)
    path('api/analyze/consumption/', views.analyze_consumption_api, name='analyze_consumption_api'),
    path('api/optimize/meal-plan/', views.generate_meal_plan_api, name='generate_meal_plan_api'),
    path('api/chat/nourish-bot/', views.nourish_bot_chat_api, name='nourish_bot_chat_api'),
    path('api/estimate/waste/', views.waste_estimation_api, name='waste_estimation_api'),
    path('api/score/sdg/', views.sdg_score_api, name='sdg_score_api'),
    
    # AI-Powered Features Frontend Views
    path('ai/consumption-analysis/', views.consumption_analysis_view, name='consumption_analysis'),
    path('ai/meal-planner/', views.meal_planner_view, name='meal_planner'),
    path('ai/nourish-bot/', views.nourish_bot_view, name='nourish_bot'),
    path('ai/sdg-score/', views.sdg_score_view, name='sdg_score'),
    path('ai/waste-estimation/', views.waste_estimation_view, name='waste_estimation'),
    path('ai/expiration-risks/', views.expiration_risks_view, name='expiration_risks'),
    
    # Waste Log Management
    path('waste-logs/', views.waste_logs_list, name='waste_logs_list'),
    path('waste-logs/add/', views.waste_log_form, name='waste_log_form'),
    path('waste-logs/<int:pk>/delete/', views.waste_log_delete, name='waste_log_delete'),
]
