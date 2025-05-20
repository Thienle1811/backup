# apps/labtests/admin.py
from django.contrib import admin
from django.utils import timezone
from .models import LabTestTemplate, LabTestTemplateField, LabTest, LabTestResultValue, LabTestVersion

# LabTestTemplateFieldInline (Giữ nguyên)
class LabTestTemplateFieldInline(admin.TabularInline):
    model = LabTestTemplateField
    extra = 1
    ordering = ('field_order', 'field_name',)

# LabTestTemplateAdmin (Giữ nguyên)
@admin.register(LabTestTemplate)
class LabTestTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'created_by', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('is_active', 'created_at')
    ordering = ('name',)
    inlines = [LabTestTemplateFieldInline]
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'is_active')
        }),
        ('Thông tin theo dõi', {
            'fields': ('created_by',),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('created_at', 'updated_at')

    def save_model(self, request, obj, form, change):
        if not obj.pk:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

# LabTestResultValueInline (Giữ nguyên)
class LabTestResultValueInline(admin.TabularInline):
    model = LabTestResultValue
    extra = 0
    fields = ('template_field', 'value', 'comment', 'entered_by')
    readonly_fields = ('template_field',)
    raw_id_fields = ('entered_by',)

    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        if obj and obj.template:
            template_fields = obj.template.fields.all()
            if not obj.result_values.exists():
                 self.extra = template_fields.count()
            else:
                 self.extra = 0 # Không thêm dòng trống nếu đã có kết quả
        else:
            self.extra = 0
        return formset

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "template_field":
            lab_test_id = request.resolver_match.kwargs.get('object_id')
            if lab_test_id:
                try:
                    lab_test = LabTest.objects.get(pk=lab_test_id)
                    if lab_test.template:
                        kwargs["queryset"] = LabTestTemplateField.objects.filter(template=lab_test.template)
                except LabTest.DoesNotExist:
                    pass
            else:
                 kwargs["queryset"] = LabTestTemplateField.objects.none()
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

# LabTestAdmin (CẬP NHẬT)
@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ('custom_id_display', 'medical_record_patient_name', 'template', 'latest_version', 'print_status', 'requested_by', 'requested_at')
    search_fields = (
        'custom_id', # Thêm tìm theo custom_id
        'medical_record__patient__full_name',
        'medical_record__patient__ma_benh_nhan', # Thêm tìm theo mã bệnh nhân
        'template__name',
        'medical_record__id' # ID của MedicalRecord
    )
    list_filter = ('print_status', 'template', 'requested_at', 'requested_by')
    date_hierarchy = 'requested_at'
    ordering = ('-requested_at',)
    raw_id_fields = ('medical_record', 'template', 'requested_by', 'latest_version')
    inlines = [LabTestResultValueInline]

    fieldsets = (
        (None, {
            'fields': ('custom_id', 'medical_record', 'template', 'latest_version') # Thêm custom_id
        }),
        ('Trạng thái và Theo dõi In', {
            'fields': ('print_status', 'last_print_date')
        }),
        ('Thông tin Yêu cầu', {
            'fields': ('requested_by',),
        }),
    )
    readonly_fields = ('custom_id', 'requested_at', 'results_updated_at') # custom_id là readonly

    def custom_id_display(self, obj):
        return obj.custom_id if obj.custom_id else f"(Chưa có - ID DB: {obj.pk})"
    custom_id_display.short_description = 'ID Phiếu XN'
    custom_id_display.admin_order_field = 'custom_id'


    def medical_record_patient_name(self, obj):
        if obj.medical_record and obj.medical_record.patient:
            return f"{obj.medical_record.patient.full_name} (Mã BN: {obj.medical_record.patient.ma_benh_nhan})"
        return "N/A"
    medical_record_patient_name.short_description = 'Bệnh nhân (Mã BN)'
    medical_record_patient_name.admin_order_field = 'medical_record__patient__full_name'

    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.requested_by: # Khi tạo mới và chưa có người yêu cầu
            obj.requested_by = request.user
        # Logic tạo custom_id đã nằm trong model.save()
        super().save_model(request, obj, form, change)

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        lab_test_instance = form.instance
        # Tự động tạo các LabTestResultValue rỗng dựa trên template nếu chưa có
        if lab_test_instance.pk and lab_test_instance.template and not lab_test_instance.result_values.exists():
            for field in lab_test_instance.template.fields.all().order_by('field_order'):
                LabTestResultValue.objects.create(
                    lab_test=lab_test_instance,
                    template_field=field,
                    entered_by=request.user # Gán người dùng hiện tại là người tạo
                )
            # Cập nhật thời gian sửa kết quả
            lab_test_instance.results_updated_at = timezone.now()
            lab_test_instance.save(update_fields=['results_updated_at'])

# LabTestVersionAdmin (CẬP NHẬT)
@admin.register(LabTestVersion)
class LabTestVersionAdmin(admin.ModelAdmin):
    list_display = ('lab_test_custom_id_info', 'version_number', 'changed_by', 'changed_at', 'is_post_print')
    search_fields = (
        'lab_test__custom_id', # Thêm tìm theo custom_id của lab_test
        'lab_test__template__name',
        'lab_test__medical_record__patient__full_name',
        'lab_test__medical_record__patient__ma_benh_nhan', # Thêm tìm theo mã bệnh nhân
        'result_snapshot',
        'change_reason'
    )
    list_filter = ('is_post_print', 'changed_at', 'changed_by')
    date_hierarchy = 'changed_at'
    ordering = ('-changed_at',)
    raw_id_fields = ('lab_test', 'changed_by')

    fieldsets = (
        (None, {
            'fields': ('lab_test', 'version_number')
        }),
        ('Nội dung phiên bản', {
            'fields': ('result_snapshot',)
        }),
        ('Thông tin thay đổi', {
            'fields': ('is_post_print', 'changed_by', 'change_reason')
        }),
    )
    readonly_fields = ('changed_at',)

    def lab_test_custom_id_info(self, obj):
        if obj.lab_test:
            return obj.lab_test.custom_id if obj.lab_test.custom_id else f"(Chưa có ID - DB ID: {obj.lab_test.pk})"
        return "N/A"
    lab_test_custom_id_info.short_description = 'ID Phiếu Xét Nghiệm Gốc'
    lab_test_custom_id_info.admin_order_field = 'lab_test__custom_id'
