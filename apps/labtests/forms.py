# apps/labtests/forms.py
from django import forms
from django.forms.models import inlineformset_factory
from .models import LabTestTemplate, LabTestTemplateField, LabTest, LabTestResultValue
from django.utils.translation import gettext_lazy as _
from apps.medical_records.models import MedicalRecord

# LabTestTemplateForm và BASE_TEST_TYPES (Dùng để TẠO MẪU XÉT NGHIỆM MỚI, không phải để người dùng chọn khi tạo phiếu)
BASE_TEST_TYPES = [
    ('', '---------'),
    ('HUYET_HOC_TONG_QUAT', _('HUYẾT HỌC (Tổng phân tích tế bào máu)')),
    ('HUYET_HOC_DONG_MAU', _('HUYẾT HỌC (Đông máu)')),
    ('SINH_HOA', _('SINH HÓA')),
    ('MIEN_DICH', _('MIỄN DỊCH')),
    ('NUOC_TIEU', _('NƯỚC TIỂU (Tổng phân tích)')),
]

class LabTestTemplateForm(forms.ModelForm):
    base_template_selector = forms.ChoiceField(
        choices=BASE_TEST_TYPES,
        required=True,
        label=_("Chọn mẫu xét nghiệm cơ sở") + "*",
        widget=forms.Select(attrs={'class': 'form-select mb-4', 'id': 'id_base_template_selector'})
    )
    class Meta:
        model = LabTestTemplate
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ví dụ: Công thức máu (tùy chỉnh)')}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Mô tả chi tiết')}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': _('Tên mẫu xét nghiệm (đặt tên cụ thể)') + "*",
            'description': _('Mô tả'),
            'is_active': _('Đang hoạt động'),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'base_template_selector' in self.fields:
            current_fields = list(self.fields.keys())
            if 'base_template_selector' in current_fields:
                current_fields.remove('base_template_selector')
            new_order = ['base_template_selector'] + current_fields
            self.order_fields(new_order)

LabTestTemplateFieldFormSet = inlineformset_factory(
    LabTestTemplate,
    LabTestTemplateField,
    fields=('field_name', 'result_guidance', 'reference_range_text', 'unit', 'field_order'),
    widgets={
        'field_name': forms.TextInput(attrs={'class': 'form-control form-control-sm field-name-input', 'placeholder': _('Tên chỉ số')}),
        'result_guidance': forms.TextInput(attrs={'class': 'form-control form-control-sm result-guidance-input', 'placeholder': _('Nhập kết quả/hướng dẫn')}),
        'reference_range_text': forms.TextInput(attrs={'class': 'form-control form-control-sm reference-range-text-input', 'placeholder': _('CSBT dạng text')}),
        'unit': forms.TextInput(attrs={'class': 'form-control form-control-sm unit-input', 'placeholder': _('Đơn vị')}),
        'field_order': forms.NumberInput(attrs={'class': 'form-control form-control-sm field-order-input'}),
    },
    labels={
        'field_name': _('Tên xét nghiệm (chỉ số)'), # Sửa label cho rõ hơn
        'result_guidance': _('Kết quả (Hướng dẫn/Mẫu)'),
        'reference_range_text': _('Chỉ số bình thường'),
        'unit': _('Đơn vị'),
        'field_order': _('TT'),
    },
    extra=1,
    can_delete=True,
)

class LabTestForm(forms.ModelForm):
    medical_record = forms.ModelChoiceField(
        queryset=MedicalRecord.objects.select_related('patient').order_by('-record_date', 'patient__full_name'),
        label=_("Hồ sơ bệnh án của bệnh nhân"),
        widget=forms.Select(attrs={'class': 'form-select select2-medical-record'})
    )
    # Đây là trường người dùng sẽ thấy và chọn
    template = forms.ModelChoiceField(
        queryset=LabTestTemplate.objects.filter(is_active=True).order_by('name'),
        label=_("Tên xét nghiệm") + "*",  # <<<< THAY ĐỔI NHÃN Ở ĐÂY
        widget=forms.Select(attrs={'class': 'form-select select2-labtest-template', 'id': 'id_lab_test_template_selector'})
    )
    class Meta:
        model = LabTest
        fields = ['medical_record', 'template'] # 'print_status' đã được bỏ đi

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medical_record'].label_from_instance = lambda obj: f"{obj.patient.full_name} - {_('Khám ngày')}: {obj.record_date.strftime('%d/%m/%Y') if obj.record_date else 'N/A'}"
        # Tên hiển thị trong dropdown "Tên xét nghiệm" sẽ là tên của LabTestTemplate (obj.name)
        self.fields['template'].label_from_instance = lambda obj: obj.name


class LabTestResultValueForm(forms.ModelForm):
    template_field = forms.ModelChoiceField(
        queryset=LabTestTemplateField.objects.all(),
        widget=forms.HiddenInput(),
        required=True
    )
    value = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm result-value-input', 'placeholder': _('Nhập kết quả')})
    )
    comment = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm result-comment-input', 'placeholder': _('Ghi chú (nếu có)')})
    )
    class Meta:
        model = LabTestResultValue
        fields = ['template_field', 'value', 'comment']

LabTestResultValueFormSet = inlineformset_factory(
    LabTest,
    LabTestResultValue,
    form=LabTestResultValueForm,
    extra=0,
    can_delete=True,
)