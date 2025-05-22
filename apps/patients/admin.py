from django.contrib import admin
from django.utils.html import format_html
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'full_name', 'gender', 'date_of_birth', 'phone', 'email', 'created_at', 'medical_records_count', 'lab_tests_count')
    list_filter = ('gender', 'created_at')
    search_fields = ('full_name', 'phone', 'email', 'address')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    def medical_records_count(self, obj):
        count = obj.medical_records.count()
        return format_html('<a href="{}?patient__id__exact={}">{}</a>',
            '/admin/medical_records/medicalrecord/',
            obj.id,
            count
        )
    medical_records_count.short_description = 'Số phiếu khám'

    def lab_tests_count(self, obj):
        count = obj.lab_tests.count()
        return format_html('<a href="{}?patient__id__exact={}">{}</a>',
            '/admin/labtests/labtest/',
            obj.id,
            count
        )
    lab_tests_count.short_description = 'Số phiếu xét nghiệm'
