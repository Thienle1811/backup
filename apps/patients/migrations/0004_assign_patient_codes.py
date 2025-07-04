# Generated by Django 5.2.1 on 2025-05-25 09:14

from django.db import migrations

def assign_patient_codes(apps, schema_editor):
    Patient = apps.get_model('patients', 'Patient')
    patients = Patient.objects.all().order_by('id')
    for idx, patient in enumerate(patients, start=1):
        code = str(idx).zfill(8)
        patient.patient_code = code
        patient.save(update_fields=['patient_code'])

class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0003_remove_patient_email_patient_patient_code_and_more'),
    ]

    operations = [
        migrations.RunPython(assign_patient_codes, reverse_code=migrations.RunPython.noop),
    ]
