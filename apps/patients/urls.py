# apps/patients/urls.py
from django.urls import path
from . import views # Chúng ta sẽ tạo views.patient_list và views.patient_create

app_name = 'patients' # Đặt tên cho namespace của app này

urlpatterns = [
    # URL để hiển thị danh sách bệnh nhân
    # Khi người dùng truy cập vào đường dẫn gốc của app 'patients' (ví dụ: /patients/),
    # nó sẽ gọi view 'patient_list'.
    # Tên 'patient_list' được dùng để tham chiếu URL này từ template hoặc view khác.
    path('', views.patient_list, name='patient_list'),

    # URL để thêm bệnh nhân mới
    # Khi người dùng truy cập /patients/add/, nó sẽ gọi view 'patient_create'.
    path('add/', views.patient_create, name='patient_create'),
    path('<int:pk>/edit/', views.patient_update, name='patient_update'),
    path('<int:pk>/delete/', views.patient_delete, name='patient_delete'),

    # Chúng ta sẽ thêm các URL khác sau này, ví dụ:
    # path('<int:pk>/', views.patient_detail, name='patient_detail'), # Xem chi tiết bệnh nhân
    # path('<int:pk>/edit/', views.patient_update, name='patient_update'), # Sửa thông tin bệnh nhân
    # path('<int:pk>/delete/', views.patient_delete, name='patient_delete'), # Xóa bệnh nhân
]
