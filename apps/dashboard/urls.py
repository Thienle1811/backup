# apps/dashboard/urls.py
from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_view, name='dashboard_home'),
    path('system-management/', views.system_management_dashboard_view, name='system_management_dashboard'), # <<< DÒNG MỚI THÊM
]