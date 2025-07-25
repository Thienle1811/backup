# Generated by Django 5.2.1 on 2025-05-23 04:17

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('patients', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='MedicalRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('record_date', models.DateField(default=django.utils.timezone.now, verbose_name='Ngày khám')),
                ('symptoms', models.TextField(verbose_name='Triệu chứng')),
                ('diagnosis', models.TextField(verbose_name='Chẩn đoán')),
                ('treatment_plan', models.TextField(verbose_name='Kế hoạch điều trị')),
                ('notes', models.TextField(blank=True, verbose_name='Ghi chú')),
                ('is_completed', models.BooleanField(default=False, verbose_name='Đã hoàn thành')),
                ('latest_version', models.PositiveIntegerField(default=1, verbose_name='Phiên bản mới nhất')),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='medical_records_created', to=settings.AUTH_USER_MODEL, verbose_name='Người tạo')),
                ('doctor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_records', to=settings.AUTH_USER_MODEL, verbose_name='Bác sĩ')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='medical_records', to='patients.patient', verbose_name='Bệnh nhân')),
                ('updated_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='medical_records_updated', to=settings.AUTH_USER_MODEL, verbose_name='Người cập nhật')),
            ],
            options={
                'verbose_name': 'Phiếu khám',
                'verbose_name_plural': 'Danh sách phiếu khám',
                'ordering': ('-record_date',),
            },
        ),
        migrations.CreateModel(
            name='Prescription',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('medical_record', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='prescription', to='medical_records.medicalrecord')),
            ],
            options={
                'verbose_name': 'Đơn thuốc',
                'verbose_name_plural': 'Đơn thuốc',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='PrescriptionItem',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine_name', models.CharField(max_length=200, verbose_name='Tên thuốc')),
                ('dosage', models.CharField(max_length=100, verbose_name='Liều dùng')),
                ('frequency', models.CharField(max_length=100, verbose_name='Tần suất')),
                ('duration', models.CharField(max_length=100, verbose_name='Thời gian')),
                ('notes', models.TextField(blank=True, verbose_name='Ghi chú')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('prescription', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='medical_records.prescription')),
            ],
            options={
                'verbose_name': 'Chi tiết đơn thuốc',
                'verbose_name_plural': 'Chi tiết đơn thuốc',
                'ordering': ['created_at'],
            },
        ),
        migrations.CreateModel(
            name='MedicalRecordVersion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Ngày tạo')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Ngày cập nhật')),
                ('version_number', models.PositiveIntegerField(verbose_name='Phiên bản')),
                ('change_reason', models.TextField(blank=True, verbose_name='Lý do thay đổi')),
                ('is_post_print', models.BooleanField(default=False, verbose_name='Sửa sau in')),
                ('changed_at', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Thời gian thay đổi')),
                ('diagnosis', models.TextField(blank=True, verbose_name='Chẩn đoán')),
                ('notes', models.TextField(blank=True, verbose_name='Ghi chú')),
                ('changed_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Người thực hiện')),
                ('medical_record', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='versions', to='medical_records.medicalrecord', verbose_name='Bệnh án')),
            ],
            options={
                'verbose_name': 'Phiên bản bệnh án',
                'verbose_name_plural': 'Danh sách phiên bản bệnh án',
                'ordering': ('-version_number',),
                'abstract': False,
                'unique_together': {('medical_record', 'version_number')},
            },
        ),
    ]
