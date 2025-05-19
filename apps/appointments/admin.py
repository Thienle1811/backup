from django.contrib import admin
from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient_name', 'staff_name', 'appointment_date', 'appointment_time', 'status', 'created_at')
    search_fields = ('patient__full_name', 'staff__full_name', 'staff__email', 'notes')
    list_filter = ('status', 'appointment_date', 'staff')
    date_hierarchy = 'appointment_date' # Thêm điều hướng theo ngày tháng dựa trên ngày hẹn
    ordering = ('-appointment_date', '-appointment_time')
    raw_id_fields = ('patient', 'staff', 'created_by') # Giúp chọn patient và staff dễ hơn

    fieldsets = (
        (None, {
            'fields': ('patient', 'staff', 'appointment_date', 'appointment_time', 'status')
        }),
        ('Ghi chú', {
            'fields': ('notes',),
            'classes': ('collapse',), # Có thể ẩn nhóm này mặc định
        }),
        ('Thông tin theo dõi', {
            'fields': ('created_by',), # created_at, updated_at thường là readonly
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    # Phương thức để hiển thị tên bệnh nhân
    def patient_name(self, obj):
        if obj.patient:
            return obj.patient.full_name
        return "N/A"
    patient_name.short_description = 'Bệnh nhân' # Tên cột trong admin
    patient_name.admin_order_field = 'patient__full_name' # Cho phép sắp xếp

    # Phương thức để hiển thị tên nhân viên
    def staff_name(self, obj):
        if obj.staff:
            # Giả sử CustomUser có trường full_name hoặc phương thức get_full_name()
            return obj.staff.full_name if hasattr(obj.staff, 'full_name') and obj.staff.full_name else obj.staff.email
        return "N/A"
    staff_name.short_description = 'Nhân viên' # Tên cột trong admin
    staff_name.admin_order_field = 'staff__full_name' # Hoặc staff__email nếu sắp xếp theo email

    # Ghi đè phương thức save_model để tự động gán created_by nếu cần
    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.created_by : # Khi tạo mới và chưa có người tạo
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# Hoặc bạn có thể đăng ký đơn giản nếu không cần tùy chỉnh nhiều:
# admin.site.register(Appointment)
