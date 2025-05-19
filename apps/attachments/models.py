import os
from django.db import models
from django.conf import settings # Để lấy AUTH_USER_MODEL
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify

# Hàm helper để tạo đường dẫn upload file duy nhất dựa trên tên đối tượng và tên file
def get_attachment_upload_path(instance, filename):
    # Lấy tên lớp của đối tượng liên quan (ví dụ: 'patient', 'medicalrecord')
    # và ID của đối tượng đó.
    # Điều này giúp tổ chức file trên S3.
    # Ví dụ: attachments/patient/123/filename.pdf
    #        attachments/medicalrecord/456/anotherfile.jpg

    # Lấy tên lớp của đối tượng được liên kết
    # content_object là đối tượng thực tế mà FileAttachment này được gắn vào
    # (ví dụ: một instance của Patient, hoặc MedicalRecord)
    related_object_type = slugify(instance.content_type.model) # 'patient', 'medicalrecord'
    related_object_id = instance.object_id

    # Lấy tên file gốc và phần mở rộng
    original_filename, file_extension = os.path.splitext(filename)
    # Tạo tên file an toàn hơn (slugify)
    safe_filename = slugify(original_filename) + file_extension

    return f'attachments/{related_object_type}/{related_object_id}/{safe_filename}'

class FileAttachment(models.Model):
    # Trường cho Generic Foreign Key
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('loại đối tượng liên quan')
    )
    object_id = models.PositiveIntegerField(_('ID đối tượng liên quan'))
    content_object = GenericForeignKey('content_type', 'object_id')

    # Trường lưu trữ file thực tế
    # `upload_to` có thể là một chuỗi hoặc một hàm.
    # Sử dụng hàm `get_attachment_upload_path` để tạo đường dẫn động.
    # Django sẽ tự động xử lý việc lưu file lên S3 nếu bạn đã cấu hình
    # DEFAULT_FILE_STORAGE và các cài đặt S3 khác trong settings.py.
    # Hiện tại, chúng ta chỉ định nghĩa trường FileField.
    # Việc cấu hình S3 sẽ là một bước riêng.
    attachment_file = models.FileField(
        _('tệp đính kèm'),
        upload_to=get_attachment_upload_path, # Sử dụng hàm helper
        null=True, blank=True # Cho phép null nếu file_url được dùng thay thế
    )
    # file_url có thể được dùng nếu bạn lưu file ở nơi khác và chỉ muốn lưu URL
    # Hoặc nó có thể là URL công khai của file trên S3 sau khi upload.
    file_url = models.URLField(_('đường dẫn file (URL)'), max_length=1024, null=True, blank=True)
    file_name = models.CharField(_('tên file hiển thị'), max_length=255, null=True, blank=True)
    file_type = models.CharField(_('loại file (MIME type)'), max_length=100, null=True, blank=True)
    file_size = models.PositiveIntegerField(_('kích thước file (bytes)'), null=True, blank=True)

    description = models.CharField(_('mô tả ngắn'), max_length=255, null=True, blank=True)

    # Thông tin theo dõi
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='file_attachments_uploaded',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('người tải lên')
    )
    uploaded_at = models.DateTimeField(_('ngày tải lên'), auto_now_add=True)

    def __str__(self):
        return self.file_name or f"Tệp đính kèm cho {self.content_type} ID {self.object_id}"

    def save(self, *args, **kwargs):
        # Tự động điền file_name, file_type, file_size nếu có file được upload
        if self.attachment_file and not self.file_name:
            self.file_name = os.path.basename(self.attachment_file.name)
        if self.attachment_file and not self.file_type and hasattr(self.attachment_file.file, 'content_type'):
             self.file_type = self.attachment_file.file.content_type
        if self.attachment_file and not self.file_size and hasattr(self.attachment_file, 'size'):
            self.file_size = self.attachment_file.size
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('tệp đính kèm')
        verbose_name_plural = _('danh sách tệp đính kèm')
        ordering = ['-uploaded_at']
        # Thêm index cho các trường GFK để tăng tốc độ truy vấn
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
        ]
