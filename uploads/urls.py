from django.urls import path
from . import views

app_name = 'uploads'

urlpatterns = [
    # Image Upload Infrastructure (Phase 6 requirement)
    path('', views.upload_form, name='upload_form'),
    path('list/', views.upload_list, name='upload_list'),
    path('<int:pk>/', views.upload_detail, name='upload_detail'),
    path('<int:pk>/delete/', views.upload_delete, name='upload_delete'),
    path('<int:pk>/link/', views.link_to_inventory, name='link_to_inventory'),
]
