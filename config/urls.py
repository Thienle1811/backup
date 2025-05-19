"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# config/urls.py
from django.contrib import admin
from django.urls import path, include # Đảm bảo 'include' đã được import
from apps.dashboard import views as dashboard_views

urlpatterns = [
    path('admin/', admin.site.urls),

    # Đặt URL cho dashboard ở đây nếu muốn nó là trang chủ (ví dụ: /)
    path('', dashboard_views.dashboard_view, name='home_dashboard'), # Trang chủ trỏ đến dashboard
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')), # Hoặc /dashboard/ nếu muốn

    
    # Include URLs của app 'patients' (đã có từ trước)
    path('patients/', include('apps.patients.urls', namespace='patients')),
    
    # Include URLs của app 'medical_records' (DÒNG CẦN KIỂM TRA)
    # Tất cả các URL trong apps/medical_records/urls.py sẽ có tiền tố là 'medical-records/'
    # Ví dụ: /medical-records/ sẽ trỏ đến medical_record_list
    #        /medical-records/add/ sẽ trỏ đến medical_record_create
    path('medical-records/', include('apps.medical_records.urls', namespace='medical_records')),
    path('appointments/', include('apps.appointments.urls', namespace='appointments')),
    path('lab-tests/', include('apps.labtests.urls', namespace='labtests')),
    path('management/accounts/', include('apps.accounts.urls', namespace='accounts_admin')), 
     path('accounts/', include('django.contrib.auth.urls')),

    # Bạn có thể thêm các include cho các app khác ở đây sau này, ví dụ:
    # path('lab-tests/', include('apps.labtests.urls', namespace='labtests')),
    # path('appointments/', include('apps.appointments.urls', namespace='appointments')),
    # path('attachments/', include('apps.attachments.urls', namespace='attachments')),
    # path('activity-logs/', include('apps.activity_logs.urls', namespace='activity_logs')),
    # path('accounts/', include('apps.accounts.urls', namespace='accounts')), # Nếu bạn có URL riêng cho accounts
]

