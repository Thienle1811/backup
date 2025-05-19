        # apps/labtests/urls.py
from django.urls import path
from . import views

app_name = 'labtests'

urlpatterns = [
            # URLs cho LabTestTemplate
            path('templates/', views.lab_test_template_list, name='lab_test_template_list'),
            path('templates/add/', views.lab_test_template_create, name='lab_test_template_create'),
            path('templates/<int:pk>/edit/', views.lab_test_template_update, name='lab_test_template_update'),
            path('templates/<int:pk>/delete/', views.lab_test_template_delete, name='lab_test_template_delete'),

            # URLs cho LabTest
            path('create/', views.lab_test_create_and_enter_results, name='lab_test_create_and_enter_results'),
            path('ajax/get-template-fields/<int:template_id>/', views.ajax_get_template_fields, name='ajax_get_template_fields'),
            path('', views.lab_test_list, name='lab_test_list'), 
            
            # URL để xem/sửa một phiếu xét nghiệm đã có (MỚI)
            path('<int:pk>/edit-results/', views.lab_test_update_results, name='lab_test_update_results'),
            
            # URL để xóa một phiếu xét nghiệm (sẽ tạo view sau)
            # path('<int:pk>/delete/', views.lab_test_delete, name='lab_test_delete'),
            path('<int:pk>/delete/', views.lab_test_delete, name='lab_test_delete'),
        ]
        