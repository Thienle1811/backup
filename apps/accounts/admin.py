from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    # Các trường sẽ hiển thị trong danh sách người dùng
    list_display = ('email', 'username', 'full_name', 'is_staff', 'is_active', 'date_joined')
    # Các trường có thể tìm kiếm
    search_fields = ('email', 'username', 'full_name')
    # Các trường có thể lọc
    list_filter = ('is_staff', 'is_active', 'groups')
    # Sắp xếp mặc định
    ordering = ('email',)

    # Nếu bạn muốn tùy chỉnh form thêm/sửa người dùng trong admin,
    # bạn có thể định nghĩa fieldsets hoặc fields ở đây.
    # Ví dụ, để hiển thị các trường tùy chỉnh của bạn:
    fieldsets = UserAdmin.fieldsets + (
        ('Thông tin bổ sung', {'fields': ('phone', 'date_of_birth', 'full_name')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Thông tin bổ sung', {'fields': ('phone', 'date_of_birth', 'full_name')}),
    )

# Đăng ký CustomUser model với CustomUserAdmin tùy chỉnh
admin.site.register(CustomUser, CustomUserAdmin)
