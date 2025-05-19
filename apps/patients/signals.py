from django.db.models.signals import post_save, post_delete # Import các tín hiệu cần thiết
from django.dispatch import receiver # Decorator để kết nối hàm với tín hiệu
from django.contrib.contenttypes.models import ContentType
from apps.accounts.models import CustomUser # Để kiểm tra kiểu của user
from apps.activity_logs.models import ActivityLog # Model để ghi log
from .models import Patient # Model Patient của chúng ta

# Hàm này sẽ được gọi sau khi một đối tượng Patient được lưu
@receiver(post_save, sender=Patient)
def log_patient_saved(sender, instance, created, raw, using, update_fields, **kwargs):
    """
    Ghi log khi một đối tượng Patient được tạo mới hoặc cập nhật.
    """
    # Bỏ qua nếu đây là việc load dữ liệu thô (raw fixture loading)
    if raw:
        return

    user = None
    action = ActivityLog.ActionChoices.UPDATED
    details = f"Thông tin bệnh nhân '{instance.full_name}' (ID: {instance.pk}) đã được cập nhật."

    if created:
        action = ActivityLog.ActionChoices.CREATED
        details = f"Bệnh nhân mới '{instance.full_name}' (ID: {instance.pk}) đã được tạo."
        if instance.created_by:
            user = instance.created_by
    else:
        # Nếu là cập nhật, cố gắng lấy người cập nhật
        if instance.updated_by:
            user = instance.updated_by

    # Lấy ContentType của model Patient
    try:
        patient_content_type = ContentType.objects.get_for_model(instance)
    except Exception: # Xử lý trường hợp ContentType chưa sẵn sàng (hiếm khi xảy ra ở đây)
        patient_content_type = None

    if patient_content_type:
        ActivityLog.objects.create(
            user=user,
            action=action,
            content_type=patient_content_type,
            object_id=instance.pk,
            target_object=instance, # Gán trực tiếp đối tượng
            details=details
            # ip_address và user_agent sẽ cần lấy từ request nếu có,
            # điều này phức tạp hơn khi dùng model signals.
            # Hiện tại chúng ta bỏ qua chúng.
        )

# (Tùy chọn) Hàm này sẽ được gọi sau khi một đối tượng Patient bị xóa
# @receiver(post_delete, sender=Patient)
# def log_patient_deleted(sender, instance, using, **kwargs):
#     """
#     Ghi log khi một đối tượng Patient bị xóa.
#     Lưu ý: Việc lấy 'user' đã thực hiện hành động xóa trong post_delete signal
#     thường khó khăn hơn vì không có request object trực tiếp.
#     Bạn có thể cần một giải pháp phức tạp hơn như middleware hoặc truyền user qua context.
#     """
#     user = None # Khó xác định user ở đây một cách đơn giản
#     action = ActivityLog.ActionChoices.DELETED
#     details = f"Bệnh nhân '{instance.full_name}' (ID: {instance.pk}) đã bị xóa."

#     try:
#         patient_content_type = ContentType.objects.get_for_model(instance)
#     except Exception:
#         patient_content_type = None

#     if patient_content_type:
#         ActivityLog.objects.create(
#             user=user, # Sẽ là None trong trường hợp này
#             action=action,
#             content_type=patient_content_type,
#             object_id=instance.pk,
#             # target_object sẽ không còn tồn tại sau khi xóa,
#             # nên chúng ta không gán nó ở đây.
#             # ContentType và object_id vẫn được lưu để biết đối tượng nào đã bị xóa.
#             details=details
#         )
