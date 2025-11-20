from django.urls import path
from . import views

app_name = 'food'

urlpatterns = [
    path('inventory/', views.inventory_list, name='inventory_list'),
    path('inventory/add/', views.inventory_form, name='inventory_form'),
]
