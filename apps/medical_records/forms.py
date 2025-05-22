# ───────────────────────── apps/medical_records/forms.py ─────────────────────
from django import forms
from .models import MedicalRecord
from apps.labtests.models import LabTest


class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ["record_date", "diagnosis", "notes"]
        widgets = {
            "record_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "diagnosis": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
        labels = {
            "record_date": "Ngày khám",
            "diagnosis": "Chẩn đoán",
            "notes": "Ghi chú",
        }


class AttachLabTestForm(forms.Form):
    labtests = forms.ModelMultipleChoiceField(
        queryset=LabTest.objects.none(),  # fill in __init__
        widget=forms.CheckboxSelectMultiple,
        label="Chọn phiếu xét nghiệm để gắn",
    )

    def __init__(self, *args, patient=None, **kwargs):
        super().__init__(*args, **kwargs)
        if patient:
            qs = (
                LabTest.objects
                .filter(patient=patient, medical_record__isnull=True)
                .order_by("-created_at")
            )
            self.fields["labtests"].queryset = qs
            # ➊  tùy biến label
            self.fields["labtests"].label_from_instance = (
                lambda obj: f"{obj.category.name} · {obj.created_at:%d/%m/%Y %H:%M} · ID#{obj.id}"
            )
