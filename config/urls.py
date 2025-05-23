# config/urls.py
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views # Import auth_views
from apps.dashboard import views as dashboard_views # Giả sử bạn có view này
from django.conf import settings # Cho static files trong development
from django.conf.urls.static import static # Cho static files trong development

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', dashboard_views.dashboard_view, name='home_dashboard'), 
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')), 
    
    path('patients/', include('apps.patients.urls', namespace='patients')),
    path('medical-records/', include('apps.medical_records.urls', namespace='medical_records')),
    path('appointments/', include('apps.appointments.urls', namespace='appointments')),
    path('lab-tests/', include('apps.labtests.urls', namespace='labtests')),
    path('dashboard/', include('apps.dashboard.urls', namespace='dashboard')),
    
    # URL cho quản lý người dùng (admin tự tạo trong app 'accounts')
    path('management/accounts/', include('apps.accounts.urls', namespace='accounts_admin')), 
    path('activity-logs/', include('apps.activity_logs.urls', namespace='activity_logs')),

    # URL cho ĐĂNG NHẬP, ĐĂNG XUẤT (sử dụng view của Django với template tùy chỉnh)
    # Chúng ta định nghĩa login và logout ở đây để có thể tùy chỉnh template_name.
    # Các URL khác của django.contrib.auth.urls (như password reset) vẫn sẽ hoạt động nếu bạn giữ lại include bên dưới
    # hoặc bạn có thể định nghĩa tất cả chúng ở đây.
    
    path('accounts/login/', 
         auth_views.LoginView.as_view(
             template_name='accounts/login.html' # Trỏ đến template login.html mới của bạn
         ), 
         name='login'),
    path('accounts/logout/', 
         auth_views.LogoutView.as_view(
             template_name='accounts/logged_out.html' # Template cho trang sau khi logout (bạn cần tạo file này)
         ), 
         name='logout'),

    # Bạn có thể giữ lại include này nếu muốn sử dụng các URL khác của django.contrib.auth
    # như password_reset, password_change mà không cần định nghĩa lại tất cả.
    # Nếu có xung đột tên URL (ví dụ login, logout đã định nghĩa ở trên),
    # các định nghĩa tường minh ở trên sẽ được ưu tiên.
    path('accounts/', include('django.contrib.auth.urls')),
]

# Cấu hình phục vụ file tĩnh và media trong môi trường development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Dòng static cho STATIC_URL thường không cần thiết nếu DEBUG=True và bạn đang dùng runserver,
    # vì Django tự động xử lý. Nhưng thêm vào cũng không sao.
    # urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
