# Example: apps/patients/migrations/000X_populate_existing_ma_benh_nhan.py
import uuid
from django.db import migrations

# Hàm này cần được định nghĩa lại ở đây vì chúng ta không thể import trực tiếp model Patient
# trong giai đoạn migration theo cách thông thường để gọi _generate_ma_benh_nhan.
# Hoặc, nếu model Patient không thay đổi cấu trúc quá nhiều, bạn có thể thử import.
# Để an toàn, chúng ta định nghĩa lại logic tạo mã ở đây.
def _generate_ma_benh_nhan_for_migration():
    random_part = uuid.uuid4().hex[:8].upper()
    return f"BN-{random_part}"

def populate_ma_benh_nhan_values(apps, schema_editor):
    Patient = apps.get_model('patients', 'Patient')
    db_alias = schema_editor.connection.alias
    patients_to_update = list(Patient.objects.using(db_alias).filter(ma_benh_nhan__isnull=True)) # Lấy danh sách trước

    for patient in patients_to_update:
        generated_id = _generate_ma_benh_nhan_for_migration()
        # Đảm bảo mã là duy nhất trong DB và trong danh sách đang cập nhật
        while Patient.objects.using(db_alias).filter(ma_benh_nhan=generated_id).exists() or \
              any(p.ma_benh_nhan == generated_id for p in patients_to_update if p.pk != patient.pk and hasattr(p, 'ma_benh_nhan')):
            generated_id = _generate_ma_benh_nhan_for_migration()
        patient.ma_benh_nhan = generated_id
        # Không gọi patient.save() trực tiếp ở đây vì nó có thể chạy logic save() đầy đủ của model,
        # bao gồm cả việc tạo mã lại. Chúng ta chỉ muốn cập nhật trường này.
        # Tuy nhiên, vì logic tạo mã của bạn đã có trong save() và có kiểm tra .exists(),
        # việc gọi save() có thể vẫn ổn.
        # Để chắc chắn chỉ cập nhật, chúng ta sẽ dùng update().
        # Nhưng vì vòng lặp, save() từng cái một sẽ an toàn hơn cho việc kiểm tra unique.
        # Do đó, gọi save() là chấp nhận được.
        patient.save(using=db_alias) # Gọi save để logic _generate_ma_benh_nhan (nếu cần) và unique check chạy

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0003_patient_ma_benh_nhan'), # !!! THAY THẾ '0003_auto_xxxxxxxx_xxxx' BẰNG TÊN FILE MIGRATION TRƯỚC ĐÓ (file được tạo ở Bước 4)
    ]

    operations = [
        migrations.RunPython(populate_ma_benh_nhan_values, migrations.RunPython.noop),
    ]
