from django.contrib import admin
from django.contrib.contenttypes.admin import GenericTabularInline # Hoặc GenericStackedInline
from .models import FileAttachment

# Cách 1: Đăng ký FileAttachment như một model độc lập
@admin.register(FileAttachment)
class FileAttachmentAdmin(admin.ModelAdmin):
    list_display = ('file_name_display', 'content_object_display', 'file_type', 'file_size_display', 'uploaded_by', 'uploaded_at')
    search_fields = ('file_name', 'description', 'content_type__model') # Tìm theo tên file, mô tả, loại model liên quan
    list_filter = ('content_type', 'file_type', 'uploaded_at', 'uploaded_by')
    date_hierarchy = 'uploaded_at'
    ordering = ('-uploaded_at',)
    # raw_id_fields = ('uploaded_by',) # Giúp chọn uploaded_by dễ hơn

    # Các trường chỉ đọc trong form chi tiết
    readonly_fields = ('content_object_display', 'uploaded_at', 'file_url_display', 'file_size')

    fieldsets = (
        (None, {
            'fields': ('attachment_file', 'description')
        }),
        ('Thông tin File (tự động)', {
            'fields': ('file_name', 'file_type', 'file_size', 'file_url_display'),
        }),
        ('Đối tượng liên quan (Không sửa trực tiếp)', { # GFK không nên sửa trực tiếp qua form này
            'fields': ('content_type', 'object_id', 'content_object_display'),
        }),
        ('Thông tin theo dõi', {
            'fields': ('uploaded_by', 'uploaded_at'),
            'classes': ('collapse',),
        }),
    )

    def file_name_display(self, obj):
        return obj.file_name or obj.attachment_file.name if obj.attachment_file else "N/A"
    file_name_display.short_description = "Tên File"

    def content_object_display(self, obj):
        return str(obj.content_object) if obj.content_object else "N/A"
    content_object_display.short_description = "Đối tượng liên quan"

    def file_url_display(self, obj):
        if obj.file_url:
            return obj.file_url
        if obj.attachment_file:
            try:
                return obj.attachment_file.url
            except ValueError: # Có thể xảy ra nếu file không được lưu đúng cách hoặc storage có vấn đề
                return "Không có URL"
        return "N/A"
    file_url_display.short_description = "URL File"

    def file_size_display(self, obj):
        if obj.file_size:
            # Chuyển đổi bytes sang KB, MB cho dễ đọc
            if obj.file_size < 1024:
                return f"{obj.file_size} bytes"
            elif obj.file_size < 1024 * 1024:
                return f"{obj.file_size / 1024:.2f} KB"
            else:
                return f"{obj.file_size / (1024 * 1024):.2f} MB"
        return "N/A"
    file_size_display.short_description = "Kích thước"


    def save_model(self, request, obj, form, change):
        if not obj.pk and not obj.uploaded_by : # Khi tạo mới và chưa có người tải lên
            obj.uploaded_by = request.user
        super().save_model(request, obj, form, change)

    # Để GFK hoạt động đúng trong admin khi bạn muốn thêm FileAttachment
    # từ trang admin của FileAttachment, bạn thường không cần làm gì thêm ở đây.
    # Tuy nhiên, việc tạo FileAttachment thường sẽ được thực hiện từ form của
    # đối tượng cha (ví dụ: từ form Patient, upload file cho Patient đó).

# Cách 2: Sử dụng GenericTabularInline để thêm FileAttachments từ trang admin của model khác
# Ví dụ: Thêm vào admin.py của app 'patients'
# class FileAttachmentInline(GenericTabularInline):
#     model = FileAttachment
#     extra = 1 # Số form inline trống
#     fields = ('attachment_file', 'description', 'uploaded_by') # Các trường hiển thị inline
#     readonly_fields = ('uploaded_by',) # uploaded_by thường được tự động gán

# Và trong PatientAdmin (trong apps/patients/admin.py):
# class PatientAdmin(admin.ModelAdmin):
#     # ... các cấu hình khác ...
#     inlines = [FileAttachmentInline] # Thêm dòng này
