from django.db import models
from django.conf import settings # Để lấy AUTH_USER_MODEL
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _

class ActivityLog(models.Model):
    # Các lựa chọn cho trường action (ví dụ)
    # Bạn có thể định nghĩa các hành động cụ thể hơn cho ứng dụng của mình
    class ActionChoices(models.TextChoices):
        CREATED = 'CREATED', _('Đã tạo')
        UPDATED = 'UPDATED', _('Đã cập nhật')
        DELETED = 'DELETED', _('Đã xóa')
        VIEWED = 'VIEWED', _('Đã xem')
        PRINTED = 'PRINTED', _('Đã in')
        LOGGED_IN = 'LOGGED_IN', _('Đăng nhập')
        LOGGED_OUT = 'LOGGED_OUT', _('Đăng xuất')
        # Thêm các hành động khác nếu cần

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL, # Nếu user bị xóa, log vẫn còn nhưng user là null
        null=True, blank=True, # Cho phép user là null (ví dụ, hành động của hệ thống)
        verbose_name=_('người dùng thực hiện')
    )

    # Trường cho Generic Foreign Key (đối tượng bị tác động)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_('loại đối tượng bị tác động'),
        null=True, blank=True # Cho phép null nếu hành động không liên quan đến đối tượng cụ thể (ví dụ: đăng nhập)
    )
    object_id = models.PositiveIntegerField(
        _('ID đối tượng bị tác động'),
        null=True, blank=True
    )
    # content_object là đối tượng thực tế mà log này được gắn vào
    # (ví dụ: một instance của Patient, MedicalRecord, LabTest, etc.)
    # Hoặc có thể là None nếu hành động không gắn với đối tượng cụ thể.
    target_object = GenericForeignKey('content_type', 'object_id') # Đổi tên từ content_object để tránh nhầm lẫn

    action = models.CharField(
        _('hành động'),
        max_length=50,
        choices=ActionChoices.choices, # Sử dụng các lựa chọn đã định nghĩa
        db_index=True # Thêm index cho trường action để tìm kiếm nhanh hơn
    )
    details = models.TextField(_('chi tiết hành động'), null=True, blank=True) # Mô tả thêm về hành động
    log_timestamp = models.DateTimeField(_('thời điểm ghi log'), auto_now_add=True, db_index=True)

    ip_address = models.GenericIPAddressField(_('địa chỉ IP'), null=True, blank=True)
    user_agent = models.CharField(_('user agent'), max_length=512, null=True, blank=True)


    def __str__(self):
        user_str = self.user.email if self.user else _("Hệ thống")
        target_str = str(self.target_object) if self.target_object else ""
        action_display = self.get_action_display() # Lấy tên hiển thị của action

        if target_str:
            return f"{user_str} {action_display.lower()} '{target_str}' lúc {self.log_timestamp.strftime('%H:%M %d/%m/%Y')}"
        else:
            return f"{user_str} {action_display.lower()} lúc {self.log_timestamp.strftime('%H:%M %d/%m/%Y')}"


    class Meta:
        verbose_name = _('nhật ký hoạt động')
        verbose_name_plural = _('danh sách nhật ký hoạt động')
        ordering = ['-log_timestamp'] # Sắp xếp theo thời gian mới nhất
        # Thêm index cho các trường GFK để tăng tốc độ truy vấn
        indexes = [
            models.Index(fields=["content_type", "object_id"]),
            models.Index(fields=["log_timestamp"]),
            models.Index(fields=["user", "action"]),
        ]
