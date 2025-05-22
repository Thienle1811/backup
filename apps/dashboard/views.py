from django.shortcuts import render

# Create your views here.
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import timedelta
from django.utils import timezone
from django.db.models import BooleanField, Case, Value, When, Count
from datetime import datetime, time

from apps.labtests.models import LabTest
from apps.patients.models import Patient
from apps.medical_records.models import MedicalRecord


@login_required
def home(request):
    # Get today's date range
    today = timezone.now().date()
    today_start = timezone.make_aware(datetime.combine(today, time.min))
    today_end = timezone.make_aware(datetime.combine(today, time.max))

    # Get statistics
    total_patients = Patient.objects.count()
    today_records = MedicalRecord.objects.filter(created_at__range=(today_start, today_end)).count()
    today_labtests = LabTest.objects.filter(created_at__range=(today_start, today_end)).count()
    pending_labtests = LabTest.objects.filter(medical_record__isnull=True).count()

    # Get recent records
    recent_labtests = (
        LabTest.objects
        .select_related('patient', 'category', 'created_by')
        .order_by('-created_at')[:10]
    )
    
    recent_medical_records = (
        MedicalRecord.objects
        .select_related('patient', 'created_by')
        .order_by('-created_at')[:10]
    )

    context = {
        'total_patients': total_patients,
        'today_records': today_records,
        'today_labtests': today_labtests,
        'pending_labtests': pending_labtests,
        'lab_tests': recent_labtests,
        'medical_records': recent_medical_records,
    }
    
    return render(request, 'dashboard/home.html', context)
