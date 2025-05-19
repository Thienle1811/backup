        # apps/appointments/forms.py
from django import forms
from .models import Appointment
from apps.patients.models import Patient
from apps.accounts.models import CustomUser # Hoặc settings.AUTH_USER_MODEL

class AppointmentForm(forms.ModelForm):
            # Tùy chỉnh trường patient
            patient = forms.ModelChoiceField(
                queryset=Patient.objects.all().order_by('full_name'),
                label="Bệnh nhân",
                widget=forms.Select(attrs={'class': 'form-select select2-patient'})
            )
            # Tùy chỉnh trường staff
            staff = forms.ModelChoiceField(
                # Lọc chỉ những user là staff (ví dụ) hoặc thuộc một group cụ thể
                # queryset=CustomUser.objects.filter(is_staff=True).order_by('full_name', 'email'),
                queryset=CustomUser.objects.all().order_by('full_name', 'email'), # Hiện tại lấy tất cả user
                label="Nhân viên (Bác sĩ/KTV)",
                widget=forms.Select(attrs={'class': 'form-select select2-staff'})
            )

            class Meta:
                model = Appointment
                fields = [
                    'patient',
                    'staff',
                    'appointment_date',
                    'appointment_time',
                    'status',
                    'notes',
                    # Các trường 'created_by', 'created_at', 'updated_at'
                    # thường được xử lý tự động.
                ]
                widgets = {
                    'appointment_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
                    'appointment_time': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
                    'status': forms.Select(attrs={'class': 'form-select'}),
                    'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Ghi chú thêm cho lịch hẹn (nếu có)'}),
                }
                labels = {
                    'appointment_date': 'Ngày hẹn',
                    'appointment_time': 'Giờ hẹn',
                    'status': 'Trạng thái',
                    'notes': 'Ghi chú',
                }

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                # Ví dụ: nếu bạn muốn giới hạn danh sách staff chỉ những người có is_staff=True
                # self.fields['staff'].queryset = CustomUser.objects.filter(is_staff=True).order_by('full_name', 'email')
                pass
        