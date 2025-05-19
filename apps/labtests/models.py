from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone # Cần cho một số logic tự động (ví dụ trong admin)

# LabTestTemplate
class LabTestTemplate(models.Model):
    name = models.CharField(_('tên mẫu xét nghiệm'), max_length=255, unique=True)
    description = models.TextField(_('mô tả'), null=True, blank=True)
    is_active = models.BooleanField(_('đang hoạt động'), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='lab_test_templates_created',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('người tạo')
    )
    created_at = models.DateTimeField(_('ngày tạo'), auto_now_add=True)
    updated_at = models.DateTimeField(_('ngày cập nhật'), auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _('mẫu xét nghiệm')
        verbose_name_plural = _('danh sách mẫu xét nghiệm')
        ordering = ['name']

# LabTestTemplateField
class LabTestTemplateField(models.Model):
    template = models.ForeignKey(
        LabTestTemplate,
        related_name='fields',
        on_delete=models.CASCADE,
        verbose_name=_('mẫu xét nghiệm cha')
    )
    field_name = models.CharField(_('tên chỉ số'), max_length=255)
    result_guidance = models.CharField(
        _('hướng dẫn/placeholder kết quả'),
        max_length=255,
        blank=True, null=True,
        help_text=_("Nhập hướng dẫn, giá trị mẫu, hoặc placeholder cho ô kết quả khi thực hiện xét nghiệm.")
    )
    reference_range_text = models.CharField(
        _('khoảng tham chiếu (dạng text)'),
        max_length=255, null=True, blank=True,
        help_text=_("Ví dụ: Âm tính, <10.0, Nam: 60-120 Nữ: 40-100")
    )
    unit = models.CharField(_('đơn vị'), max_length=50, null=True, blank=True)
    field_order = models.PositiveIntegerField(_('thứ tự hiển thị'), default=0, help_text=_('Thứ tự hiển thị của chỉ số trong mẫu'))
    
    # Các trường này có thể vẫn hữu ích cho việc lọc hoặc tính toán nếu dữ liệu có thể được chuẩn hóa
    normal_min = models.DecimalField(_('giá trị bình thường (min)'), max_digits=10, decimal_places=2, null=True, blank=True)
    normal_max = models.DecimalField(_('giá trị bình thường (max)'), max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.template.name} - {self.field_name}"

    class Meta:
        verbose_name = _('chỉ số của mẫu xét nghiệm')
        verbose_name_plural = _('các chỉ số của mẫu xét nghiệm')
        ordering = ['template', 'field_order', 'field_name']

# LabTestVersion
class LabTestVersion(models.Model):
    lab_test = models.ForeignKey(
        'LabTest', 
        on_delete=models.CASCADE,
        related_name='versions',
        verbose_name=_('phiếu xét nghiệm gốc')
    )
    version_number = models.PositiveIntegerField(_('số phiên bản'))
    result_snapshot = models.TextField(_('bản ghi kết quả (snapshot/JSON/PDF link)'), null=True, blank=True)
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
        verbose_name = _('phiên bản phiếu xét nghiệm')
        verbose_name_plural = _('các phiên bản phiếu xét nghiệm')
        ordering = ['lab_test', '-version_number']
        unique_together = ('lab_test', 'version_number')

    def __str__(self):
        return f"Phiên bản {self.version_number} của phiếu XN {self.lab_test_id}"

# LabTest
class LabTest(models.Model):
    class PrintStatus(models.TextChoices):
        PENDING = 'PENDING', _('Chờ xử lý')
        PRINTED = 'PRINTED', _('Đã in')

    medical_record = models.ForeignKey(
        'medical_records.MedicalRecord', # Tham chiếu bằng chuỗi
        on_delete=models.CASCADE,
        related_name='lab_tests',
        verbose_name=_('hồ sơ bệnh án')
    )
    template = models.ForeignKey(
        LabTestTemplate,
        on_delete=models.PROTECT,
        related_name='lab_tests',
        verbose_name=_('mẫu xét nghiệm áp dụng')
    )
    latest_version = models.OneToOneField(
        LabTestVersion, 
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='current_for_lab_test',
        verbose_name=_('phiên bản mới nhất')
    )
    print_status = models.CharField(
        _('trạng thái in'),
        max_length=20,
        choices=PrintStatus.choices,
        default=PrintStatus.PENDING
    )
    last_print_date = models.DateTimeField(_('ngày in sau cùng'), null=True, blank=True)
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='lab_tests_requested',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('người yêu cầu')
    )
    requested_at = models.DateTimeField(_('ngày yêu cầu'), auto_now_add=True)
    results_updated_at = models.DateTimeField(_('kết quả cập nhật lúc'), null=True, blank=True)

    def __str__(self):
        mr_id = self.medical_record.id if self.medical_record else "N/A"
        mr_date_str = self.medical_record.record_date.strftime('%d/%m/%Y') if self.medical_record and self.medical_record.record_date else "N/A"
        template_name = self.template.name if self.template else "N/A"
        return f"Xét nghiệm {template_name} cho HSBA {mr_id} (Ngày: {mr_date_str})"

    class Meta:
        verbose_name = _('phiếu xét nghiệm')
        verbose_name_plural = _('danh sách phiếu xét nghiệm')
        ordering = ['-requested_at']

# LabTestResultValue
class LabTestResultValue(models.Model):
    lab_test = models.ForeignKey(
        LabTest,
        on_delete=models.CASCADE,
        related_name='result_values',
        verbose_name=_('phiếu xét nghiệm liên quan')
    )
    template_field = models.ForeignKey(
        LabTestTemplateField,
        on_delete=models.CASCADE,
        related_name='result_values',
        verbose_name=_('chỉ số xét nghiệm')
    )
    value = models.CharField(_('giá trị kết quả'), max_length=255, null=True, blank=True)
    comment = models.TextField(_('ghi chú/bình luận'), null=True, blank=True)
    entered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='lab_test_values_entered',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        verbose_name=_('người nhập/sửa')
    )
    entered_at = models.DateTimeField(_('thời điểm nhập/sửa'), auto_now=True)

    def __str__(self):
        return f"Kết quả cho '{self.template_field.field_name}' của phiếu XN {self.lab_test_id}: {self.value}"

    class Meta:
        verbose_name = _('giá trị kết quả xét nghiệm')
        verbose_name_plural = _('các giá trị kết quả xét nghiệm')
        unique_together = ('lab_test', 'template_field')
        ordering = ['lab_test', 'template_field__field_order']
