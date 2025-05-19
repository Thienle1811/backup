from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from apps.activity_logs.models import ActivityLog
from .models import Appointment # Model Appointment của chúng ta

        # Hàm này sẽ được gọi sau khi một đối tượng Appointment được lưu
@receiver(post_save, sender=Appointment)
def log_appointment_saved(sender, instance, created, raw, using, update_fields, **kwargs):
            """
            Ghi log khi một đối tượng Appointment được tạo mới hoặc cập nhật.
            """
            if raw:
                return

            user = None # Người thực hiện hành động này có thể là người tạo lịch hẹn (created_by)
                        # hoặc người dùng hiện tại nếu cập nhật trạng thái qua một view.
                        # Hiện tại, chúng ta sẽ thử lấy từ created_by hoặc updated_by (nếu có)
            action = ActivityLog.ActionChoices.UPDATED
            
            patient_name = instance.patient.full_name if instance.patient else "Không rõ bệnh nhân"
            staff_name = instance.staff.get_full_name() if instance.staff else "Chưa gán nhân viên"
            appointment_datetime_str = f"{instance.appointment_date.strftime('%d/%m/%Y')}"
            if instance.appointment_time:
                appointment_datetime_str += f" {instance.appointment_time.strftime('%H:%M')}"

            details = f"Lịch hẹn (ID: {instance.pk}) cho '{patient_name}' với '{staff_name}' vào {appointment_datetime_str} đã được cập nhật trạng thái thành '{instance.get_status_display()}'."

            if created:
                action = ActivityLog.ActionChoices.CREATED
                details = f"Lịch hẹn mới (ID: {instance.pk}) cho '{patient_name}' với '{staff_name}' vào {appointment_datetime_str} đã được tạo (Trạng thái: {instance.get_status_display()})."
                if instance.created_by: # Giả sử created_by được gán khi tạo lịch hẹn
                    user = instance.created_by
            else:
                # Nếu là cập nhật, chúng ta cần một cách để biết ai đã cập nhật.
                # Model Appointment hiện tại chưa có trường 'updated_by'.
                # Nếu bạn muốn theo dõi người cập nhật, bạn cần thêm trường đó vào model Appointment
                # và gán giá trị cho nó trong view hoặc admin.
                # Tạm thời, nếu không phải tạo mới, user có thể là None hoặc người tạo ban đầu.
                if hasattr(instance, 'updated_by') and instance.updated_by:
                     user = instance.updated_by
                elif instance.created_by: # Mặc định lấy người tạo nếu không có người cập nhật
                    user = instance.created_by


            try:
                appointment_content_type = ContentType.objects.get_for_model(instance)
            except Exception:
                appointment_content_type = None

            if appointment_content_type:
                ActivityLog.objects.create(
                    user=user,
                    action=action,
                    content_type=appointment_content_type,
                    object_id=instance.pk,
                    target_object=instance,
                    details=details
                )

        # (Tùy chọn) Hàm cho post_delete tương tự
        # @receiver(post_delete, sender=Appointment)
        # def log_appointment_deleted(sender, instance, using, **kwargs):
        #     # ... logic tương tự ...
        #     pass
        