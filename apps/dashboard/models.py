# apps/dashboard/models.py
from django.db import models
from django.utils.translation import gettext_lazy as _

class ClinicSetting(models.Model):
    name = models.CharField(_("tên phòng khám"), max_length=255, default="Phòng khám Medionco")
    address = models.TextField(_("địa chỉ"), blank=True, null=True)
    phone = models.CharField(_("số điện thoại"), max_length=50, blank=True, null=True)
    email = models.EmailField(_("email phòng khám"), blank=True, null=True)
    logo = models.ImageField(_("logo phòng khám"), upload_to='clinic_logo/', blank=True, null=True)
    # Thêm các trường khác nếu bạn cần, ví dụ: website, mã số thuế, giờ làm việc...

    # Để đảm bảo chỉ có một bản ghi ClinicSetting (Singleton pattern)
    # chúng ta có thể thêm một phương thức save tùy chỉnh hoặc quản lý việc này ở logic view.
    # Cách đơn giản nhất là chỉ tạo một đối tượng qua Django Admin hoặc một command.

    def __str__(self):
        return self.name or _("Cài đặt Phòng khám")

    class Meta:
        verbose_name = _("cài đặt phòng khám")
        verbose_name_plural = _("cài đặt phòng khám")

    # Phương thức tiện ích để lấy bản ghi cài đặt duy nhất (hoặc tạo nếu chưa có)
    @classmethod
    def get_instance(cls):
        instance, created = cls.objects.get_or_create(pk=1, defaults={'name': _('Phòng khám của bạn')})
        # Bạn có thể đặt các giá trị mặc định khác ở đây nếu muốn
        # if created:
        #     instance.address = "Địa chỉ mặc định"
        #     instance.save()
        return instance