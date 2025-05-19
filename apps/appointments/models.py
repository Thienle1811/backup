from django.db import models
from django.conf import settings # Để lấy AUTH_USER_MODEL
from django.utils.translation import gettext_lazy as _
# from apps.patients.models import Patient # Sẽ dùng chuỗi tham chiếu
# from apps.accounts.models import CustomUser # Sẽ dùng settings.AUTH_USER_MODEL

class Appointment(models.Model):
    # Các lựa chọn cho trường status
    class AppointmentStatus(models.TextChoices):
        PENDING = 'PENDING', _('Chờ xác nhận')
        CONFIRMED = 'CONFIRMED', _('Đã xác nhận')
        COMPLETED = 'COMPLETED', _('Đã hoàn thành') # Hoặc 'DONE' như trong Modeling.md
        CANCELLED = 'CANCELLED', _('Đã hủy')
        # Bạn có thể thêm các trạng thái khác nếu cần, ví dụ: NO_SHOW = 'NO_SHOW', _('Không đến')

    patient = models.ForeignKey(
        'patients.Patient', # Tham chiếu đến Patient model của app patients
        on_delete=models.CASCADE, # Nếu bệnh nhân bị xóa, lịch hẹn cũng bị xóa
        related_name='appointments',
        verbose_name=_('bệnh nhân')
    )
    staff = models.ForeignKey(
        settings.AUTH_USER_MODEL, # Tham chiếu đến CustomUser model của bạn
        on_delete=models.SET_NULL, # Nếu nhân viên bị xóa, lịch hẹn vẫn còn nhưng staff là null
        null=True, blank=True, # Cho phép staff là null (ví dụ, lịch hẹn chung chưa gán cụ thể)
        related_name='staff_appointments',
        verbose_name=_('nhân viên (bác sĩ/KTV)')
        # Bạn có thể thêm limit_choices_to để chỉ cho phép chọn user là staff
        # limit_choices_to={'is_staff': True} # Hoặc một group cụ thể
    )
    appointment_date = models.DateField(_('ngày hẹn'))
    appointment_time = models.TimeField(_('giờ hẹn'), null=True, blank=True) # Giờ hẹn có thể không bắt buộc
    
    status = models.CharField(
        _('trạng thái lịch hẹn'),
        max_length=20,
        choices=AppointmentStatus.choices,
        default=AppointmentStatus.PENDING
    )
    notes = models.TextField(_('ghi chú cho lịch hẹn'), null=True, blank=True) # Ghi chú thêm

    # Thông tin theo dõi
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='appointments_created',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('người tạo lịch hẹn')
    )
    created_at = models.DateTimeField(_('ngày tạo lịch'), auto_now_add=True)
    updated_at = models.DateTimeField(_('ngày cập nhật lịch'), auto_now=True)

    def __str__(self):
        patient_name = self.patient.full_name if self.patient else _("Không rõ bệnh nhân")
        staff_name = self.staff.get_full_name() if self.staff else _("Chưa gán nhân viên")
        appointment_datetime_str = f"{self.appointment_date.strftime('%d/%m/%Y')}"
        if self.appointment_time:
            appointment_datetime_str += f" {self.appointment_time.strftime('%H:%M')}"
        return f"Lịch hẹn cho {patient_name} với {staff_name} vào {appointment_datetime_str} ({self.get_status_display()})"

    class Meta:
        verbose_name = _('lịch hẹn')
        verbose_name_plural = _('danh sách lịch hẹn')
        ordering = ['appointment_date', 'appointment_time'] # Sắp xếp theo ngày giờ hẹn
