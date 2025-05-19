# apps/patients/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Gender(models.TextChoices):
    MALE = 'MALE', _('Nam')
    FEMALE = 'FEMALE', _('Nữ')
    OTHER = 'OTHER', _('Khác')

class Patient(models.Model):
    # Thông tin cá nhân
    full_name = models.CharField(_('họ và tên'), max_length=255) # Mặc định là bắt buộc
    date_of_birth = models.DateField(_('ngày sinh')) # Bỏ null=True, blank=True để làm bắt buộc
    gender = models.CharField(
        _('giới tính'),
        max_length=10,
        choices=Gender.choices
        # Bỏ null=True, blank=True để làm bắt buộc
    )
    phone = models.CharField(_('số điện thoại'), max_length=20) # Bỏ null=True, blank=True để làm bắt buộc
    
    # Các trường không bắt buộc (giữ nguyên hoặc tùy chỉnh theo ý bạn)
    address = models.CharField(_('địa chỉ'), max_length=255, null=True, blank=True)
    email = models.EmailField(_('email'), max_length=255, null=True, blank=True, unique=True)
    blood_type = models.CharField(_('nhóm máu'), max_length=10, null=True, blank=True)
    allergies = models.TextField(_('dị ứng'), null=True, blank=True)

    # Thông tin theo dõi (audit fields)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='patients_created',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('người tạo')
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='patients_updated',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('người cập nhật')
    )
    created_at = models.DateTimeField(_('ngày tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('ngày cập nhật'), auto_now=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = _('bệnh nhân')
        verbose_name_plural = _('danh sách bệnh nhân')
        ordering = ['full_name']
