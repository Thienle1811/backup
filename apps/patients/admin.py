from django.contrib import admin
from .models import Patient

@admin.register(Patient) # Sử dụng decorator @admin.register để đăng ký
class PatientAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'date_of_birth', 'gender', 'created_at', 'created_by')
    search_fields = ('full_name', 'email', 'phone')
    list_filter = ('gender', 'blood_type', 'created_at')
    ordering = ('-created_at', 'full_name') # Sắp xếp theo ngày tạo giảm dần, sau đó theo tên
    date_hierarchy = 'created_at' # Thêm điều hướng theo ngày tháng dựa trên trường created_at

    # Nếu bạn muốn tùy chỉnh form thêm/sửa bệnh nhân:
    # fieldsets = (
    #     ('Thông tin cá nhân', {
    #         'fields': ('full_name', 'date_of_birth', 'gender', 'address', 'phone', 'email')
    #     }),
    #     ('Thông tin y tế', {
    #         'fields': ('blood_type', 'allergies')
    #     }),
    #     ('Thông tin theo dõi', {
    #         'fields': ('created_by', 'updated_by') # created_at, updated_at thường là read-only
    #     }),
    # )
    # readonly_fields = ('created_at', 'updated_at') # Các trường chỉ đọc

# Hoặc bạn có thể đăng ký đơn giản nếu không cần tùy chỉnh nhiều:
# admin.site.register(Patient)
