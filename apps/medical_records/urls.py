                        # apps/medical_records/urls.py
from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
                path('', views.medical_record_list, name='medical_record_list'),
                path('add/', views.medical_record_create, name='medical_record_create'),
                # URL để sửa hồ sơ bệnh án (MỚI)
                path('<int:pk>/edit/', views.medical_record_update, name='medical_record_update'),
                path('<int:pk>/delete/', views.medical_record_delete, name='medical_record_delete'),
            ]
            
            