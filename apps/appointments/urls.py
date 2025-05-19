            # apps/appointments/urls.py
from django.urls import path
from . import views # Chúng ta sẽ tạo views ở bước tiếp theo

app_name = 'appointments' # Đặt tên cho namespace của app này

urlpatterns = [
                # URL để hiển thị danh sách tất cả lịch hẹn
                path('', views.appointment_list, name='appointment_list'),
                # URL để thêm lịch hẹn mới
                path('add/', views.appointment_create, name='appointment_create'),
                path('<int:pk>/edit/', views.appointment_update, name='appointment_update'),
                path('<int:pk>/delete/', views.appointment_delete, name='appointment_delete'),
                # Các URL khác (sửa, xóa) sẽ được thêm sau
            ]
            