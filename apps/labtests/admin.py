# ---------------------------------------------------------------------------
# 3️⃣  apps/labtests/admin.py
# ---------------------------------------------------------------------------

from django.contrib import admin
from django.utils.html import format_html
from .models import TestCategory, TestItem, LabTest, LabTestResultValue


class TestItemInline(admin.TabularInline):
    model = TestItem
    extra = 1
    fields = ("order", "name", "unit", "reference_range")


@admin.register(TestCategory)
class TestCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'created_at', 'updated_at')
    list_filter = ('is_active',)
    search_fields = ('name',)
    ordering = ('name',)
    inlines = [TestItemInline]


class ResultInline(admin.TabularInline):
    model = LabTestResultValue
    extra = 0
    readonly_fields = ("item", "value", "comment")


@admin.register(LabTest)
class LabTestAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient_link', 'category_link', 'created_by_link', 'created_at', 'status_badge')
    list_filter = ('category', 'created_at', 'created_by')
    search_fields = ('patient__full_name', 'category__name', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    inlines = [ResultInline]

    def patient_link(self, obj):
        return format_html('<a href="{}">{}</a>', 
            f'/admin/patients/patient/{obj.patient.id}/change/',
            obj.patient.full_name
        )
    patient_link.short_description = 'Bệnh nhân'

    def category_link(self, obj):
        return format_html('<a href="{}">{}</a>',
            f'/admin/labtests/testcategory/{obj.category.id}/change/',
            obj.category.name
        )
    category_link.short_description = 'Loại xét nghiệm'

    def created_by_link(self, obj):
        return format_html('<a href="{}">{}</a>',
            f'/admin/accounts/user/{obj.created_by.id}/change/',
            obj.created_by.get_full_name() or obj.created_by.username
        )
    created_by_link.short_description = 'Người tạo'

    def status_badge(self, obj):
        return format_html('<span class="badge bg-warning">Chờ kết quả</span>')
    status_badge.short_description = 'Trạng thái'


@admin.register(LabTestResultValue)
class LabTestResultValueAdmin(admin.ModelAdmin):
    list_display = ('lab_test_link', 'item_name', 'value', 'comment')
    list_filter = ('lab_test__category',)
    search_fields = ('lab_test__patient__full_name', 'item__name', 'value', 'comment')

    def lab_test_link(self, obj):
        return format_html('<a href="{}">{}</a>',
            f'/admin/labtests/labtest/{obj.lab_test.id}/change/',
            f'Phiếu #{obj.lab_test.id}'
        )
    lab_test_link.short_description = 'Phiếu xét nghiệm'

    def item_name(self, obj):
        return obj.item.name
    item_name.short_description = 'Chỉ số'
