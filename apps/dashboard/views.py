# apps/dashboard/views.py
from django.shortcuts import render, redirect # Import thêm redirect
from django.contrib import messages # Import messages để hiển thị thông báo
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Count, Q
from django.utils import timezone
import datetime

from apps.accounts.models import CustomUser
from apps.activity_logs.models import ActivityLog
from apps.medical_records.models import MedicalRecord
from apps.patients.models import Patient
from apps.appointments.models import Appointment

from .models import ClinicSetting # Đảm bảo đã import
from .forms import ClinicSettingForm # Đảm bảo đã import


def is_superuser_check(user):
    return user.is_authenticated and user.is_superuser

@login_required
def dashboard_view(request):
    today = timezone.localdate()
    total_patients = Patient.objects.count()
    appointments_today = Appointment.objects.filter(
        appointment_date=today
    ).select_related('patient', 'staff').order_by('appointment_time')
    next_seven_days = today + datetime.timedelta(days=7)
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gt=today,
        appointment_date__lte=next_seven_days
    ).select_related('patient', 'staff').order_by('appointment_date', 'appointment_time')[:5]
    medical_records_today_count = MedicalRecord.objects.filter(created_at__date=today).count()
    context = {
        'page_title': 'Bảng điều khiển',
        'total_patients': total_patients,
        'appointments_today': appointments_today,
        'upcoming_appointments': upcoming_appointments,
        'medical_records_today_count': medical_records_today_count,
        'current_date': today,
    }
    return render(request, 'dashboard/dashboard.html', context)

@login_required
@user_passes_test(is_superuser_check, login_url='home_dashboard')
def system_management_dashboard_view(request):
    active_tab = request.GET.get('tab', 'settings') # <<< Mặc định là tab 'settings' để dễ test
    
    clinic_setting_instance = ClinicSetting.get_instance()

    # Khởi tạo form ban đầu bên ngoài khối if POST
    # để nó luôn có sẵn cho context, ngay cả khi POST thất bại
    clinic_setting_form = ClinicSettingForm(instance=clinic_setting_instance)

    if request.method == 'POST':
        # Chỉ xử lý POST nếu nó dành cho clinic_settings và đang ở đúng tab
        if 'save_clinic_settings' in request.POST and active_tab == 'settings':
            # Khởi tạo lại form với dữ liệu POST và FILES
            clinic_setting_form = ClinicSettingForm(request.POST, request.FILES, instance=clinic_setting_instance)
            if clinic_setting_form.is_valid():
                clinic_setting_form.save()
                messages.success(request, "Đã cập nhật thông tin phòng khám thành công!")
                # Thêm tag vào message để có thể lọc trong template nếu cần
                # messages.success(request, "Đã cập nhật thông tin phòng khám thành công!", extra_tags="clinic_settings_form")
                return redirect(request.path + '?tab=settings')
            else:
                messages.error(request, "Vui lòng sửa các lỗi trong form thông tin phòng khám.")
                # messages.error(request, "Vui lòng sửa các lỗi trong form thông tin phòng khám.", extra_tags="clinic_settings_form")
        # Thêm xử lý cho các form khác (ví dụ: cài đặt bảo mật) ở đây nếu cần
        # elif 'save_security_settings' in request.POST and active_tab == 'settings':
        #     pass
    
    # Các context khác được chuẩn bị sau khi xử lý POST (nếu có)
    # hoặc khi là GET request
    context = {
        'page_title': 'Quản lý hệ thống',
        'active_tab': active_tab,
        'search_query_staff': request.GET.get('q_staff', ''),
        # 'search_query_stats': request.GET.get('q_stats', ''), # Bỏ comment nếu có tìm kiếm cho tab stats
        'clinic_setting_form': clinic_setting_form, # Form luôn được truyền, có thể chứa lỗi nếu POST thất bại
        'current_clinic_logo_url': clinic_setting_instance.logo.url if clinic_setting_instance.logo else None,
    }

    if active_tab == 'staff':
        staff_queryset = CustomUser.objects.filter(is_staff=True).order_by('full_name', 'email')
        query_staff = context['search_query_staff']
        if query_staff:
            staff_queryset = staff_queryset.filter(
                Q(email__icontains=query_staff) |
                Q(full_name__icontains=query_staff) |
                Q(username__icontains=query_staff)
            ).distinct()
        context['staff_list'] = staff_queryset
        context['staff_count'] = staff_queryset.count()

    elif active_tab == 'stats':
        context['total_medical_records'] = MedicalRecord.objects.count()
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        context['medical_records_this_month'] = MedicalRecord.objects.filter(
            created_at__year=current_year,
            created_at__month=current_month
        ).count()
        context['recent_activities'] = ActivityLog.objects.select_related('user').order_by('-log_timestamp')[:10]
        # Nếu bạn muốn staff_count ở tab Thống kê, hãy thêm nó vào đây:
        # context['staff_count'] = CustomUser.objects.filter(is_staff=True).count()


    elif active_tab == 'settings':
        # Dữ liệu cho tab Cài đặt đã được chuẩn bị bởi form clinic_setting_form
        # và current_clinic_logo_url
        context['security_settings'] = { # Dữ liệu ví dụ
            'enable_2fa': False,
            'auto_logout_minutes': 30
        }

    return render(request, 'dashboard/system_management_dashboard.html', context)