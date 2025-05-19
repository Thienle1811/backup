        # apps/medical_records/forms.py
from django import forms
from .models import MedicalRecord
from apps.patients.models import Patient # Để tùy chỉnh widget cho trường patient

class MedicalRecordForm(forms.ModelForm):
            # Tùy chỉnh trường patient để hiển thị danh sách bệnh nhân dễ chọn hơn
            # Hoặc bạn có thể dùng một widget tìm kiếm nếu danh sách bệnh nhân quá dài
            patient = forms.ModelChoiceField(
                queryset=Patient.objects.all().order_by('full_name'),
                label="Bệnh nhân",
                widget=forms.Select(attrs={'class': 'form-select select2-patient'}) # Thêm class để có thể dùng Select2 nếu muốn
            )

            class Meta:
                model = MedicalRecord
                fields = [
                    'patient',
                    'record_date',
                    'diagnosis',
                    'notes',
                    # Trường 'latest_version' thường được quản lý tự động hoặc không hiển thị trong form tạo/sửa cơ bản.
                    # Các trường 'created_by', 'updated_by', 'created_at', 'updated_at'
                    # cũng được xử lý tự động.
                ]
                widgets = {
                    'record_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                    'diagnosis': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Nhập chẩn đoán của bác sĩ'}),
                    'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ghi chú thêm (nếu có)'}),
                }
                labels = {
                    'patient': 'Bệnh nhân',
                    'record_date': 'Ngày khám',
                    'diagnosis': 'Chẩn đoán',
                    'notes': 'Ghi chú của bác sĩ',
                }

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Nếu bạn muốn lọc danh sách bệnh nhân hoặc làm gì đó đặc biệt khi khởi tạo form
                # Ví dụ: self.fields['patient'].queryset = Patient.objects.filter(is_active=True)
                pass
        