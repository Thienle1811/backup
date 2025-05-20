# apps/patients/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from apps.activity_logs.models import ActivityLog # Model để ghi log
from .models import Patient # Model Patient của chúng ta

# Import cho chức năng tự động tạo MedicalRecord
from apps.medical_records.models import MedicalRecord, MedicalRecordVersion
from django.utils import timezone

# --- Ghi log hoạt động cho Patient (Giữ lại nếu bạn đã có) ---
@receiver(post_save, sender=Patient)
def log_patient_saved(sender, instance, created, raw, using, update_fields, **kwargs):
    """
    Ghi log khi một đối tượng Patient được tạo mới hoặc cập nhật.
    """
    if raw: # Bỏ qua nếu đây là việc load dữ liệu thô
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
        if instance.updated_by: # Nếu là cập nhật, cố gắng lấy người cập nhật
            user = instance.updated_by

    try:
        patient_content_type = ContentType.objects.get_for_model(instance)
    except Exception:
        patient_content_type = None

    if patient_content_type:
        ActivityLog.objects.create(
            user=user,
            action=action,
            content_type=patient_content_type,
            object_id=instance.pk,
            target_object=instance,
            details=details
        )

# (Tùy chọn) Ghi log khi Patient bị xóa (Giữ lại nếu bạn đã có)
# @receiver(post_delete, sender=Patient)
# def log_patient_deleted(sender, instance, using, **kwargs):
#     # ... (Code ghi log xóa của bạn ở đây) ...
#     pass

# --- Tự động tạo MedicalRecord cho Patient mới ---
@receiver(post_save, sender=Patient)
def create_initial_medical_record_for_new_patient(sender, instance, created, **kwargs):
    """
    Tự động tạo một MedicalRecord và MedicalRecordVersion ban đầu
    khi một Patient mới được tạo.
    """
    if created: # Chỉ thực hiện khi đối tượng Patient được tạo mới
        # Tạo MedicalRecord
        medical_record_instance = MedicalRecord.objects.create(
            patient=instance,
            record_date=instance.created_at.date(), # Sử dụng ngày tạo bệnh nhân làm ngày khám ban đầu
            created_by=instance.created_by,    # Gán người tạo nếu có
            updated_by=instance.created_by     # Gán người cập nhật nếu có
            # diagnosis và notes sẽ để trống theo mặc định của model
        )

        # Tạo MedicalRecordVersion đầu tiên cho MedicalRecord vừa tạo
        first_version = MedicalRecordVersion.objects.create(
            medical_record=medical_record_instance,
            version_number=1,
            diagnosis=medical_record_instance.diagnosis, # Sẽ là None hoặc chuỗi rỗng
            notes=medical_record_instance.notes,           # Sẽ là None hoặc chuỗi rỗng
            changed_by=instance.created_by,      # Người thay đổi là người tạo bệnh nhân
            change_reason="Hồ sơ bệnh án ban đầu được tạo tự động khi tạo bệnh nhân."
        )
        
        # Cập nhật trường latest_version của MedicalRecord
        medical_record_instance.latest_version = first_version
        medical_record_instance.save(update_fields=['latest_version'])