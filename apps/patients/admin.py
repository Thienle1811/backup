# apps/patients/admin.py
from django.contrib import admin
from .models import Patient

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('ma_benh_nhan', 'full_name', 'email', 'phone', 'date_of_birth', 'gender', 'created_at', 'created_by')
    search_fields = ('ma_benh_nhan', 'full_name', 'email', 'phone') # Thêm ma_benh_nhan vào tìm kiếm
    list_filter = ('gender', 'blood_type', 'created_at')
    ordering = ('-created_at', 'full_name')
    date_hierarchy = 'created_at'
    
    # Hiển thị ma_benh_nhan dưới dạng chỉ đọc trong form chi tiết của admin
    readonly_fields = ('ma_benh_nhan', 'created_at', 'updated_at', 'created_by', 'updated_by')

    fieldsets = (
        (None, {
            'fields': ('ma_benh_nhan', 'full_name', 'date_of_birth', 'gender')
        }),
        (('Thông tin liên hệ'), {
            'fields': ('phone', 'address', 'email')
        }),
        (('Thông tin y tế'), {
            'fields': ('blood_type', 'allergies')
        }),
        (('Thông tin theo dõi'), {
            'fields': ('created_by', 'updated_by', 'created_at', 'updated_at')
        }),
    )
    # Nếu bạn không dùng fieldsets, chỉ cần thêm 'ma_benh_nhan' vào readonly_fields là đủ
    # để nó hiển thị ở dạng chỉ đọc nếu model field có editable=False.
    # Tuy nhiên, để đảm bảo nó xuất hiện trong form admin, bạn có thể cần thêm nó vào fieldsets
    # hoặc fields nếu bạn tùy chỉnh chúng.
