"""apps/activity_logs/models.py – Hệ thống ghi nhật ký hoạt động"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# ---------------------------------------------------------------------------
# Lựa chọn hành động – có thể mở rộng khi cần
# ---------------------------------------------------------------------------


class ActivityAction(models.TextChoices):
    CREATE = "create", "Tạo mới"
    UPDATE = "update", "Cập nhật"
    DELETE = "delete", "Xoá"
    PRINT = "print", "In PDF"
    LOGIN = "login", "Đăng nhập"


# ---------------------------------------------------------------------------
# Model ActivityLog
# ---------------------------------------------------------------------------


class ActivityLog(models.Model):
    """Ghi lại hành động của người dùng trên bất kỳ thực thể nào."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Người thực hiện",
    )

    # Generic FK tới bản ghi
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")

    action = models.CharField(
        max_length=20,
        choices=ActivityAction.choices,
        verbose_name="Hành động",
    )
    message = models.TextField(blank=True, verbose_name="Mô tả chi tiết")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    timestamp = models.DateTimeField(default=timezone.now, verbose_name="Thời gian")

    class Meta:
        verbose_name = "Nhật ký hoạt động"
        verbose_name_plural = "Nhật ký hoạt động"
        ordering = ("-timestamp",)

    def __str__(self):
        return f"{self.get_action_display()} – {self.content_type}#{self.object_id} by {self.user}"


# ---------------------------------------------------------------------------
# Helper tiện lợi để ghi log trong các view/service
# ---------------------------------------------------------------------------


def log_activity(user, instance, action: str, message: str = "", ip: str | None = None):
    """Hàm tiện ích: gọi ở view/service để tạo ActivityLog nhanh."""
    ActivityLog.objects.create(
        user=user,
        content_object=instance,
        action=action,
        message=message,
        ip_address=ip,
    )
