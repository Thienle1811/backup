# seed_group.py (chạy 1 lần)
from django.contrib.auth.models import Group, Permission

agent, _ = Group.objects.get_or_create(name="Agent")
# Cho phép Agent CRUD LabTest và đọc Patient/MedicalRecord
perms = Permission.objects.filter(
    content_type__app_label__in=["labtests", "patients", "medical_records"],
    codename__startswith=("add_", "change_", "view_"),
)
agent.permissions.set(perms)
