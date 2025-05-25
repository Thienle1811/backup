# 📄 apps/labtests/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.urls import reverse
from django.http import FileResponse
import os
import tempfile
import shutil

from apps.patients.models import Patient
from .models import TestCategory, LabTest, LabTestResultValue
from .forms import labtest_value_formset
from apps.activity_logs.models import log_activity
from .utils import export_labtest_to_word


# 1️⃣ Tìm bệnh nhân
@login_required
@permission_required("labtests.add_labtest", raise_exception=True)
def select_patient(request):
    q = request.GET.get("q", "").strip()
    qs = Patient.objects.filter(full_name__icontains=q) if q else Patient.objects.none()
    page_obj = Paginator(qs, 15).get_page(request.GET.get("page"))
    return render(
        request, "labtests/select_patient.html", {"page_obj": page_obj, "q": q}
    )


# 2️⃣ Chọn loại xét nghiệm
@login_required
@permission_required("labtests.add_labtest", raise_exception=True)
def select_category(request, patient_id):
    categories = TestCategory.objects.filter(is_active=True).order_by("name")
    if request.method == "POST":
        selected_categories = request.POST.getlist("categories")
        if selected_categories:
            patient = get_object_or_404(Patient, pk=patient_id)
            for category_id in selected_categories:
                category = get_object_or_404(TestCategory, pk=category_id)
                labtest = LabTest.objects.create(
                    patient=patient,
                    category=category,
                    created_by=request.user,
                )
                log_activity(request.user, labtest, "create", "Tạo phiếu xét nghiệm")
            messages.success(request, "Đã lưu phiếu xét nghiệm thành công!")
            return redirect("labtests:list")
    return render(
        request,
        "labtests/select_category.html",
        {"categories": categories, "patient_id": patient_id},
    )


# 3️⃣ Nhập giá trị
@login_required
@permission_required("labtests.add_labtest", raise_exception=True)
def fill_values(request, patient_id, category_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    category = get_object_or_404(TestCategory, pk=category_id)
    items = list(category.items.order_by("order"))

    formset = labtest_value_formset(request.POST or None, items=items)
    if request.method == "POST" and formset.is_valid():
        labtest = LabTest.objects.create(
            patient=patient,
            category=category,
            created_by=request.user,
        )
        values = []
        for form, item in zip(formset.forms, items):
            cd = form.cleaned_data
            values.append(
                LabTestResultValue(
                    lab_test=labtest,
                    item=item,
                    value=cd.get("value", ""),
                    comment=cd.get("comment", ""),
                )
            )
        LabTestResultValue.objects.bulk_create(values)
        log_activity(request.user, labtest, "create", "Tạo phiếu xét nghiệm")
        messages.success(request, "Đã lưu phiếu xét nghiệm thành công!")
        # Nếu có ?mr=.. thì quay lại Record detail
        medical_record_id = request.GET.get("mr")
        if medical_record_id:
            return redirect("medical_records:detail", pk=medical_record_id)

        return redirect("labtests:detail", pk=labtest.pk)

    combo = list(zip(items, formset.forms))
    return render(
        request,
        "labtests/fill_values.html",
        {
            "patient": patient,
            "category": category,
            "combo": combo,
            "formset": formset,
        },
    )


# 4️⃣ Chi tiết phiếu
@login_required
def labtest_detail(request, pk):
    labtest = get_object_or_404(
        LabTest.objects.select_related("patient", "category"), pk=pk
    )
    if request.method == "POST" and "export_word" in request.POST:
        try:
            # Create a temporary directory
            temp_dir = tempfile.mkdtemp()
            temp_file = os.path.join(temp_dir, f"labtest_{labtest.id}.docx")
            
            # Export to temporary file
            filename = export_labtest_to_word(labtest)
            shutil.move(filename, temp_file)
            
            # Create response with file iterator
            def file_iterator():
                with open(temp_file, 'rb') as f:
                    while chunk := f.read(8192):
                        yield chunk
                # Clean up after sending
                try:
                    os.remove(temp_file)
                    os.rmdir(temp_dir)
                except Exception as e:
                    print(f"Error cleaning up temporary files: {str(e)}")
            
            response = FileResponse(
                file_iterator(),
                as_attachment=True,
                filename=f"labtest_{labtest.id}.docx",
                content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )
            return response
            
        except Exception as e:
            messages.error(request, f'Lỗi khi xuất file: {str(e)}')
            return redirect('labtests:detail', pk=pk)
            
    results = labtest.results.select_related("item")
    return render(
        request, "labtests/detail.html", {"labtest": labtest, "results": results}
    )


# List view
@login_required
def labtest_list(request):
    # Get filter parameters
    q = request.GET.get('q', '').strip()
    category_id = request.GET.get('category')
    sort = request.GET.get('sort', '-created_at')

    # Base queryset
    qs = LabTest.objects.select_related('patient', 'category', 'created_by')

    # Apply search filter
    if q:
        qs = qs.filter(patient__full_name__icontains=q)

    # Apply category filter
    if category_id:
        qs = qs.filter(category_id=category_id)

    # Apply sorting
    qs = qs.order_by(sort)

    # Get all categories for filter dropdown
    categories = TestCategory.objects.filter(is_active=True).order_by('name')

    # Pagination
    page_obj = Paginator(qs, 15).get_page(request.GET.get('page'))

    return render(request, 'labtests/list.html', {
        'page_obj': page_obj,
        'categories': categories,
    })


@login_required
def labtest_update(request, pk):
    labtest = get_object_or_404(
        LabTest.objects.select_related("patient", "category"), pk=pk
    )
    results = labtest.results.select_related("item")
    items = list(labtest.category.items.order_by("order"))

    if request.method == "POST":
        formset = labtest_value_formset(request.POST, items=items)
        if formset.is_valid():
            # Xóa các kết quả cũ
            labtest.results.all().delete()
            
            # Tạo kết quả mới
            values = []
            for form, item in zip(formset.forms, items):
                cd = form.cleaned_data
                values.append(
                    LabTestResultValue(
                        lab_test=labtest,
                        item=item,
                        value=cd.get("value", ""),
                        comment=cd.get("comment", ""),
                    )
                )
            LabTestResultValue.objects.bulk_create(values)
            log_activity(request.user, labtest, "update", "Cập nhật phiếu xét nghiệm")
            messages.success(request, "Đã cập nhật phiếu xét nghiệm thành công!")
            return redirect("labtests:detail", pk=labtest.pk)
    else:
        # Điền giá trị cũ vào form
        initial_data = []
        for result in results:
            initial_data.append({
                'value': result.value,
                'comment': result.comment,
            })
        formset = labtest_value_formset(items=items, initial=initial_data)

    combo = list(zip(items, formset.forms))
    return render(
        request,
        "labtests/update.html",
        {
            "labtest": labtest,
            "combo": combo,
            "formset": formset,
        },
    )


@login_required
def export_labtest_word(request, pk):
    """Export lab test to Word document"""
    labtest = get_object_or_404(
        LabTest.objects.select_related("patient", "category"), pk=pk
    )
    try:
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()
        temp_file = os.path.join(temp_dir, f"labtest_{labtest.id}.docx")
        
        # Export to temporary file
        filename = export_labtest_to_word(labtest)
        shutil.move(filename, temp_file)
        
        # Create response with file iterator
        def file_iterator():
            with open(temp_file, 'rb') as f:
                while chunk := f.read(8192):
                    yield chunk
            # Clean up after sending
            try:
                os.remove(temp_file)
                os.rmdir(temp_dir)
            except Exception as e:
                print(f"Error cleaning up temporary files: {str(e)}")
        
        # Generate a more descriptive filename
        patient_name = labtest.patient.full_name.replace(' ', '_')
        category_name = labtest.category.name.replace(' ', '_')
        filename = f"{patient_name}_{category_name}_{labtest.created_at.strftime('%Y%m%d')}.docx"
        
        response = FileResponse(
            file_iterator(),
            as_attachment=True,
            filename=filename,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        
        # Add additional headers to ensure proper download
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        
        return response
        
    except Exception as e:
        messages.error(request, f'Lỗi khi xuất file: {str(e)}')
        return redirect('labtests:detail', pk=pk)
