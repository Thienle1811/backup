# apps/labtests/models.py
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError

# LabTestTemplate (Giữ nguyên)
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

# LabTestTemplateField (Giữ nguyên)
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
    normal_min = models.DecimalField(_('giá trị bình thường (min)'), max_digits=10, decimal_places=2, null=True, blank=True)
    normal_max = models.DecimalField(_('giá trị bình thường (max)'), max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.template.name} - {self.field_name}"

    class Meta:
        verbose_name = _('chỉ số của mẫu xét nghiệm')
        verbose_name_plural = _('các chỉ số của mẫu xét nghiệm')
        ordering = ['template', 'field_order', 'field_name']

# LabTestVersion (Giữ nguyên)
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


# LabTest (CẬP NHẬT _generate_custom_id và save)
class LabTest(models.Model):
    class PrintStatus(models.TextChoices):
        PENDING = 'PENDING', _('Chờ xử lý')
        PRINTED = 'PRINTED', _('Đã in')

    custom_id = models.CharField(
        _('ID Phiếu Xét nghiệm'),
        max_length=50,
        unique=True,
        editable=False,
        blank=True # Sẽ được tạo tự động
    )
    medical_record = models.ForeignKey(
        'medical_records.MedicalRecord',
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

    def _generate_custom_id(self):
        if not (self.medical_record and self.medical_record.patient and self.medical_record.patient.ma_benh_nhan):
            return None # Không thể tạo ID nếu thiếu thông tin

        patient_ma_bn = self.medical_record.patient.ma_benh_nhan
        
        # Tìm số thứ tự lớn nhất hiện tại của các phiếu có custom_id đúng định dạng cho bệnh nhân này
        # Loại trừ chính phiếu hiện tại nếu nó đã có PK (trường hợp update một phiếu chưa có custom_id)
        queryset = LabTest.objects.filter(
            medical_record__patient_id=self.medical_record.patient_id, # Lọc theo patient_id để chính xác hơn
            custom_id__startswith=f"{patient_ma_bn}-"
        )
        if self.pk:
            queryset = queryset.exclude(pk=self.pk)
        
        current_max_seq = 0
        for test in queryset.only('custom_id'): # Chỉ lấy trường custom_id để tối ưu
            if test.custom_id: # Đảm bảo custom_id không rỗng
                try:
                    seq_part_str = test.custom_id.split('-')[-1]
                    seq = int(seq_part_str)
                    if seq > current_max_seq:
                        current_max_seq = seq
                except (ValueError, IndexError):
                    # Bỏ qua các custom_id không đúng định dạng
                    continue
        
        next_sequence = current_max_seq + 1
        
        generated_id_candidate = f"{patient_ma_bn}-{next_sequence}"
        
        # Vòng lặp đảm bảo tính duy nhất
        check_uniqueness_qs_base = LabTest.objects.filter(custom_id=generated_id_candidate)
        if self.pk:
            check_uniqueness_qs_base = check_uniqueness_qs_base.exclude(pk=self.pk)

        safety_counter = 0
        while check_uniqueness_qs_base.exists(): # Kiểm tra lại với queryset đã cập nhật
            safety_counter += 1
            next_sequence += 1
            generated_id_candidate = f"{patient_ma_bn}-{next_sequence}"
            
            # Cập nhật lại queryset kiểm tra unique cho mỗi lần lặp
            check_uniqueness_qs_base = LabTest.objects.filter(custom_id=generated_id_candidate)
            if self.pk:
                check_uniqueness_qs_base = check_uniqueness_qs_base.exclude(pk=self.pk)

            if safety_counter > 100:
                # Ghi log hoặc raise lỗi nếu không thể tạo ID duy nhất
                # (Ví dụ: có quá nhiều phiếu hoặc có lỗi logic không mong muốn)
                # Đây là một biện pháp an toàn để tránh vòng lặp vô hạn.
                # Trong thực tế, với logic đúng, trường hợp này rất hiếm.
                timestamp_fallback = timezone.now().strftime('%Y%m%d%H%M%S%f')
                return f"{patient_ma_bn}-ERR-{timestamp_fallback}" # ID dự phòng
        return generated_id_candidate

    def save(self, *args, **kwargs):
        if not self.custom_id: 
            if self.medical_record and self.medical_record.patient and self.medical_record.patient.ma_benh_nhan:
                generated_id = self._generate_custom_id()
                if generated_id: # Chỉ gán nếu ID được tạo thành công
                    self.custom_id = generated_id
                # else: custom_id sẽ vẫn là blank, có thể cần xử lý thêm nếu custom_id là bắt buộc
            # else:
                # Nếu không có medical_record, custom_id sẽ không được tạo.
                # Điều này nên được validate ở form hoặc view.
                # Nếu đến đây mà medical_record vẫn None, custom_id sẽ là blank.
                pass
        super().save(*args, **kwargs)


    def __str__(self):
        display_id = self.custom_id if self.custom_id else f"#{self.pk}"
        patient_name = self.medical_record.patient.full_name if self.medical_record and self.medical_record.patient else _("Không rõ BN")
        template_name = self.template.name if self.template else _("Không rõ mẫu")
        return f"Phiếu XN {display_id} ({template_name}) cho {patient_name}"

    class Meta:
        verbose_name = _('phiếu xét nghiệm')
        verbose_name_plural = _('danh sách phiếu xét nghiệm')
        ordering = ['-requested_at']

# LabTestResultValue (Giữ nguyên)
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
        lab_test_display = self.lab_test.custom_id if self.lab_test and self.lab_test.custom_id else f"#{self.lab_test_id}"
        return f"Kết quả cho '{self.template_field.field_name}' của phiếu XN {lab_test_display}: {self.value}"

    class Meta:
        verbose_name = _('giá trị kết quả xét nghiệm')
        verbose_name_plural = _('các giá trị kết quả xét nghiệm')
        unique_together = ('lab_test', 'template_field')
        ordering = ['lab_test', 'template_field__field_order']
