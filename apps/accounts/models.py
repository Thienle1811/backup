from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _ # Thường dùng cho các chuỗi sẽ hiển thị ra UI

class CustomUser(AbstractUser):
    # AbstractUser đã có các trường: username, first_name, last_name, email,
    # password, groups, user_permissions, is_staff, is_active, is_superuser,
    # last_login, date_joined.

    # Chúng ta muốn dùng email làm trường đăng nhập chính và nó phải là duy nhất.
    email = models.EmailField(_('email address'), unique=True)

    # Các trường bổ sung theo tài liệu Modeling (1).md
    phone = models.CharField(_('phone number'), max_length=20, blank=True, null=True)
    date_of_birth = models.DateField(_('date of birth'), blank=True, null=True)
    # full_name có thể được tạo từ first_name và last_name, hoặc là một trường riêng.
    # Nếu bạn muốn dùng first_name và last_name từ AbstractUser, bạn không cần trường full_name riêng.
    # Nếu bạn muốn một trường full_name riêng, bạn có thể thêm như sau:
    full_name = models.CharField(_('full name'), max_length=255, blank=True, null=True)
    # Hoặc bạn có thể tạo một property để lấy full_name từ first_name và last_name:
    # @property
    # def full_name(self):
    #     return f"{self.first_name} {self.last_name}".strip()

    # Đặt email làm trường định danh để đăng nhập
    USERNAME_FIELD = 'email'

    # Các trường bắt buộc khi tạo user qua lệnh `createsuperuser`
    # (ngoài USERNAME_FIELD và password).
    # `AbstractUser` yêu cầu `username` theo mặc định.
    # Nếu bạn vẫn giữ trường `username` (mặc dù đăng nhập bằng email),
    # thì `username` vẫn cần thiết và nên là unique.
    # Nếu bạn muốn loại bỏ hoàn toàn `username`, bạn cần phải ghi đè nhiều hơn.
    # Để đơn giản, chúng ta vẫn giữ `username` và yêu cầu nó khi tạo superuser.
    REQUIRED_FIELDS = ['username'] # Bạn có thể thêm 'first_name', 'last_name' nếu muốn chúng bắt buộc

    def __str__(self):
        return self.email # Hiển thị email khi đối tượng User được gọi dưới dạng chuỗi

    # Bạn có thể thêm các phương thức tùy chỉnh khác cho model ở đây nếu cần.
