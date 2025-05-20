# apps/medical_records/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import MedicalRecord, MedicalRecordVersion
from .forms import MedicalRecordForm
from django.db.models import Q, Max
from django.utils import timezone
from django.db import models # Thêm models vào đây
from django.utils.translation import gettext_lazy as _ # Thêm gettext_lazy

@login_required
def medical_record_list(request):
    query = request.GET.get('q', '')
    # Đảm bảo select_related 'patient' để truy cập patient.ma_benh_nhan hiệu quả
    medical_records_queryset = MedicalRecord.objects.select_related('patient', 'created_by', 'latest_version').all()
    if query:
        medical_records_queryset = medical_records_queryset.filter(
            Q(patient__full_name__icontains=query) |
            Q(patient__ma_benh_nhan__icontains=query) | # Thêm tìm kiếm theo mã bệnh nhân
            Q(diagnosis__icontains=query) |
            Q(notes__icontains=query)
        ).distinct()
    medical_records = medical_records_queryset.order_by('-record_date', 'patient__full_name')
    context = {
        'medical_records': medical_records,
        'page_title': _('Danh sách Hồ sơ Bệnh án'),
        'search_query': query,
        'record_count': medical_records.count()
    }
    return render(request, 'medical_records/medical_record_list.html', context)

@login_required
def medical_record_create(request):
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            medical_record = form.save(commit=False)
            if request.user.is_authenticated:
                medical_record.created_by = request.user
                medical_record.updated_by = request.user
            medical_record.save()

            # Tự động tạo phiên bản đầu tiên
            # Đảm bảo medical_record đã có patient được gán
            if medical_record.patient:
                first_version = MedicalRecordVersion.objects.create(
                    medical_record=medical_record,
                    version_number=1,
                    diagnosis=medical_record.diagnosis,
                    notes=medical_record.notes,
                    changed_by=request.user,
                    change_reason=_("Hồ sơ ban đầu được tạo.")
                )
                medical_record.latest_version = first_version
                medical_record.save(update_fields=['latest_version'])
                messages.success(request, _("Đã thêm hồ sơ bệnh án cho '{patient_name}' (Mã: {patient_id}) thành công!").format(patient_name=medical_record.patient.full_name, patient_id=medical_record.patient.ma_benh_nhan))
            else:
                # Xử lý trường hợp không có patient (dù form nên validate việc này)
                messages.error(request, _("Không thể tạo hồ sơ bệnh án mà không có thông tin bệnh nhân."))
                # Có thể không cần tạo version nếu không có patient
            return redirect('medical_records:medical_record_list')
        else:
            messages.error(request, _("Vui lòng sửa các lỗi trong form."))
    else:
        form = MedicalRecordForm()
    
    context = {
        'form': form,
        'page_title': _('Thêm Hồ sơ Bệnh án Mới'),
        'form_title': _('Thông tin Hồ sơ Bệnh án Mới'),
        'submit_button_text': _('Lưu Hồ sơ')
    }
    return render(request, 'medical_records/medical_record_form.html', context)

@login_required
def medical_record_update(request, pk):
    record_instance = get_object_or_404(MedicalRecord.objects.select_related('patient'), pk=pk)
    old_diagnosis = record_instance.diagnosis
    old_notes = record_instance.notes

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, instance=record_instance)
        if form.is_valid():
            updated_record = form.save(commit=False)
            if request.user.is_authenticated:
                updated_record.updated_by = request.user
            
            # Kiểm tra xem patient có thay đổi không (dù form này thường không cho đổi patient của record)
            # Nếu cho phép đổi patient, cần xử lý cẩn thận hơn.
            # Hiện tại, giả sử patient không đổi qua form này.
            updated_record.save() 

            significant_change = (
                form.cleaned_data.get('diagnosis') != old_diagnosis or
                form.cleaned_data.get('notes') != old_notes
            )

            if significant_change:
                last_version_number = updated_record.versions.aggregate(max_version=models.Max('version_number'))['max_version'] or 0
                new_version_number = last_version_number + 1
                
                new_version = MedicalRecordVersion.objects.create(
                    medical_record=updated_record,
                    version_number=new_version_number,
                    diagnosis=updated_record.diagnosis,
                    notes=updated_record.notes,
                    changed_by=request.user,
                    change_reason=_("Thông tin hồ sơ được cập nhật.")
                )
                updated_record.latest_version = new_version
                # Chỉ định rõ các trường cần update để tránh ghi đè không mong muốn
                updated_record.save(update_fields=['latest_version', 'diagnosis', 'notes', 'updated_by', 'updated_at'])


            messages.success(request, _("Đã cập nhật hồ sơ bệnh án cho '{patient_name}' (Mã: {patient_id}) thành công!").format(patient_name=updated_record.patient.full_name, patient_id=updated_record.patient.ma_benh_nhan))
            return redirect('medical_records:medical_record_list')
        else:
            messages.error(request, _("Vui lòng sửa các lỗi trong form."))
    else:
        form = MedicalRecordForm(instance=record_instance)
    
    context = {
        'form': form,
        'page_title': _("Cập nhật Hồ sơ: {patient_name} (Mã: {patient_id}) - {record_date}").format(
            patient_name=record_instance.patient.full_name, 
            patient_id=record_instance.patient.ma_benh_nhan,
            record_date=record_instance.record_date.strftime("%d/%m/%Y")
        ),
        'form_title': _('Cập nhật Thông tin Hồ sơ Bệnh án'),
        'submit_button_text': _('Lưu Thay đổi'),
        'medical_record_instance': record_instance 
    }
    return render(request, 'medical_records/medical_record_form.html', context)

@login_required
def medical_record_delete(request, pk):
    record_instance = get_object_or_404(MedicalRecord.objects.select_related('patient'), pk=pk)
    patient_name = record_instance.patient.full_name if record_instance.patient else _("Không rõ bệnh nhân")
    patient_id = record_instance.patient.ma_benh_nhan if record_instance.patient else "N/A"
    record_date_str = record_instance.record_date.strftime("%d/%m/%Y")

    if request.method == 'POST':
        record_instance.delete()
        messages.success(request, _("Đã xóa hồ sơ bệnh án ngày {record_date} của bệnh nhân '{patient_name}' (Mã: {patient_id}) thành công!").format(record_date=record_date_str, patient_name=patient_name, patient_id=patient_id))
        return redirect('medical_records:medical_record_list')

    context = {
        'medical_record': record_instance,
        'page_title': _("Xác nhận Xóa Hồ sơ: {patient_name} (Mã: {patient_id}) - {record_date}").format(
            patient_name=patient_name, 
            patient_id=patient_id,
            record_date=record_date_str
        ),
        'confirm_message': _("Bạn có chắc chắn muốn xóa hồ sơ bệnh án ngày {record_date} của bệnh nhân '{patient_name}' (Mã: {patient_id}) không? Hành động này sẽ xóa cả hồ sơ và tất cả các phiên bản của nó. Hành động này không thể hoàn tác.").format(
            record_date=record_date_str, 
            patient_name=patient_name, 
            patient_id=patient_id
        )
    }
    return render(request, 'medical_records/medical_record_confirm_delete.html', context)
