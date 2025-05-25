from django import forms
from .models import Patient

class PatientForm(forms.ModelForm):
    GENDER_CHOICES = [
        ("Male", "Nam"),
        ("Female", "Nữ"),
        ("Other", "Khác"),
    ]
    BLOOD_TYPE_CHOICES = [
        ("A", "A"),
        ("B", "B"),
        ("AB", "AB"),
        ("O", "O"),
    ]

    gender = forms.ChoiceField(
        choices=GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Giới tính",
    )
    date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
        label="Ngày sinh",
    )
    blood_type = forms.ChoiceField(
        choices=BLOOD_TYPE_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
        label="Nhóm máu",
    )

    class Meta:
        model = Patient
        fields = [
            "full_name",
            "phone",
            "date_of_birth",
            "gender",
            "address",
            "referring_doctor",
            "blood_type",
            "allergies",
        ]
        widgets = {
            "full_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Họ tên"}),
            "phone": forms.TextInput(attrs={"class": "form-control", "placeholder": "Số điện thoại"}),
            "address": forms.TextInput(attrs={"class": "form-control", "placeholder": "Địa chỉ"}),
            "referring_doctor": forms.TextInput(attrs={"class": "form-control", "placeholder": "Tên bác sĩ chỉ định"}),
            "allergies": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Dị ứng (nếu có)"}),
        }
        labels = {
            "full_name": "Họ và tên",
            "phone": "Số điện thoại",
            "address": "Địa chỉ",
            "referring_doctor": "Bác sĩ chỉ định",
            "allergies": "Dị ứng",
        }
        help_texts = {
            "allergies": "Liệt kê các loại dị ứng nếu có",
        }
        error_messages = {
            "full_name": {"required": "Trường họ tên không được bỏ trống."},
        }
