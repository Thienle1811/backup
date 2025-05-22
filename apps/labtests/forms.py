# apps/labtests/forms.py
from django import forms
from .models import TestItem


class LabTestValueForm(forms.Form):
    value = forms.CharField(
        label="Giá trị",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    comment = forms.CharField(
        label="Ghi chú",
        required=False,
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def __init__(self, *args, item: TestItem = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.item = item
        if item and item.unit:
            self.fields["value"].widget.attrs["placeholder"] = item.unit


def labtest_value_formset(data=None, items=None, initial=None):
    """
    Tạo formset khớp danh sách TestItem, bao gồm management form và initial forms.
    """
    if items is None:
        items = []
    # extra=0 so we only get forms for items
    FormSet = forms.formset_factory(LabTestValueForm, extra=0)
    if initial is None:
        initial = [{} for _ in items]
    formset = FormSet(data=data, initial=initial)
    # Attach item to each form
    for form, item in zip(formset.forms, items):
        if form.is_bound:
            form.__init__(*(form.data,), item=item)
        else:
            form.__init__(item=item)
    return formset
