# apps/dashboard/forms.py
from django import forms
from django.utils.translation import gettext_lazy as _
from .models import ClinicSetting # Import model ClinicSetting

class ClinicSettingForm(forms.ModelForm):
    class Meta:
        model = ClinicSetting
        fields = ['name', 'address', 'phone', 'email', 'logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
            'address': forms.Textarea(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'rows': 3}),
            'phone': forms.TextInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
            'email': forms.EmailInput(attrs={'class': 'mt-1 block w-full border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
            'logo': forms.ClearableFileInput(attrs={'class': 'mt-1 block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'}),
        }
        labels = {
            'name': _("Tên phòng khám"),
            'address': _("Địa chỉ"),
            'phone': _("Số điện thoại"),
            'email': _("Email phòng khám"),
            'logo': _("Logo phòng khám"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bạn có thể thêm tùy chỉnh khác cho form ở đây nếu cần
        # Ví dụ: self.fields['logo'].help_text = _("Tải lên logo mới sẽ thay thế logo hiện tại.")
        if self.instance and self.instance.logo:
             self.fields['logo'].help_text = _("Để trống nếu không muốn thay đổi logo hiện tại.")