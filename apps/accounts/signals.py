from django.contrib.auth.signals import user_logged_in # Tín hiệu khi người dùng đăng nhập thành công
from django.dispatch import receiver
from django.http import HttpRequest # Để lấy thông tin request nếu có thể
from apps.activity_logs.models import ActivityLog
# from .models import CustomUser # Không cần import CustomUser trực tiếp nếu user được truyền qua signal

# Hàm này sẽ được gọi sau khi một người dùng đăng nhập thành công
@receiver(user_logged_in)
def log_user_logged_in(sender, request: HttpRequest, user, **kwargs):
    """
    Ghi log khi một người dùng đăng nhập thành công.
    """
    ip_address = None
    user_agent = None

    # Cố gắng lấy thông tin IP và User-Agent từ request
    # Lưu ý: request object có thể không luôn luôn có sẵn hoặc đầy đủ thông tin
    # tùy thuộc vào cách tín hiệu được phát đi trong một số trường hợp tùy chỉnh.
    # Tuy nhiên, đối với user_logged_in, request thường có sẵn.
    if request:
        # Lấy địa chỉ IP thực của client
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
        
        user_agent = request.META.get('HTTP_USER_AGENT', '')


    ActivityLog.objects.create(
        user=user, # user là đối tượng CustomUser đã đăng nhập, được truyền bởi signal
        action=ActivityLog.ActionChoices.LOGGED_IN,
        details=f"Người dùng '{user.email}' đã đăng nhập thành công.",
        ip_address=ip_address,
        user_agent=user_agent
        # content_type và object_id có thể để là None vì hành động này không tác động lên đối tượng cụ thể nào khác
    )

# Bạn cũng có thể thêm signal handler cho user_logged_out hoặc user_login_failed nếu muốn
# from django.contrib.auth.signals import user_logged_out, user_login_failed

# @receiver(user_logged_out)
# def log_user_logged_out(sender, request, user, **kwargs):
#     # ... (logic tương tự để ghi log đăng xuất) ...
#     pass

# @receiver(user_login_failed)
# def log_user_login_failed(sender, credentials, request, **kwargs):
#     # ... (logic tương tự để ghi log đăng nhập thất bại) ...
#     # 'credentials' là một dict chứa thông tin đăng nhập đã thử (ví dụ: {'username': 'abc'})
#     # 'user' trong trường hợp này sẽ là None
#     pass
