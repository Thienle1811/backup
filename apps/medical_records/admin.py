from django.contrib import admin
from django.utils.html import format_html
from .models import MedicalRecord, Prescription, PrescriptionItem

@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_link', 'doctor_link', 'created_at', 'status_badge')
    list_filter = ('created_at', 'doctor')
    search_fields = ('patient__full_name', 'doctor__username', 'symptoms', 'diagnosis')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def patient_link(self, obj):
        return format_html('<a href="{}">{}</a>',
            f'/admin/patients/patient/{obj.patient.id}/change/',
            obj.patient.full_name
        )
    patient_link.short_description = 'Bệnh nhân'

    def doctor_link(self, obj):
        return format_html('<a href="{}">{}</a>',
            f'/admin/accounts/user/{obj.doctor.id}/change/',
            obj.doctor.get_full_name() or obj.doctor.username
        )
    doctor_link.short_description = 'Bác sĩ'

    def status_badge(self, obj):
        if obj.is_completed:
            return format_html('<span class="badge bg-success">Hoàn thành</span>')
        return format_html('<span class="badge bg-warning">Đang điều trị</span>')
    status_badge.short_description = 'Trạng thái'

@admin.register(Prescription)
class PrescriptionAdmin(admin.ModelAdmin):
    list_display = ('medical_record_link', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    search_fields = ('medical_record__patient__full_name',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'

    def medical_record_link(self, obj):
        return format_html('<a href="{}">{}</a>',
            f'/admin/medical_records/medicalrecord/{obj.medical_record.id}/change/',
            f'Phiếu khám #{obj.medical_record.id}'
        )
    medical_record_link.short_description = 'Phiếu khám'

@admin.register(PrescriptionItem)
class PrescriptionItemAdmin(admin.ModelAdmin):
    list_display = ('prescription_link', 'medicine_name', 'dosage', 'frequency', 'duration')
    list_filter = ('prescription__created_at',)
    search_fields = ('medicine_name', 'dosage', 'frequency', 'duration')
    readonly_fields = ('created_at', 'updated_at')

    def prescription_link(self, obj):
        return format_html('<a href="{}">{}</a>',
            f'/admin/medical_records/prescription/{obj.prescription.id}/change/',
            f'Đơn thuốc #{obj.prescription.id}'
        )
    prescription_link.short_description = 'Đơn thuốc'
