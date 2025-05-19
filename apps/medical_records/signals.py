from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from apps.activity_logs.models import ActivityLog
from .models import MedicalRecord # Model MedicalRecord của chúng ta

# Hàm này sẽ được gọi sau khi một đối tượng MedicalRecord được lưu
@receiver(post_save, sender=MedicalRecord)
def log_medical_record_saved(sender, instance, created, raw, using, update_fields, **kwargs):
    """
    Ghi log khi một đối tượng MedicalRecord được tạo mới hoặc cập nhật.
    """
    if raw:
        return

    user = None
    action = ActivityLog.ActionChoices.UPDATED
    patient_name = instance.patient.full_name if instance.patient else "Không rõ bệnh nhân"
    details = f"Hồ sơ bệnh án (ID: {instance.pk}) cho bệnh nhân '{patient_name}' ngày {instance.record_date.strftime('%d/%m/%Y')} đã được cập nhật."

    if created:
        action = ActivityLog.ActionChoices.CREATED
        details = f"Hồ sơ bệnh án mới (ID: {instance.pk}) cho bệnh nhân '{patient_name}' ngày {instance.record_date.strftime('%d/%m/%Y')} đã được tạo."
        if instance.created_by:
            user = instance.created_by
    else:
        if instance.updated_by:
            user = instance.updated_by

    try:
        medical_record_content_type = ContentType.objects.get_for_model(instance)
    except Exception:
        medical_record_content_type = None

    if medical_record_content_type:
        ActivityLog.objects.create(
            user=user,
            action=action,
            content_type=medical_record_content_type,
            object_id=instance.pk,
            target_object=instance,
            details=details
        )

# (Tùy chọn) Hàm cho post_delete tương tự như của Patient
# @receiver(post_delete, sender=MedicalRecord)
# def log_medical_record_deleted(sender, instance, using, **kwargs):
#     user = None # Khó xác định user
#     action = ActivityLog.ActionChoices.DELETED
#     patient_name = instance.patient.full_name if instance.patient else "Không rõ bệnh nhân"
#     details = f"Hồ sơ bệnh án (ID: {instance.pk}) cho bệnh nhân '{patient_name}' ngày {instance.record_date.strftime('%d/%m/%Y')} đã bị xóa."
#
#     try:
#         medical_record_content_type = ContentType.objects.get_for_model(instance)
#     except Exception:
#         medical_record_content_type = None
#
#     if medical_record_content_type:
#         ActivityLog.objects.create(
#             user=user,
#             action=action,
#             content_type=medical_record_content_type,
#             object_id=instance.pk,
#             details=details
#         )
