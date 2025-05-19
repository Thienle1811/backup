        # apps/accounts/urls.py
from django.urls import path
from . import views

app_name = 'accounts_admin' # Đảm bảo app_name là 'accounts_admin' nếu bạn dùng namespace này

urlpatterns = [
            path('users/', views.user_list_admin_view, name='user_list_admin'),
            path('users/add/', views.user_create_admin_view, name='user_create_admin'),
            path('users/<int:pk>/edit/', views.user_update_admin_view, name='user_update_admin'),
            path('users/<int:pk>/delete/', views.user_delete_admin_view, name='user_delete_admin'), # MỚI
        ]
        