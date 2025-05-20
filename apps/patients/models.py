# apps/patients/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
# import uuid # Không cần uuid nữa nếu chỉ dùng số
import random # Thêm thư viện random

class Gender(models.TextChoices):
    MALE = 'MALE', _('Nam')
    FEMALE = 'FEMALE', _('Nữ')
    OTHER = 'OTHER', _('Khác')

class Patient(models.Model):
    ma_benh_nhan = models.CharField(
        _('mã bệnh nhân'),
        max_length=10, # Giảm max_length nếu chỉ có 6 chữ số (ví dụ: 6 nếu không có prefix, hoặc 9 nếu có "BN-")
                       # Hiện tại max_length=20 vẫn ổn. Nếu muốn chặt chẽ hơn, có thể đặt là 6.
        unique=True,
        editable=False,
        blank=True,
        null=False
    )
    full_name = models.CharField(_('họ và tên'), max_length=255)
    date_of_birth = models.DateField(_('ngày sinh'))
    gender = models.CharField(
        _('giới tính'),
        max_length=10,
        choices=Gender.choices
    )
    phone = models.CharField(_('số điện thoại'), max_length=20)
    address = models.CharField(_('địa chỉ'), max_length=255, null=True, blank=True)
    email = models.EmailField(_('email'), max_length=255, null=True, blank=True, unique=True)
    blood_type = models.CharField(_('nhóm máu'), max_length=10, null=True, blank=True)
    allergies = models.TextField(_('dị ứng'), null=True, blank=True)
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
        return f"{self.full_name} ({self.ma_benh_nhan})" if self.ma_benh_nhan else self.full_name

    def _generate_ma_benh_nhan(self):
        """
        Tạo mã bệnh nhân duy nhất gồm 6 chữ số.
        """
        # Tạo số ngẫu nhiên từ 100000 đến 999999
        # Sau đó chuyển thành chuỗi và đảm bảo có 6 chữ số (có thể không cần nếu random.randint luôn trả về 6 chữ số)
        # random_part = str(random.randint(0, 999999)).zfill(6)
        # Hoặc đơn giản hơn:
        random_part = str(random.randint(100000, 999999))
        return random_part # Chỉ trả về 6 chữ số

        # Nếu bạn vẫn muốn có tiền tố "BN-":
        # return f"BN-{random_part}"
        # Và nếu có tiền tố, hãy đảm bảo max_length của ma_benh_nhan đủ lớn (ví dụ: 9 hoặc 10)

    def save(self, *args, **kwargs):
        if not self.ma_benh_nhan:
            self.ma_benh_nhan = self._generate_ma_benh_nhan()
            # Đảm bảo mã là duy nhất
            while Patient.objects.filter(ma_benh_nhan=self.ma_benh_nhan).exclude(pk=self.pk).exists():
                self.ma_benh_nhan = self._generate_ma_benh_nhan()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = _('bệnh nhân')
        verbose_name_plural = _('danh sách bệnh nhân')
        ordering = ['full_name']
