"""
apps/medical_records/models.py

Models cho MedicalRecord và phiên bản history
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation

from apps.patients.models import Patient
from apps.activity_logs.models import ActivityLog

# ---------------------------------------------------------------------------
# Mixins dùng chung
# ---------------------------------------------------------------------------


class TimeStampedModel(models.Model):
    """Mixin thêm thời gian tạo và cập nhật."""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        abstract = True


class VersionedModelMixin(models.Model):
    """Mixin cho các bảng lưu version history."""

    version_number = models.PositiveIntegerField(verbose_name="Phiên bản")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Người thực hiện",
    )
    change_reason = models.TextField(blank=True, verbose_name="Lý do thay đổi")
    is_post_print = models.BooleanField(default=False, verbose_name="Sửa sau in")
    changed_at = models.DateTimeField(
        default=timezone.now, verbose_name="Thời gian thay đổi"
    )

    class Meta:
        abstract = True
        ordering = ("-version_number",)


# ---------------------------------------------------------------------------
# MedicalRecord chính
# ---------------------------------------------------------------------------


class MedicalRecord(TimeStampedModel):
    """Bệnh án của một lần khám bệnh."""

    patient = models.ForeignKey(
        Patient,
        related_name="medical_records",
        on_delete=models.CASCADE,
        verbose_name="Bệnh nhân",
    )
    doctor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="medical_records",
        on_delete=models.CASCADE,
        verbose_name="Bác sĩ",
    )
    record_date = models.DateField(default=timezone.now, verbose_name="Ngày khám")
    symptoms = models.TextField(verbose_name="Triệu chứng")
    diagnosis = models.TextField(verbose_name="Chẩn đoán")
    treatment_plan = models.TextField(verbose_name="Kế hoạch điều trị")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")
    is_completed = models.BooleanField(default=False, verbose_name="Đã hoàn thành")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="medical_records_created",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Người tạo",
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="medical_records_updated",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Người cập nhật",
    )

    latest_version = models.PositiveIntegerField(
        default=1, verbose_name="Phiên bản mới nhất"
    )

    # Liên kết tới activity logs
    activity_logs = GenericRelation(ActivityLog, related_query_name="medical_record")

    class Meta:
        verbose_name = "Phiếu khám"
        verbose_name_plural = "Danh sách phiếu khám"
        ordering = ("-record_date",)

    def __str__(self) -> str:
        return f"Phiếu khám #{self.id} - {self.patient.full_name}"

    @property
    def labtest_count(self):
        return self.lab_tests.count()

    @property
    def unlinked_labtests(self):
        return self.patient.lab_tests.filter(medical_record__isnull=True)

    def create_version(self, user=None, reason: str = "") -> "MedicalRecordVersion":
        """Tạo snapshot bản ghi hiện tại sang MedicalRecordVersion."""
        next_ver = self.latest_version + 1
        version = MedicalRecordVersion.objects.create(
            medical_record=self,
            version_number=next_ver,
            changed_by=user,
            change_reason=reason,
            is_post_print=False,
        )
        # Copy hiện trạng
        version.diagnosis = self.diagnosis
        version.notes = self.notes
        version.save()

        # Cập nhật counter
        self.latest_version = next_ver
        self.save(update_fields=["latest_version"])
        return version


# ---------------------------------------------------------------------------
# History/version của MedicalRecord
# ---------------------------------------------------------------------------


class MedicalRecordVersion(TimeStampedModel, VersionedModelMixin):
    """Lưu lịch sử thay đổi của MedicalRecord."""

    medical_record = models.ForeignKey(
        MedicalRecord,
        related_name="versions",
        on_delete=models.CASCADE,
        verbose_name="Bệnh án",
    )
    diagnosis = models.TextField(blank=True, verbose_name="Chẩn đoán")
    notes = models.TextField(blank=True, verbose_name="Ghi chú")

    class Meta(VersionedModelMixin.Meta):
        unique_together = ("medical_record", "version_number")
        verbose_name = "Phiên bản bệnh án"
        verbose_name_plural = "Danh sách phiên bản bệnh án"

    def __str__(self) -> str:
        return f"{self.medical_record} – v{self.version_number}"


class Prescription(models.Model):
    medical_record = models.OneToOneField(MedicalRecord, on_delete=models.CASCADE, related_name='prescription')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Đơn thuốc'
        verbose_name_plural = 'Đơn thuốc'
        ordering = ['-created_at']

    def __str__(self):
        return f'Đơn thuốc #{self.id} - {self.medical_record.patient.full_name}'


class PrescriptionItem(models.Model):
    prescription = models.ForeignKey(Prescription, on_delete=models.CASCADE, related_name='items')
    medicine_name = models.CharField(max_length=200, verbose_name='Tên thuốc')
    dosage = models.CharField(max_length=100, verbose_name='Liều dùng')
    frequency = models.CharField(max_length=100, verbose_name='Tần suất')
    duration = models.CharField(max_length=100, verbose_name='Thời gian')
    notes = models.TextField(blank=True, verbose_name='Ghi chú')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Chi tiết đơn thuốc'
        verbose_name_plural = 'Chi tiết đơn thuốc'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.medicine_name} - {self.dosage}'
