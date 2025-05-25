# ────────────────────── apps/medical_records/views.py ────────────────────────
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.urls import reverse
from .utils import export_medicalrecord_to_word
from django.http import FileResponse
import os
from django.db import models

from apps.patients.models import Patient
from .models import MedicalRecord
from .forms import MedicalRecordForm
from apps.activity_logs.models import log_activity
from .forms import AttachLabTestForm
from apps.labtests.models import LabTest
from django.contrib.auth import get_user_model


# List view
@login_required
def record_list(request):
    # Get filter parameters
    q = request.GET.get('q', '').strip()
    sort = request.GET.get('sort', '-record_date')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')

    # Base queryset
    qs = MedicalRecord.objects.select_related('patient', 'doctor', 'created_by')

    # Apply search filter
    if q:
        qs = qs.filter(
            models.Q(patient__full_name__icontains=q) |
            models.Q(diagnosis__icontains=q) |
            models.Q(notes__icontains=q)
        )

    # Apply date range filter
    if date_from:
        qs = qs.filter(record_date__gte=date_from)
    if date_to:
        qs = qs.filter(record_date__lte=date_to)

    # Apply sorting
    qs = qs.order_by(sort)

    # Pagination
    page_obj = Paginator(qs, 15).get_page(request.GET.get('page'))

    return render(request, 'medical_records/list.html', {
        'page_obj': page_obj,
    })


# bước 1: chọn bệnh nhân (+ optional preselect)
@login_required
def select_patient(request):
    pre_id = request.GET.get("patient")
    if pre_id:
        return redirect("medical_records:create", patient_id=pre_id)

    q = request.GET.get("q", "")
    patients = (
        Patient.objects.filter(full_name__icontains=q) if q else Patient.objects.none()
    )
    return render(
        request, "medical_records/select_patient.html", {"patients": patients, "q": q}
    )


@login_required
def record_create(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    form = MedicalRecordForm(request.POST or None)
    
    if request.method == "POST":
        if form.is_valid():
            mr = form.save(commit=False)
            mr.patient = patient
            mr.created_by = request.user
            mr.save()
            log_activity(request.user, mr, "create", "Tạo bệnh án")

            if mr.unlinked_labtests.exists():
                # 👉 ngay sau khi tạo, chuyển sang màn hình Gắn phiếu
                messages.info(request, "Bệnh nhân còn phiếu xét nghiệm chưa gắn.")
                return redirect("medical_records:attach_labtests", pk=mr.pk)

            messages.success(request, "Đã tạo bệnh án thành công!")
            return redirect("medical_records:detail", pk=mr.pk)
        else:
            # Add form errors to messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")

    return render(
        request,
        "medical_records/form.html",
        {"form": form, "patient": patient, "title": "Thêm bệnh án"},
    )


# chi tiết
@login_required
def record_detail(request, pk):
    record = get_object_or_404(MedicalRecord.objects.select_related("patient"), pk=pk)
    labtests = record.lab_tests.select_related("category")
    return render(
        request,
        "medical_records/detail.html",
        {
            "record": record,
            "labtests": labtests,
            "create_labtest_url": reverse(
                "labtests:select_category", args=[record.patient.id]
            )
            + f"?mr={record.id}",
        },
    )


# chỉnh sửa
@login_required
def record_edit(request, pk):
    record = get_object_or_404(MedicalRecord, pk=pk)
    form = MedicalRecordForm(request.POST or None, instance=record)
    if request.method == "POST" and form.is_valid():
        rec = form.save(commit=False)
        rec.updated_by = request.user
        rec.save()
        log_activity(request.user, rec, "update", "Cập nhật bệnh án")
        messages.success(request, "Đã lưu thay đổi!")
        return redirect("medical_records:detail", pk=pk)
    return render(
        request,
        "medical_records/form.html",
        {
            "form": form,
            "patient": record.patient,
            "title": "Chỉnh sửa bệnh án",
            "record": record,
        },
    )


@login_required
def attach_labtests(request, pk):
    record = get_object_or_404(MedicalRecord.objects.select_related("patient"), pk=pk)
    form = AttachLabTestForm(request.POST or None, patient=record.patient)

    if request.method == "POST" and form.is_valid():
        selected_ids = form.cleaned_data["labtests"].values_list("id", flat=True)
        LabTest.objects.filter(id__in=selected_ids).update(medical_record=record)

        log_activity(
            request.user,
            record,
            "update",
            f"Gắn {len(selected_ids)} phiếu xét nghiệm",
        )
        messages.success(request, "Đã gắn phiếu xét nghiệm vào bệnh án!")
        return redirect("medical_records:detail", pk=record.id)

    return render(
        request,
        "medical_records/attach_labtests.html",
        {"form": form, "record": record},
    )


@login_required
def detach_labtest(request, pk, labtest_id):
    record = get_object_or_404(MedicalRecord, pk=pk)
    labtest = get_object_or_404(LabTest, pk=labtest_id, medical_record=record)
    # Gỡ liên kết
    labtest.medical_record = None
    labtest.save()
    # Ghi lại activity và thông báo
    log_activity(
        request.user,
        record,
        "update",
        f"Gỡ phiếu xét nghiệm #{labtest.id} khỏi bệnh án",
    )
    messages.success(request, "Đã gỡ phiếu xét nghiệm khỏi bệnh án.")
    return redirect("medical_records:detail", pk=pk)


@login_required
def record_word(request, pk):
    record = get_object_or_404(MedicalRecord.objects.select_related("patient"), pk=pk)
    try:
        filename = export_medicalrecord_to_word(record)
        
        def file_iterator():
            with open(filename, 'rb') as f:
                while chunk := f.read(8192):
                    yield chunk
            # File will be automatically closed after the generator is exhausted
            try:
                os.remove(filename)
            except Exception as e:
                print(f"Error deleting temporary file {filename}: {str(e)}")
        
        response = FileResponse(
            file_iterator(),
            as_attachment=True,
            filename=filename,
            content_type='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        )
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        messages.error(request, f'Lỗi khi xuất file: {str(e)}')
        return redirect('medical_records:detail', pk=pk)
