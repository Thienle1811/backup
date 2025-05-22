from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import gettext_lazy as _


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Tài khoản",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nhập tài khoản",
            }
        ),
        error_messages={
            "required": "Trường này là bắt buộc.",
        },
    )
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nhập mật khẩu",
            }
        ),
        error_messages={
            "required": "Trường này là bắt buộc.",
        },
    )
    error_messages = {
        "invalid_login": "Sai tên đăng nhập hoặc mật khẩu.",
        "inactive": "Tài khoản chưa được kích hoạt.",
    }
