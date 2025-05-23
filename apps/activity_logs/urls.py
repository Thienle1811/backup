# apps/activity_logs/urls.py
from django.urls import path
from . import views

app_name = 'activity_logs'

urlpatterns = [
    path('', views.full_activity_log_list_view, name='full_log_list'),
]