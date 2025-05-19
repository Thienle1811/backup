        # apps/accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import Group
from .models import CustomUser
from django.utils.translation import gettext_lazy as _

class CustomUserAdminCreationForm(UserCreationForm):
            class Meta(UserCreationForm.Meta):
                model = CustomUser
                fields = ('email', 'username', 'full_name', 'phone', 'date_of_birth', 
                          'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
                labels = {
                    'email': _('Địa chỉ Email*'),
                    'username': _('Tên đăng nhập (Username)*'),
                    'full_name': _('Họ và tên đầy đủ'),
                    'phone': _('Số điện thoại'),
                    'date_of_birth': _('Ngày sinh'),
                    'is_active': _('Đang hoạt động'),
                    'is_staff': _('Là nhân viên (có thể truy cập admin)'),
                    'is_superuser': _('Là quản trị viên cấp cao (có tất cả quyền)'),
                    'groups': _('Nhóm quyền'),
                    'user_permissions': _('Quyền cụ thể'),
                }
                widgets = {
                    'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                    'email': forms.EmailInput(attrs={'class': 'form-control'}),
                    'username': forms.TextInput(attrs={'class': 'form-control'}),
                    'full_name': forms.TextInput(attrs={'class': 'form-control'}),
                    'phone': forms.TextInput(attrs={'class': 'form-control'}),
                    'groups': forms.SelectMultiple(attrs={'class': 'form-select select2-groups', 'multiple': True}),
                    'user_permissions': forms.SelectMultiple(attrs={'class': 'form-select select2-permissions', 'multiple': True}),
                }

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if CustomUser.USERNAME_FIELD == 'email':
                    self.fields['username'].required = False 
                if 'is_active' in self.fields: self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
                if 'is_staff' in self.fields: self.fields['is_staff'].widget.attrs.update({'class': 'form-check-input'})
                if 'is_superuser' in self.fields: self.fields['is_superuser'].widget.attrs.update({'class': 'form-check-input'})


class CustomUserAdminChangeForm(UserChangeForm):
            password = None 
            class Meta(UserChangeForm.Meta):
                model = CustomUser
                fields = ('email', 'username', 'full_name', 'phone', 'date_of_birth', 
                          'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions',
                          'last_login', 'date_joined')
                labels = {
                    'email': _('Địa chỉ Email*'),
                    'username': _('Tên đăng nhập (Username)*'),
                    'full_name': _('Họ và tên đầy đủ'),
                    'phone': _('Số điện thoại'),
                    'date_of_birth': _('Ngày sinh'),
                    'is_active': _('Đang hoạt động'),
                    'is_staff': _('Là nhân viên (có thể truy cập admin)'),
                    'is_superuser': _('Là quản trị viên cấp cao (có tất cả quyền)'),
                    'groups': _('Nhóm quyền'),
                    'user_permissions': _('Quyền cụ thể'),
                    'last_login': _('Lần đăng nhập cuối'),
                    'date_joined': _('Ngày tham gia'),
                }
                widgets = {
                    'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                    'email': forms.EmailInput(attrs={'class': 'form-control'}),
                    'username': forms.TextInput(attrs={'class': 'form-control'}),
                    'full_name': forms.TextInput(attrs={'class': 'form-control'}),
                    'phone': forms.TextInput(attrs={'class': 'form-control'}),
                    'groups': forms.SelectMultiple(attrs={'class': 'form-select select2-groups', 'multiple': True}),
                    'user_permissions': forms.SelectMultiple(attrs={'class': 'form-select select2-permissions', 'multiple': True}),
                    'last_login': forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': True}),
                    'date_joined': forms.DateTimeInput(attrs={'class': 'form-control', 'readonly': True}),
                }

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if CustomUser.USERNAME_FIELD == 'email': self.fields['username'].required = False
                if 'is_active' in self.fields: self.fields['is_active'].widget.attrs.update({'class': 'form-check-input'})
                if 'is_staff' in self.fields: self.fields['is_staff'].widget.attrs.update({'class': 'form-check-input'})
                if 'is_superuser' in self.fields: self.fields['is_superuser'].widget.attrs.update({'class': 'form-check-input'})
                if 'last_login' in self.fields: self.fields['last_login'].disabled = True
                if 'date_joined' in self.fields: self.fields['date_joined'].disabled = True


class StaffUserCreationForm(UserCreationForm): # Form đơn giản để Admin tạo Nhân viên
            class Meta(UserCreationForm.Meta):
                model = CustomUser
                fields = ('email', 'username', 'full_name', 'phone', 'date_of_birth')
                labels = {
                    'email': _('Địa chỉ Email*'),
                    'username': _('Tên đăng nhập (Username)*'),
                    'full_name': _('Họ và tên đầy đủ'),
                    'phone': _('Số điện thoại'),
                    'date_of_birth': _('Ngày sinh'),
                }
                widgets = {
                    'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
                    'email': forms.EmailInput(attrs={'class': 'form-control'}),
                    'username': forms.TextInput(attrs={'class': 'form-control'}),
                    'full_name': forms.TextInput(attrs={'class': 'form-control'}),
                    'phone': forms.TextInput(attrs={'class': 'form-control'}),
                }

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                if CustomUser.USERNAME_FIELD == 'email':
                    self.fields['username'].required = False

            def save(self, commit=True):
                user = super().save(commit=False)
                user.is_staff = True
                user.is_active = True
                user.is_superuser = False 
                if commit:
                    user.save()
                    try:
                        # Đảm bảo tên nhóm này khớp với tên nhóm bạn đã tạo trong Django Admin
                        staff_group = Group.objects.get(name=_("Nhân viên phòng khám")) 
                        user.groups.add(staff_group)
                    except Group.DoesNotExist:
                        print(f"CẢNH BÁO: Nhóm '{_('Nhân viên phòng khám')}' chưa tồn tại. Vui lòng tạo nhóm này trong Django Admin.")
                        pass
                return user
        