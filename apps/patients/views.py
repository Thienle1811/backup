# apps/patients/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Patient
from .forms import PatientForm
from django.db.models import Q
from django.utils.translation import gettext_lazy as _

@login_required
def patient_list(request):
    query = request.GET.get('q', '')
    patients_queryset = Patient.objects.all()
    if query:
        patients_queryset = patients_queryset.filter(
            Q(ma_benh_nhan__icontains=query) | # Thêm tìm kiếm theo mã bệnh nhân
            Q(full_name__icontains=query) |
            Q(email__icontains=query) |
            Q(phone__icontains=query)
        ).distinct()
    
    # Sắp xếp theo ngày tạo mới nhất hoặc theo tên tùy bạn
    patients = patients_queryset.order_by('-created_at', 'full_name') 
    
    context = {
        'patients': patients,
        'page_title': _('Danh sách Bệnh nhân'),
        'search_query': query,
        'patient_count': patients.count()
    }
    return render(request, 'patients/patient_list.html', context)

@login_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            if request.user.is_authenticated:
                patient.created_by = request.user
            # Mã bệnh nhân sẽ được tạo tự động trong phương thức save() của model
            patient.save() 
            messages.success(request, _("Đã thêm bệnh nhân '{name}' (Mã: {ma_bn}) thành công!").format(name=patient.full_name, ma_bn=patient.ma_benh_nhan))
            return redirect('patients:patient_list')
        else:
            messages.error(request, _("Vui lòng sửa các lỗi trong form."))
    else:
        form = PatientForm()
    
    context = {
        'form': form,
        'page_title': _('Thêm Bệnh nhân Mới'),
        'form_title': _('Thông tin Bệnh nhân Mới'),
        'submit_button_text': _('Lưu Bệnh nhân')
    }
    return render(request, 'patients/patient_form.html', context)

@login_required
def patient_update(request, pk):
    patient_instance = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient_instance)
        if form.is_valid():
            updated_patient = form.save(commit=False)
            if request.user.is_authenticated:
                updated_patient.updated_by = request.user
            updated_patient.save()
            messages.success(request, _("Đã cập nhật thông tin bệnh nhân '{name}' (Mã: {ma_bn}) thành công!").format(name=updated_patient.full_name, ma_bn=updated_patient.ma_benh_nhan))
            return redirect('patients:patient_list')
        else:
            messages.error(request, _("Vui lòng sửa các lỗi trong form."))
    else:
        form = PatientForm(instance=patient_instance)
    
    context = {
        'form': form,
        'page_title': _("Cập nhật Bệnh nhân: {name}").format(name=patient_instance.full_name),
        'form_title': _('Cập nhật Thông tin Bệnh nhân (Mã: {ma_bn})').format(ma_bn=patient_instance.ma_benh_nhan), # Hiển thị mã BN ở tiêu đề form
        'submit_button_text': _('Lưu Thay đổi'),
        'patient_instance': patient_instance # Truyền patient_instance để có thể hiển thị mã BN trong template nếu muốn
    }
    return render(request, 'patients/patient_form.html', context)

@login_required
def patient_delete(request, pk):
    patient_instance = get_object_or_404(Patient, pk=pk)
    patient_name = patient_instance.full_name
    patient_ma = patient_instance.ma_benh_nhan
    if request.method == 'POST':
        patient_instance.delete()
        messages.success(request, _("Đã xóa bệnh nhân '{name}' (Mã: {ma_bn}) thành công!").format(name=patient_name, ma_bn=patient_ma))
        return redirect('patients:patient_list')
    
    context = {
        'patient': patient_instance,
        'page_title': _("Xác nhận Xóa Bệnh nhân: {name}").format(name=patient_name),
        'confirm_message': _("Bạn có chắc chắn muốn xóa bệnh nhân '{name}' (Mã: {ma_bn}) không? Hành động này không thể hoàn tác.").format(name=patient_name, ma_bn=patient_ma)
    }
    return render(request, 'patients/patient_confirm_delete.html', context)
