from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q
from apps.medical_records.models import MedicalRecord
from .models import Patient
from .forms import PatientForm


# Danh sách có tìm kiếm + phân trang
def patient_list(request):
    q = request.GET.get("q", "").strip()
    patients_qs = Patient.objects.all()
    if q:
        patients_qs = patients_qs.filter(
            Q(full_name__icontains=q) | Q(phone__icontains=q)
        )

    paginator = Paginator(patients_qs, 10)  # 10 per page
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "patients": page_obj.object_list,
        "page_obj": page_obj,
        "q": q,
    }
    return render(request, "patients/list.html", context)


def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    records_qs = MedicalRecord.objects.filter(patient=patient).order_by("-record_date")
    paginator = Paginator(records_qs, 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "patients/detail.html",
        {"patient": patient, "records": page_obj.object_list, "page_obj": page_obj},
    )


def patient_create(request):
    form = PatientForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("patients:list")
    return render(
        request, "patients/form.html", {"form": form, "title": "Thêm bệnh nhân"}
    )


def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    records = patient.medical_records.select_related("patient") \
                                     .prefetch_related("lab_tests__category")
    return render(request, "patients/detail.html", {
        "patient": patient,
        "records": records,
    })


def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    form = PatientForm(request.POST or None, instance=patient)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("patients:detail", pk=pk)
    return render(
        request, "patients/form.html", {"form": form, "title": "Chỉnh sửa thông tin bệnh nhân"}
    )


def patient_delete(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == "POST":
        patient.delete()
        return redirect("patients:list")
    return render(
        request,
        "patients/confirm_delete.html",
        {"object": patient, "title": "Xoá bệnh nhân"},
    )
