from django.contrib import admin
from .models import ActivityLog

@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('log_timestamp', 'user_display', 'action_display', 'target_object_display', 'details_short', 'ip_address')
    list_filter = ('action', 'log_timestamp', 'user', 'content_type') # Lọc theo hành động, thời gian, người dùng, loại đối tượng
    search_fields = (
        'user__email', # Tìm theo email người dùng
        'user__username', # Tìm theo username người dùng (nếu bạn vẫn dùng)
        'user__full_name', # Tìm theo tên đầy đủ người dùng
        'details',
        'ip_address',
        # Bạn không thể tìm kiếm trực tiếp trên trường GenericForeignKey 'target_object'
        # nhưng có thể tìm qua object_id nếu biết content_type
    )
    date_hierarchy = 'log_timestamp' # Điều hướng theo ngày tháng
    ordering = ('-log_timestamp',)

    # Các trường chỉ đọc, vì log thường không nên được sửa đổi
    readonly_fields = ('user', 'action', 'content_type', 'object_id', 'target_object_display', 'details', 'log_timestamp', 'ip_address', 'user_agent')

    fieldsets = (
        ('Thông tin Log', {
            'fields': ('log_timestamp', 'user_display', 'action_display', 'target_object_display')
        }),
        ('Chi tiết', {
            'fields': ('details', 'ip_address', 'user_agent')
        }),
        # ('Thông tin Đối tượng GFK (Chỉ xem)', { # Không cần thiết nếu đã có target_object_display
        #     'fields': ('content_type', 'object_id'),
        #     'classes': ('collapse',),
        # }),
    )

    def user_display(self, obj):
        return str(obj.user) if obj.user else "Hệ thống"
    user_display.short_description = "Người dùng"
    user_display.admin_order_field = 'user'

    def action_display(self, obj):
        return obj.get_action_display() # Sử dụng get_FOO_display() cho trường choices
    action_display.short_description = "Hành động"
    action_display.admin_order_field = 'action'

    def target_object_display(self, obj):
        return str(obj.target_object) if obj.target_object else "Không có đối tượng cụ thể"
    target_object_display.short_description = "Đối tượng tác động"

    def details_short(self, obj):
        if obj.details:
            return (obj.details[:75] + '...') if len(obj.details) > 75 else obj.details
        return ""
    details_short.short_description = "Chi tiết (tóm tắt)"

    # Vô hiệu hóa nút "Add" vì log thường được tạo tự động bởi hệ thống
    def has_add_permission(self, request):
        return False

    # (Tùy chọn) Vô hiệu hóa nút "Delete" cho tất cả hoặc một số log nhất định
    # def has_delete_permission(self, request, obj=None):
    #     return False # Không cho phép xóa bất kỳ log nào

    # (Tùy chọn) Vô hiệu hóa nút "Change" (sửa)
    # def has_change_permission(self, request, obj=None):
    #     return False # Không cho phép sửa log
