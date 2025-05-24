"""apps/patients/models.py – Model bệnh nhân
- `full_name` và `phone` là **bắt buộc**.
- Các thông tin cá nhân khác là **tuỳ chọn** để tra cứu/hiển thị.
"""

from django.db import models


class Patient(models.Model):
    # Bắt buộc
    full_name = models.CharField(
        max_length=255,
        verbose_name="Họ tên",
        help_text="Nhập họ tên bệnh nhân",
    )
    phone = models.CharField(
        max_length=50, 
        verbose_name="Số điện thoại liên hệ",
        blank=True,
        null=True
    )

    # Tuỳ chọn bổ sung
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Ngày sinh")
    gender = models.CharField(max_length=10, blank=True, verbose_name="Giới tính")
    address = models.CharField(max_length=255, blank=True, verbose_name="Địa chỉ")
    email = models.EmailField(blank=True, verbose_name="Email")
    blood_type = models.CharField(max_length=10, blank=True, verbose_name="Nhóm máu")
    allergies = models.TextField(blank=True, verbose_name="Dị ứng")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        verbose_name = "Bệnh nhân"
        verbose_name_plural = "Danh sách bệnh nhân"
        ordering = ("-created_at",)

    def __str__(self):
        return self.full_name
