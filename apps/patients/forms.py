# apps/patients/forms.py
from django import forms
from .models import Patient
from django.utils.translation import gettext_lazy as _

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            # 'ma_benh_nhan', # XÓA dòng này nếu có, vì nó sẽ được tạo tự động
            'full_name',
            'date_of_birth',
            'gender',
            'phone',
            'address',
            'email',
            'blood_type',
            'allergies',
        ]
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nhập họ và tên')}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nhập số điện thoại')}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Nhập địa chỉ')}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': _('Nhập địa chỉ email')}),
            'blood_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('Ví dụ: A+, O-')}),
            'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': _('Mô tả các dị ứng (nếu có)')}),
        }
        labels = {
            'full_name': _('Họ và tên'),
            'date_of_birth': _('Ngày sinh'),
            'gender': _('Giới tính'),
            'phone': _('Số điện thoại'),
            'address': _('Địa chỉ'),
            'email': _('Địa chỉ Email'),
            'blood_type': _('Nhóm máu'),
            'allergies': _('Dị ứng'),
        }
