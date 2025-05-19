from django.contrib import admin
from .models import MedicalRecord, MedicalRecordVersion # Thêm MedicalRecordVersion vào import

# Đăng ký cho MedicalRecord (đã có từ trước)
@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'record_date', 'latest_version', 'created_by', 'created_at') # Thêm latest_version vào list_display
    search_fields = ('patient__full_name', 'patient__email', 'diagnosis')
    list_filter = ('record_date', 'created_by')
    date_hierarchy = 'record_date'
    ordering = ('-record_date',)
    raw_id_fields = ('patient', 'created_by', 'updated_by', 'latest_version') # Thêm latest_version vào raw_id_fields

    fieldsets = (
        (None, {
            'fields': ('patient', 'record_date', 'latest_version') # Thêm latest_version vào fieldsets
        }),
        ('Nội dung hồ sơ (hiện hành)', { # Đổi tiêu đề cho rõ ràng hơn
            'fields': ('diagnosis', 'notes')
        }),
        ('Thông tin theo dõi', {
            'fields': ('created_by', 'updated_by'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        obj.updated_by = request.user
        super().save_model(request, obj, form, change)

# Đăng ký cho MedicalRecordVersion (thêm mới phần này)
@admin.register(MedicalRecordVersion)
class MedicalRecordVersionAdmin(admin.ModelAdmin):
    list_display = ('medical_record', 'version_number', 'changed_by', 'changed_at', 'is_post_print')
    search_fields = ('medical_record__patient__full_name', 'diagnosis', 'notes', 'change_reason')
    list_filter = ('is_post_print', 'changed_at', 'changed_by')
    date_hierarchy = 'changed_at'
    ordering = ('-changed_at',)
    raw_id_fields = ('medical_record', 'changed_by') # Giúp chọn medical_record và changed_by dễ hơn

    fieldsets = (
        (None, {
            'fields': ('medical_record', 'version_number')
        }),
        ('Nội dung phiên bản', {
            'fields': ('diagnosis', 'notes')
        }),
        ('Thông tin thay đổi', {
            'fields': ('is_post_print', 'changed_by', 'change_reason')
        }),
    )
    readonly_fields = ('changed_at',) # changed_at được tự động điền

# Hoặc bạn có thể đăng ký đơn giản nếu không cần tùy chỉnh nhiều:
# admin.site.register(MedicalRecordVersion)
