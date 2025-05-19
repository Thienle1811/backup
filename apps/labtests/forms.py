# apps/labtests/forms.py
from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from .models import LabTestTemplate, LabTestTemplateField, LabTest, LabTestResultValue
from django.utils.translation import gettext_lazy as _
from apps.medical_records.models import MedicalRecord
from django.contrib.auth import get_user_model

CustomUser = get_user_model() # Sử dụng get_user_model()

# LabTestTemplateForm và BASE_TEST_TYPES (giữ nguyên như trước)
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
        label="Chọn mẫu xét nghiệm cơ sở*",
        widget=forms.Select(attrs={'class': 'form-select mb-4', 'id': 'id_base_template_selector'})
    )
    class Meta:
        model = LabTestTemplate
        fields = ['name', 'description', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: Công thức máu (tùy chỉnh)'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả chi tiết'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'name': 'Tên mẫu xét nghiệm (đặt tên cụ thể)*',
            'description': 'Mô tả',
            'is_active': 'Đang hoạt động',
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
        'field_name': forms.TextInput(attrs={'class': 'form-control form-control-sm field-name-input', 'placeholder': 'Tên chỉ số'}),
        'result_guidance': forms.TextInput(attrs={'class': 'form-control form-control-sm result-guidance-input', 'placeholder': 'Nhập kết quả/hướng dẫn'}),
        'reference_range_text': forms.TextInput(attrs={'class': 'form-control form-control-sm reference-range-text-input', 'placeholder': 'CSBT dạng text'}),
        'unit': forms.TextInput(attrs={'class': 'form-control form-control-sm unit-input', 'placeholder': 'Đơn vị'}),
        'field_order': forms.NumberInput(attrs={'class': 'form-control form-control-sm field-order-input'}),
    },
    labels={
        'field_name': 'Tên xét nghiệm',
        'result_guidance': 'Kết quả (Hướng dẫn/Mẫu)',
        'reference_range_text': 'Chỉ số bình thường',
        'unit': 'Đơn vị',
        'field_order': 'TT',
    },
    extra=1,
    can_delete=True,
)

class LabTestForm(forms.ModelForm):
    medical_record = forms.ModelChoiceField(
        queryset=MedicalRecord.objects.select_related('patient').order_by('-record_date', 'patient__full_name'),
        label="Hồ sơ bệnh án của bệnh nhân",
        widget=forms.Select(attrs={'class': 'form-select select2-medical-record'})
    )
    template = forms.ModelChoiceField(
        queryset=LabTestTemplate.objects.filter(is_active=True).order_by('name'),
        label="Mẫu xét nghiệm áp dụng",
        widget=forms.Select(attrs={'class': 'form-select select2-labtest-template', 'id': 'id_lab_test_template_selector'})
    )
    class Meta:
        model = LabTest
        fields = ['medical_record', 'template', 'print_status']
        widgets = {
            'print_status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'medical_record': 'Hồ sơ Bệnh án (Bệnh nhân - Ngày khám)',
            'template': 'Mẫu Xét nghiệm Áp dụng',
            'print_status': 'Trạng thái In',
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['medical_record'].label_from_instance = lambda obj: f"{obj.patient.full_name} - Khám ngày: {obj.record_date.strftime('%d/%m/%Y')}"

class LabTestResultValueForm(forms.ModelForm):
    # template_field sẽ được JavaScript điền vào hidden input.
    # Chúng ta cần đảm bảo nó được xử lý đúng.
    template_field = forms.ModelChoiceField(
        queryset=LabTestTemplateField.objects.all(), # Queryset có thể rỗng ban đầu
        widget=forms.HiddenInput(),
        required=True # Quan trọng: template_field phải có để lưu kết quả
    )
    value = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm result-value-input', 'placeholder': 'Nhập kết quả'})
    )
    comment = forms.CharField(
        required=False, 
        widget=forms.TextInput(attrs={'class': 'form-control form-control-sm result-comment-input', 'placeholder': 'Ghi chú (nếu có)'})
    )
    class Meta:
        model = LabTestResultValue
        fields = ['template_field', 'value', 'comment']
        # Widgets cho value và comment đã được khai báo ở trên

LabTestResultValueFormSet = inlineformset_factory(
    LabTest, 
    LabTestResultValue, 
    form=LabTestResultValueForm, 
    extra=0, 
    can_delete=True, # Cho phép xóa các dòng kết quả khi sửa
)
