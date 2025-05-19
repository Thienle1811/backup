            # apps/medical_records/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import MedicalRecord, MedicalRecordVersion # Thêm MedicalRecordVersion nếu bạn muốn tạo version khi cập nhật
from .forms import MedicalRecordForm
from django.db.models import Q, Max
from django.utils import timezone # Cần cho việc tạo version
from django.db import models

@login_required
def medical_record_list(request):
                query = request.GET.get('q', '')
                medical_records_queryset = MedicalRecord.objects.select_related('patient', 'created_by', 'latest_version').all() # Thêm latest_version
                if query:
                    medical_records_queryset = medical_records_queryset.filter(
                        Q(patient__full_name__icontains=query) |
                        Q(diagnosis__icontains=query) |
                        Q(notes__icontains=query)
                    ).distinct()
                medical_records = medical_records_queryset.order_by('-record_date', 'patient__full_name')
                context = {
                    'medical_records': medical_records,
                    'page_title': 'Danh sách Hồ sơ Bệnh án',
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
                            medical_record.updated_by = request.user # Gán cả updated_by khi tạo mới
                        medical_record.save() # Lưu medical_record trước để có ID

                        # Tự động tạo phiên bản đầu tiên
                        MedicalRecordVersion.objects.create(
                            medical_record=medical_record,
                            version_number=1,
                            diagnosis=medical_record.diagnosis,
                            notes=medical_record.notes,
                            changed_by=request.user,
                            change_reason="Hồ sơ ban đầu được tạo."
                        )
                        # Cập nhật latest_version cho medical_record
                        # Cần lấy lại instance vừa tạo version để gán
                        first_version = medical_record.versions.order_by('version_number').first()
                        if first_version:
                            medical_record.latest_version = first_version
                            medical_record.save(update_fields=['latest_version'])


                        messages.success(request, f"Đã thêm hồ sơ bệnh án cho '{medical_record.patient.full_name}' thành công!")
                        return redirect('medical_records:medical_record_list')
                    else:
                        messages.error(request, "Vui lòng sửa các lỗi trong form.")
                else:
                    form = MedicalRecordForm()
                
                context = {
                    'form': form,
                    'page_title': 'Thêm Hồ sơ Bệnh án Mới',
                    'form_title': 'Thông tin Hồ sơ Bệnh án Mới',
                    'submit_button_text': 'Lưu Hồ sơ'
                }
                return render(request, 'medical_records/medical_record_form.html', context)

@login_required
def medical_record_update(request, pk): # pk là ID của hồ sơ cần sửa
                """
                View để cập nhật thông tin của một hồ sơ bệnh án hiện có.
                """
                record_instance = get_object_or_404(MedicalRecord, pk=pk)
                old_diagnosis = record_instance.diagnosis # Lưu lại giá trị cũ để so sánh
                old_notes = record_instance.notes

                if request.method == 'POST':
                    form = MedicalRecordForm(request.POST, instance=record_instance)
                    if form.is_valid():
                        updated_record = form.save(commit=False)
                        if request.user.is_authenticated:
                            updated_record.updated_by = request.user
                        updated_record.save() # Lưu thay đổi của MedicalRecord trước

                        # Kiểm tra xem có thay đổi nào đáng kể để tạo version mới không
                        # (ví dụ: chẩn đoán hoặc ghi chú thay đổi)
                        # Đây là một ví dụ đơn giản, bạn có thể có logic phức tạp hơn
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
                                diagnosis=updated_record.diagnosis, # Dữ liệu mới
                                notes=updated_record.notes,         # Dữ liệu mới
                                changed_by=request.user,
                                change_reason="Thông tin hồ sơ được cập nhật." # Hoặc lý do cụ thể hơn
                                # is_post_print có thể cần logic riêng để xác định
                            )
                            updated_record.latest_version = new_version
                            updated_record.save(update_fields=['latest_version', 'updated_by', 'updated_at'])


                        messages.success(request, f"Đã cập nhật hồ sơ bệnh án cho '{updated_record.patient.full_name}' thành công!")
                        return redirect('medical_records:medical_record_list')
                    else:
                        messages.error(request, "Vui lòng sửa các lỗi trong form.")
                else:
                    form = MedicalRecordForm(instance=record_instance)
                
                context = {
                    'form': form,
                    'page_title': f'Cập nhật Hồ sơ: {record_instance.patient.full_name} - {record_instance.record_date.strftime("%d/%m/%Y")}',
                    'form_title': 'Cập nhật Thông tin Hồ sơ Bệnh án',
                    'submit_button_text': 'Lưu Thay đổi',
                    'medical_record_instance': record_instance 
                }
                return render(request, 'medical_records/medical_record_form.html', context)

@login_required
def medical_record_delete(request, pk):
                """
                View để xóa một hồ sơ bệnh án sau khi xác nhận.
                """
                record_instance = get_object_or_404(MedicalRecord, pk=pk)
                patient_name = record_instance.patient.full_name if record_instance.patient else "Không rõ bệnh nhân"
                record_date_str = record_instance.record_date.strftime("%d/%m/%Y")

                if request.method == 'POST':
                    # Nếu người dùng xác nhận xóa (gửi form POST)
                    record_instance.delete() # Thực hiện xóa
                    messages.success(request, f"Đã xóa hồ sơ bệnh án ngày {record_date_str} của bệnh nhân '{patient_name}' thành công!")
                    return redirect('medical_records:medical_record_list') # Chuyển hướng về danh sách

                # Nếu là GET request, hiển thị trang xác nhận xóa
                context = {
                    'medical_record': record_instance, # Đổi tên context variable cho rõ ràng
                    'page_title': f'Xác nhận Xóa Hồ sơ: {patient_name} - {record_date_str}',
                    'confirm_message': f"Bạn có chắc chắn muốn xóa hồ sơ bệnh án ngày {record_date_str} của bệnh nhân '{patient_name}' không? Hành động này sẽ xóa cả hồ sơ và tất cả các phiên bản của nó. Hành động này không thể hoàn tác."
                }
                return render(request, 'medical_records/medical_record_confirm_delete.html', context)
            