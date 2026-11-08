from django.urls import path
from . import views

app_name = 'uploads'

urlpatterns = [
    # Image Upload Infrastructure (PART 7)
    path('', views.upload_form, name='upload_form'),
    path('list/', views.upload_list, name='upload_list'),
    path('<int:pk>/', views.upload_detail, name='upload_detail'),
    path('<int:pk>/file/', views.upload_file, name='upload_file'),
    path('<int:pk>/delete/', views.upload_delete, name='upload_delete'),
    path('<int:pk>/link/', views.link_to_inventory, name='link_to_inventory'),
    path('<int:pk>/process-ocr/', views.process_ocr_view, name='process_ocr'),
    
    # API endpoint for associations
    path('api/<int:pk>/associate/', views.upload_associate_api, name='upload_associate_api'),
]
