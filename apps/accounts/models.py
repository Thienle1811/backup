        # apps/accounts/models.py
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
            email = models.EmailField(_('địa chỉ email'), unique=True) # Label cho trường email
            phone = models.CharField(_('số điện thoại'), max_length=20, blank=True, null=True) # Label cho trường số điện thoại
            date_of_birth = models.DateField(_('ngày sinh'), blank=True, null=True) # Label cho trường ngày sinh
            full_name = models.CharField(_('họ và tên đầy đủ'), max_length=255, blank=True, null=True) # Label cho trường họ và tên

            USERNAME_FIELD = 'email'
            REQUIRED_FIELDS = ['username']

            class Meta(AbstractUser.Meta):
                verbose_name = _('người dùng') # Tên hiển thị cho model trong admin
                verbose_name_plural = _('người dùng') # Tên hiển thị số nhiều trong admin
                # db_table = 'auth_user' 

            def __str__(self):
                return self.email

            def get_full_name(self):
                if self.full_name:
                    return self.full_name.strip()
                return super().get_full_name()
            
        # Phần signals giữ nguyên như trước, không cần thay đổi cho việc Việt hóa này
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.http import HttpRequest
        # from apps.activity_logs.models import ActivityLog 

@receiver(user_logged_in)
def log_user_logged_in(sender, request: HttpRequest, user, **kwargs):
            ip_address = None
            user_agent = None
            if request:
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    ip_address = x_forwarded_for.split(',')[0]
                else:
                    ip_address = request.META.get('REMOTE_ADDR')
                user_agent = request.META.get('HTTP_USER_AGENT', '')
            
            # Tạm thời print, sẽ kích hoạt ActivityLog sau
            print(f"Người dùng '{user.email}' đã đăng nhập. IP: {ip_address}, Agent: {user_agent}")
            # try:
            #     from apps.activity_logs.models import ActivityLog
            #     ActivityLog.objects.create(
            #         user=user,
            #         action=ActivityLog.ActionChoices.LOGGED_IN,
            #         details=f"Người dùng '{user.email}' đã đăng nhập thành công.",
            #         ip_address=ip_address,
            #         user_agent=user_agent
            #     )
            # except ImportError:
            #     print("CẢNH BÁO: Model ActivityLog hoặc app chưa được tìm thấy/cấu hình để ghi log đăng nhập.")
            #     pass
        