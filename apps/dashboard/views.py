        # apps/dashboard/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.appointments.models import Appointment
from apps.medical_records.models import MedicalRecord
from apps.patients.models import Patient
from django.utils import timezone
import datetime

@login_required
def dashboard_view(request):
            # Lấy ngày hiện tại
            today = timezone.localdate() # Sử dụng localdate để lấy ngày theo múi giờ của server

            # Thống kê cơ bản (ví dụ)
            total_patients = Patient.objects.count()
            
            # Lấy các lịch hẹn cho ngày hôm nay
            # Sắp xếp theo thời gian hẹn, những lịch hẹn chưa có giờ sẽ ở cuối
            appointments_today = Appointment.objects.filter(
                appointment_date=today
            ).select_related('patient', 'staff').order_by('appointment_time')

            # Lấy các lịch hẹn sắp tới (ví dụ: trong 7 ngày tới, không bao gồm hôm nay)
            next_seven_days = today + datetime.timedelta(days=7)
            upcoming_appointments = Appointment.objects.filter(
                appointment_date__gt=today, # Lớn hơn ngày hôm nay
                appointment_date__lte=next_seven_days # Nhỏ hơn hoặc bằng 7 ngày tới
            ).select_related('patient', 'staff').order_by('appointment_date', 'appointment_time')[:5] # Lấy 5 lịch hẹn gần nhất

            # Số hồ sơ mới nhập hôm nay (ví dụ)
            medical_records_today_count = MedicalRecord.objects.filter(created_at__date=today).count()

            context = {
                'page_title': 'Bảng điều khiển',
                'total_patients': total_patients,
                'appointments_today': appointments_today,
                'upcoming_appointments': upcoming_appointments,
                'medical_records_today_count': medical_records_today_count,
                'current_date': today,
            }
            # Sau này, bạn có thể phân tách context cho admin và user thường
            # if request.user.is_staff:
            #     # Thêm context riêng cho admin
            #     pass
            return render(request, 'dashboard/dashboard.html', context)
        