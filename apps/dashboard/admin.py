# apps/dashboard/admin.py
from django.contrib import admin
from .models import ClinicSetting # Import model ClinicSetting

@admin.register(ClinicSetting)
class ClinicSettingAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'address') # Các trường hiển thị trong danh sách
    # Không cho phép thêm mới đối tượng ClinicSetting từ admin nếu bạn muốn đảm bảo chỉ có 1 bản ghi.
    # Thay vào đó, bạn sẽ tạo bản ghi đầu tiên bằng cách khác (ví dụ: shell, hoặc code trong view)
    # và chỉ cho phép chỉnh sửa bản ghi đó.

    def has_add_permission(self, request):
        # Chỉ cho phép thêm nếu chưa có bản ghi nào, hoặc luôn không cho phép nếu muốn strict singleton
        # return not ClinicSetting.objects.exists()
        return True # Tạm thời cho phép thêm để bạn dễ tạo bản ghi đầu tiên

    def has_delete_permission(self, request, obj=None):
        # Không cho phép xóa bản ghi cài đặt
        return False

# Hoặc đăng ký đơn giản nếu không cần tùy chỉnh nhiều:
# admin.site.register(ClinicSetting)