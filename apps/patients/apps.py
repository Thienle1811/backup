from django.apps import AppConfig

class PatientsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.patients' # Dòng này bạn đã có và đã sửa đúng

    # Bạn sẽ thêm phương thức ready() này vào:
    def ready(self):
        # Import signals ở đây để đảm bảo chúng được đăng ký khi Django khởi động
        # và sẵn sàng nhận tín hiệu.
        # Khi Django nạp app 'patients', nó sẽ gọi phương thức ready(),
        # và dòng import này sẽ làm cho các @receiver trong signals.py được thực thi,
        # từ đó kết nối các hàm nhận với các tín hiệu tương ứng.
        try:
            import apps.patients.signals # Hoặc bạn có thể dùng: from . import signals
        except ImportError:
            # Dòng này để xử lý trường hợp nếu có lỗi khi import signals
            # (ví dụ: trong một số trường hợp khi tệp signals.py chưa được tạo hoàn chỉnh)
            # nhưng trong trường hợp của chúng ta, tệp signals.py đã được tạo.
            pass
