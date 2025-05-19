from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
    # Không cần import Patient trực tiếp ở đây nữa nếu dùng chuỗi tham chiếu

class MedicalRecordVersion(models.Model):
        medical_record = models.ForeignKey(
            'MedicalRecord', # Tham chiếu bằng chuỗi
            on_delete=models.CASCADE,
            related_name='versions',
            verbose_name=_('hồ sơ bệnh án gốc')
        )
        version_number = models.PositiveIntegerField(_('số phiên bản'))
        diagnosis = models.TextField(_('chẩn đoán (phiên bản)'), null=True, blank=True)
        notes = models.TextField(_('ghi chú của bác sĩ (phiên bản)'), null=True, blank=True)
        is_post_print = models.BooleanField(_('chỉnh sửa sau khi in'), default=False)
        changed_by = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            on_delete=models.SET_NULL,
            null=True, blank=True,
            verbose_name=_('người thay đổi')
        )
        change_reason = models.CharField(_('lý do thay đổi'), max_length=255, null=True, blank=True)
        changed_at = models.DateTimeField(_('thời điểm thay đổi'), auto_now_add=True)

        class Meta:
            verbose_name = _('phiên bản hồ sơ bệnh án')
            verbose_name_plural = _('các phiên bản hồ sơ bệnh án')
            ordering = ['medical_record', '-version_number']
            unique_together = ('medical_record', 'version_number')

        def __str__(self):
            return f"Phiên bản {self.version_number} của hồ sơ {self.medical_record_id}"

class MedicalRecord(models.Model):
        patient = models.ForeignKey(
            'patients.Patient', # <<< THAY ĐỔI Ở ĐÂY: Sử dụng chuỗi 'app_name.ModelName'
            on_delete=models.CASCADE,
            related_name='medical_records',
            verbose_name=_('bệnh nhân')
        )
        record_date = models.DateField(_('ngày khám'))
        diagnosis = models.TextField(_('chẩn đoán (hiện hành)'), null=True, blank=True)
        notes = models.TextField(_('ghi chú của bác sĩ (hiện hành)'), null=True, blank=True)
        latest_version = models.OneToOneField(
            'MedicalRecordVersion', # <<< THAY ĐỔI Ở ĐÂY (hoặc 'medical_records.MedicalRecordVersion')
            on_delete=models.SET_NULL,
            null=True, blank=True,
            related_name='current_for_record',
            verbose_name=_('phiên bản mới nhất')
        )
        created_by = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name='medical_records_created',
            on_delete=models.SET_NULL,
            null=True, blank=True,
            verbose_name=_('người tạo')
        )
        updated_by = models.ForeignKey(
            settings.AUTH_USER_MODEL,
            related_name='medical_records_updated',
            on_delete=models.SET_NULL,
            null=True, blank=True,
            verbose_name=_('người cập nhật')
        )
        created_at = models.DateTimeField(_('ngày tạo'), auto_now_add=True)
        updated_at = models.DateTimeField(_('ngày cập nhật'), auto_now=True)

        def __str__(self):
            # Kiểm tra self.patient có tồn tại không trước khi truy cập full_name
            patient_name = self.patient.full_name if self.patient else "Không có bệnh nhân"
            return f"Hồ sơ ngày {self.record_date.strftime('%d/%m/%Y')} cho {patient_name}"

        class Meta:
            verbose_name = _('hồ sơ bệnh án')
            verbose_name_plural = _('danh sách hồ sơ bệnh án')
            ordering = ['-record_date', 'patient']
    