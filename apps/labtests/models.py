"""apps/labtests/models.py – Mô hình LabTest Neo

Entities:
1. TestCategory: Loại xét nghiệm (panel)
2. TestItem: Mục xét nghiệm (item) gồm tên, khoảng tham chiếu, đơn vị
3. LabTest: Phiếu xét nghiệm của 1 bệnh nhân với 1 TestCategory
4. LabTestResultValue: Giá trị cho mỗi TestItem
5. Versioning: lưu lịch sử snapshot của LabTest và giá trị
"""

from __future__ import annotations

from django.db import models, transaction
from django.conf import settings
from django.utils import timezone
from django.contrib.contenttypes.fields import GenericRelation

from apps.patients.models import Patient
from apps.medical_records.models import MedicalRecord


# ---------------------------------------------------------------------------
# Mixins chung
# ---------------------------------------------------------------------------
class TimeStampedModel(models.Model):
    """Mixin thêm timestamp tạo và cập nhật"""

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        abstract = True


class VersionedModelMixin(models.Model):
    """Mixin phiên bản cho snapshot tables"""

    version_number = models.PositiveIntegerField(verbose_name="Phiên bản")
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Người thay đổi",
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
# 1. Loại xét nghiệm (panel)
# ---------------------------------------------------------------------------
class TestCategory(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True, verbose_name="Loại xét nghiệm")
    description = models.TextField(blank=True, verbose_name="Mô tả")
    is_active = models.BooleanField(default=True, verbose_name="Kích hoạt")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        verbose_name="Người tạo",
    )

    class Meta:
        verbose_name = "Loại xét nghiệm"
        verbose_name_plural = "Danh sách loại xét nghiệm"
        ordering = ("name",)

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# 2. Mục xét nghiệm (item)
# ---------------------------------------------------------------------------
class TestItem(models.Model):
    category = models.ForeignKey(
        TestCategory,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="Loại xét nghiệm",
    )
    name = models.CharField(max_length=100, verbose_name="Tên xét nghiệm")
    reference_range = models.CharField(
        max_length=100, blank=True, verbose_name="Khoảng tham chiếu"
    )
    unit = models.CharField(max_length=50, blank=True, verbose_name="Đơn vị")
    order = models.PositiveIntegerField(default=0, verbose_name="Thứ tự")

    class Meta:
        unique_together = ("category", "name")
        ordering = ("order",)
        verbose_name = "Mục xét nghiệm"
        verbose_name_plural = "Danh sách mục xét nghiệm"

    def __str__(self):
        return f"{self.category.name} – {self.name}"


# ---------------------------------------------------------------------------
# 3. Phiếu xét nghiệm
# ---------------------------------------------------------------------------
class LabTest(TimeStampedModel):
    patient = models.ForeignKey(
        Patient,
        related_name="lab_tests",
        on_delete=models.CASCADE,
        verbose_name="Bệnh nhân",
    )
    medical_record = models.ForeignKey(
        MedicalRecord,
        related_name="lab_tests",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Bệnh án liên quan",
    )
    category = models.ForeignKey(
        TestCategory,
        on_delete=models.PROTECT,
        verbose_name="Loại xét nghiệm",
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="lab_tests_created",
        verbose_name="Người thực hiện",
    )
    print_status = models.CharField(
        max_length=20, default="Chưa in", verbose_name="Trạng thái in"
    )
    last_print_date = models.DateTimeField(
        null=True, blank=True, verbose_name="Lần in cuối"
    )
    latest_version = models.PositiveIntegerField(
        default=1, verbose_name="Phiên bản mới nhất"
    )

    activity_logs = GenericRelation(
        "activity_logs.ActivityLog",
        related_query_name="lab_test",
    )

    class Meta:
        verbose_name = "Phiếu xét nghiệm"
        verbose_name_plural = "Danh sách phiếu xét nghiệm"
        ordering = ("-created_at",)

    def __str__(self):
        return f"{self.patient.full_name} – {self.category.name}"

    @transaction.atomic
    def create_version(self, user=None, reason: str = "") -> "LabTestVersion":
        next_ver = self.latest_version + 1
        version = LabTestVersion.objects.create(
            lab_test=self,
            version_number=next_ver,
            changed_by=user,
            change_reason=reason,
            is_post_print=self.print_status == "Đã in",
        )
        # Snapshot result values
        LabTestResultValueVersion.objects.bulk_create(
            [
                LabTestResultValueVersion(
                    lab_test_version=version,
                    item=rv.item,
                    value=rv.value,
                    comment=rv.comment,
                )
                for rv in self.results.all()
            ]
        )
        self.latest_version = next_ver
        self.save(update_fields=["latest_version"])
        return version


# ---------------------------------------------------------------------------
# 4. Giá trị kết quả
# ---------------------------------------------------------------------------
class LabTestResultValue(models.Model):
    lab_test = models.ForeignKey(
        LabTest,
        related_name="results",
        on_delete=models.CASCADE,
        verbose_name="Phiếu xét nghiệm",
    )
    item = models.ForeignKey(
        TestItem,
        on_delete=models.PROTECT,
        related_name="values",
        verbose_name="Mục xét nghiệm",
    )
    value = models.CharField(max_length=100, blank=True, verbose_name="Giá trị")
    comment = models.CharField(max_length=255, blank=True, verbose_name="Ghi chú")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")

    class Meta:
        unique_together = ("lab_test", "item")
        verbose_name = "Kết quả xét nghiệm"
        verbose_name_plural = "Danh sách kết quả xét nghiệm"

    def __str__(self):
        return f"{self.item.name}: {self.value}"


# ---------------------------------------------------------------------------
# 5. Snapshot version
# ---------------------------------------------------------------------------
class LabTestVersion(TimeStampedModel, VersionedModelMixin):
    lab_test = models.ForeignKey(
        LabTest,
        related_name="versions",
        on_delete=models.CASCADE,
        verbose_name="Phiếu xét nghiệm",
    )

    class Meta(VersionedModelMixin.Meta):
        unique_together = ("lab_test", "version_number")
        verbose_name = "Phiên bản phiếu xét nghiệm"
        verbose_name_plural = "Danh sách phiên bản phiếu xét nghiệm"

    def __str__(self):
        return f"{self.lab_test} – v{self.version_number}"


class LabTestResultValueVersion(models.Model):
    lab_test_version = models.ForeignKey(
        LabTestVersion,
        related_name="result_values",
        on_delete=models.CASCADE,
        verbose_name="Phiên bản phiếu",
    )
    item = models.ForeignKey(
        TestItem,
        on_delete=models.PROTECT,
        verbose_name="Mục xét nghiệm",
    )
    value = models.CharField(max_length=100, blank=True, verbose_name="Giá trị")
    comment = models.CharField(max_length=255, blank=True, verbose_name="Ghi chú")

    class Meta:
        unique_together = ("lab_test_version", "item")
        verbose_name = "Kết quả xét nghiệm (snapshot)"
        verbose_name_plural = "Danh sách kết quả xét nghiệm (snapshot)"

    def __str__(self):
        return (
            f"v{self.lab_test_version.version_number} – {self.item.name}: {self.value}"
        )
