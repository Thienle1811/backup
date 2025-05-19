        # apps/labtests/forms.py
from django import forms
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from .models import LabTestTemplate, LabTestTemplateField, LabTest, LabTestResultValue # Thêm LabTest, LabTestResultValue
from django.utils.translation import gettext_lazy as _
from apps.medical_records.models import MedicalRecord # Import MedicalRecord

        # LabTestTemplateForm (đã có từ trước)
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
                    'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả chi tiết về mẫu xét nghiệm'}),
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

        # LabTestTemplateFieldFormSet (đã có từ trước)
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

        # ---- MÃ MỚI BẮT ĐẦU TỪ ĐÂY ----

class LabTestForm(forms.ModelForm):
            # Trường medical_record sẽ cho phép chọn từ danh sách các hồ sơ bệnh án
            medical_record = forms.ModelChoiceField(
                queryset=MedicalRecord.objects.select_related('patient').order_by('-record_date', 'patient__full_name'),
                label="Hồ sơ bệnh án của bệnh nhân",
                widget=forms.Select(attrs={'class': 'form-select select2-medical-record'})
            )
            # Trường template sẽ cho phép chọn từ danh sách các mẫu xét nghiệm đang hoạt động
            template = forms.ModelChoiceField(
                queryset=LabTestTemplate.objects.filter(is_active=True).order_by('name'),
                label="Mẫu xét nghiệm áp dụng",
                widget=forms.Select(attrs={'class': 'form-select select2-labtest-template', 'id': 'id_lab_test_template_selector'}) # Thêm ID để JS có thể bắt sự kiện
            )

            class Meta:
                model = LabTest
                fields = ['medical_record', 'template', 'print_status'] # requested_by sẽ được gán tự động trong view
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
                # Tùy chỉnh cách hiển thị cho medical_record để dễ chọn hơn
                self.fields['medical_record'].label_from_instance = lambda obj: f"{obj.patient.full_name} - Khám ngày: {obj.record_date.strftime('%d/%m/%Y')}"


class LabTestResultValueForm(forms.ModelForm):
            """
            Form cho từng dòng kết quả xét nghiệm.
            Sẽ được sử dụng trong FormSet.
            """
            # template_field sẽ được gán tự động hoặc ẩn đi, không cho người dùng chọn trực tiếp trong formset
            # vì nó phụ thuộc vào LabTestTemplate đã chọn.
            class Meta:
                model = LabTestResultValue
                fields = ['template_field', 'value', 'comment']
                widgets = {
                    'template_field': forms.HiddenInput(), # Ẩn trường này đi, sẽ được xử lý bởi view/JS
                    'value': forms.TextInput(attrs={'class': 'form-control form-control-sm result-value-input', 'placeholder': 'Nhập kết quả'}),
                    'comment': forms.TextInput(attrs={'class': 'form-control form-control-sm result-comment-input', 'placeholder': 'Ghi chú (nếu có)'}),
                }
                labels = { # Các label này có thể không cần thiết nếu hiển thị trong bảng
                    'value': 'Kết quả',
                    'comment': 'Bình luận',
                }

        # Base FormSet để có thể tùy chỉnh thêm nếu cần
class BaseLabTestResultValueFormSet(BaseInlineFormSet):
            def __init__(self, *args, **kwargs):
                self.lab_test_template = kwargs.pop('lab_test_template', None)
                super().__init__(*args, **kwargs)
                if self.lab_test_template:
                    # Tự động tạo các form con dựa trên các field của template
                    # Điều này thường được xử lý trong view khi khởi tạo formset lần đầu
                    # hoặc thông qua JavaScript để thêm động.
                    # Ở đây, chúng ta có thể lọc queryset cho template_field nếu cần.
                    for form in self.forms:
                        form.fields['template_field'].queryset = LabTestTemplateField.objects.filter(template=self.lab_test_template)


LabTestResultValueFormSet = inlineformset_factory(
            LabTest, # Model cha
            LabTestResultValue, # Model con (inline)
            form=LabTestResultValueForm, # Sử dụng LabTestResultValueForm tùy chỉnh ở trên
            # fields=('template_field', 'value', 'comment'), # Đã định nghĩa trong LabTestResultValueForm
            formset=BaseLabTestResultValueFormSet, # Sử dụng BaseInlineFormSet tùy chỉnh (tùy chọn)
            extra=0, # Sẽ được điều chỉnh bằng JavaScript dựa trên số lượng field của template
            can_delete=False, # Thường không cho xóa kết quả, chỉ sửa
            # can_order=False,
        )
        