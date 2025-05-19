        # apps/patients/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Patient
from .forms import PatientForm
from django.db.models import Q # Import Q object để tạo các truy vấn phức tạp (OR)

def patient_list(request):
            """
            View để hiển thị danh sách tất cả bệnh nhân, có hỗ trợ tìm kiếm.
            """
            query = request.GET.get('q', '') # Lấy từ khóa tìm kiếm từ request.GET, mặc định là chuỗi rỗng
            
            # Bắt đầu với tất cả bệnh nhân
            patients_queryset = Patient.objects.all()

            if query:
                # Nếu có từ khóa tìm kiếm, lọc danh sách bệnh nhân
                # Tìm kiếm trong các trường: full_name, email, phone
                # Q objects được dùng để kết hợp các điều kiện tìm kiếm bằng OR
                patients_queryset = patients_queryset.filter(
                    Q(full_name__icontains=query) |  # icontains: không phân biệt chữ hoa/thường
                    Q(email__icontains=query) |
                    Q(phone__icontains=query)
                ).distinct() # distinct() để tránh các kết quả trùng lặp nếu một bệnh nhân khớp nhiều điều kiện

            # Sắp xếp kết quả
            patients = patients_queryset.order_by('full_name')
            
            context = {
                'patients': patients,
                'page_title': 'Danh sách Bệnh nhân',
                'search_query': query, # Truyền lại từ khóa tìm kiếm để hiển thị trong template
                'patient_count': patients.count() # Đếm số lượng bệnh nhân sau khi lọc
            }
            return render(request, 'patients/patient_list.html', context)

        # --- Các views patient_create, patient_update, patient_delete giữ nguyên như trước ---
def patient_create(request):
            if request.method == 'POST':
                form = PatientForm(request.POST)
                if form.is_valid():
                    patient = form.save(commit=False)
                    if request.user.is_authenticated:
                        patient.created_by = request.user
                    patient.save()
                    messages.success(request, f"Đã thêm bệnh nhân '{patient.full_name}' thành công!")
                    return redirect('patients:patient_list')
                else:
                    messages.error(request, "Vui lòng sửa các lỗi trong form.")
            else:
                form = PatientForm()
            
            context = {
                'form': form,
                'page_title': 'Thêm Bệnh nhân Mới',
                'form_title': 'Thông tin Bệnh nhân Mới',
                'submit_button_text': 'Lưu Bệnh nhân'
            }
            return render(request, 'patients/patient_form.html', context)

def patient_update(request, pk):
            patient_instance = get_object_or_404(Patient, pk=pk)
            if request.method == 'POST':
                form = PatientForm(request.POST, instance=patient_instance)
                if form.is_valid():
                    updated_patient = form.save(commit=False)
                    if request.user.is_authenticated:
                        updated_patient.updated_by = request.user
                    updated_patient.save()
                    messages.success(request, f"Đã cập nhật thông tin bệnh nhân '{updated_patient.full_name}' thành công!")
                    return redirect('patients:patient_list')
                else:
                    messages.error(request, "Vui lòng sửa các lỗi trong form.")
            else:
                form = PatientForm(instance=patient_instance)
            
            context = {
                'form': form,
                'page_title': f'Cập nhật Bệnh nhân: {patient_instance.full_name}',
                'form_title': 'Cập nhật Thông tin Bệnh nhân',
                'submit_button_text': 'Lưu Thay đổi',
                'patient_instance': patient_instance
            }
            return render(request, 'patients/patient_form.html', context)

def patient_delete(request, pk):
            patient_instance = get_object_or_404(Patient, pk=pk)
            if request.method == 'POST':
                patient_name = patient_instance.full_name
                patient_instance.delete()
                messages.success(request, f"Đã xóa bệnh nhân '{patient_name}' thành công!")
                return redirect('patients:patient_list')
            context = {
                'patient': patient_instance,
                'page_title': f'Xác nhận Xóa Bệnh nhân: {patient_instance.full_name}',
                'confirm_message': f"Bạn có chắc chắn muốn xóa bệnh nhân '{patient_instance.full_name}' không? Hành động này không thể hoàn tác."
            }
            return render(request, 'patients/patient_confirm_delete.html', context)
        