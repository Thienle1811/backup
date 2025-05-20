from django.contrib import admin
from .models import MedicalRecord, MedicalRecordVersion
from django.utils.translation import gettext_lazy as _ # Thêm gettext_lazy

# Hàm để hiển thị mã bệnh nhân trong list_display
def patient_ma_benh_nhan(obj):
    if obj.patient:
        return obj.patient.ma_benh_nhan
    return None
patient_ma_benh_nhan.short_description = _('Mã Bệnh nhân') # Tên cột

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = (patient_ma_benh_nhan, 'patient', 'record_date', 'latest_version', 'created_by', 'created_at')
    search_fields = ('patient__full_name', 'patient__ma_benh_nhan', 'patient__email', 'diagnosis') # Thêm patient__ma_benh_nhan
    list_filter = ('record_date', 'created_by')
    date_hierarchy = 'record_date'
    ordering = ('-record_date',)
    raw_id_fields = ('patient', 'created_by', 'updated_by', 'latest_version')

    fieldsets = (
        (None, {
            'fields': ('patient', 'record_date', 'latest_version')
        }),
        (_('Nội dung hồ sơ (hiện hành)'), {
            'fields': ('diagnosis', 'notes')
        }),
        (_('Thông tin Bệnh nhân (Chỉ đọc)'), { # Thêm section để hiển thị mã BN
            'fields': ('get_patient_ma_benh_nhan_display', 'get_patient_full_name_display'),
            'classes': ('collapse',), # Có thể ẩn đi mặc định
        }),
        (_('Thông tin theo dõi'), {
            'fields': ('created_by', 'updated_by'),
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'get_patient_ma_benh_nhan_display', 'get_patient_full_name_display')

    def get_patient_ma_benh_nhan_display(self, obj):
        if obj.patient:
            return obj.patient.ma_benh_nhan
        return _("Chưa có")
    get_patient_ma_benh_nhan_display.short_description = _('Mã Bệnh nhân')

    def get_patient_full_name_display(self, obj):
        if obj.patient:
            return obj.patient.full_name
        return _("Chưa có")
    get_patient_full_name_display.short_description = _('Tên Bệnh nhân')


    def save_model(self, request, obj, form, change):
        if not obj.pk: # Nếu là tạo mới
            obj.created_by = request.user
        obj.updated_by = request.user # Luôn cập nhật updated_by
        super().save_model(request, obj, form, change)

@admin.register(MedicalRecordVersion)
class MedicalRecordVersionAdmin(admin.ModelAdmin):
    list_display = ('medical_record_patient_info', 'version_number', 'changed_by', 'changed_at', 'is_post_print')
    search_fields = ('medical_record__patient__full_name', 'medical_record__patient__ma_benh_nhan', 'diagnosis', 'notes', 'change_reason') # Thêm tìm theo mã BN
    list_filter = ('is_post_print', 'changed_at', 'changed_by')
    date_hierarchy = 'changed_at'
    ordering = ('-changed_at',)
    raw_id_fields = ('medical_record', 'changed_by')

    fieldsets = (
        (None, {
            'fields': ('medical_record',)
        }),
        (_('Thông tin Bệnh nhân (Từ Hồ sơ gốc)'), {
            'fields': ('get_patient_ma_benh_nhan_from_record', 'get_patient_full_name_from_record'),
        }),
        (_('Nội dung phiên bản'), {
            'fields': ('version_number', 'diagnosis', 'notes')
        }),
        (_('Thông tin thay đổi'), {
            'fields': ('is_post_print', 'changed_by', 'change_reason')
        }),
    )
    readonly_fields = ('changed_at', 'get_patient_ma_benh_nhan_from_record', 'get_patient_full_name_from_record')

    def medical_record_patient_info(self, obj):
        if obj.medical_record and obj.medical_record.patient:
            return f"{obj.medical_record.patient.full_name} (Mã: {obj.medical_record.patient.ma_benh_nhan})"
        return _("Không rõ")
    medical_record_patient_info.short_description = _('Hồ sơ Bệnh án (Bệnh nhân)')
    
    def get_patient_ma_benh_nhan_from_record(self, obj):
        if obj.medical_record and obj.medical_record.patient:
            return obj.medical_record.patient.ma_benh_nhan
        return _("Chưa có")
    get_patient_ma_benh_nhan_from_record.short_description = _('Mã Bệnh nhân')

    def get_patient_full_name_from_record(self, obj):
        if obj.medical_record and obj.medical_record.patient:
            return obj.medical_record.patient.full_name
        return _("Chưa có")
    get_patient_full_name_from_record.short_description = _('Tên Bệnh nhân')
