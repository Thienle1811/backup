        # apps/appointments/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from .models import Appointment
from .forms import AppointmentForm

@login_required
def appointment_list(request):
            query = request.GET.get('q', '')
            filter_date_str = request.GET.get('date', '')
            appointments_queryset = Appointment.objects.select_related('patient', 'staff', 'created_by').all()

            if query:
                appointments_queryset = appointments_queryset.filter(
                    Q(patient__full_name__icontains=query) |
                    Q(staff__full_name__icontains=query) |
                    Q(staff__email__icontains=query) |
                    Q(notes__icontains=query) |
                    Q(status__icontains=query)
                ).distinct()

            if filter_date_str:
                try:
                    filter_date = timezone.datetime.strptime(filter_date_str, '%Y-%m-%d').date()
                    appointments_queryset = appointments_queryset.filter(appointment_date=filter_date)
                except ValueError:
                    messages.error(request, "Định dạng ngày không hợp lệ. Vui lòng dùng YYYY-MM-DD.")

            appointments = appointments_queryset.order_by('appointment_date', 'appointment_time')
            
            context = {
                'appointments': appointments,
                'page_title': 'Danh sách Lịch hẹn',
                'search_query': query,
                'filter_date': filter_date_str,
                'appointment_count': appointments.count()
            }
            return render(request, 'appointments/appointment_list.html', context)

@login_required
def appointment_create(request):
            if request.method == 'POST':
                form = AppointmentForm(request.POST)
                if form.is_valid():
                    appointment = form.save(commit=False)
                    if request.user.is_authenticated:
                        appointment.created_by = request.user
                    appointment.save()
                    messages.success(request, f"Đã thêm lịch hẹn cho '{appointment.patient.full_name}' thành công!")
                    return redirect('appointments:appointment_list')
                else:
                    messages.error(request, "Vui lòng sửa các lỗi trong form.")
            else:
                form = AppointmentForm()
            
            context = {
                'form': form,
                'page_title': 'Thêm Lịch hẹn Mới',
                'form_title': 'Thông tin Lịch hẹn Mới',
                'submit_button_text': 'Lưu Lịch hẹn'
            }
            return render(request, 'appointments/appointment_form.html', context)

@login_required
def appointment_update(request, pk):
            appointment_instance = get_object_or_404(Appointment, pk=pk)
            if request.method == 'POST':
                form = AppointmentForm(request.POST, instance=appointment_instance)
                if form.is_valid():
                    updated_appointment = form.save(commit=False)
                    # Gán người cập nhật nếu bạn có trường updated_by trong model Appointment
                    # if request.user.is_authenticated and hasattr(updated_appointment, 'updated_by'):
                    #     updated_appointment.updated_by = request.user
                    updated_appointment.save()
                    messages.success(request, f"Đã cập nhật lịch hẹn cho '{updated_appointment.patient.full_name}' thành công!")
                    return redirect('appointments:appointment_list')
                else:
                    messages.error(request, "Vui lòng sửa các lỗi trong form.")
            else:
                form = AppointmentForm(instance=appointment_instance)
            
            context = {
                'form': form,
                'page_title': f'Cập nhật Lịch hẹn',
                'form_title': f'Cập nhật Lịch hẹn cho {appointment_instance.patient.full_name} ({appointment_instance.appointment_date.strftime("%d/%m/%Y")})',
                'submit_button_text': 'Lưu Thay đổi',
                'appointment_instance': appointment_instance
            }
            return render(request, 'appointments/appointment_form.html', context)

@login_required
def appointment_delete(request, pk): # pk là ID của lịch hẹn cần xóa
            """
            View để xóa một lịch hẹn sau khi xác nhận.
            """
            appointment_instance = get_object_or_404(Appointment, pk=pk)
            patient_name = appointment_instance.patient.full_name if appointment_instance.patient else "Không rõ bệnh nhân"
            appointment_date_str = appointment_instance.appointment_date.strftime("%d/%m/%Y")

            if request.method == 'POST':
                # Nếu người dùng xác nhận xóa (gửi form POST)
                appointment_instance.delete() # Thực hiện xóa
                messages.success(request, f"Đã xóa lịch hẹn ngày {appointment_date_str} của bệnh nhân '{patient_name}' thành công!")
                return redirect('appointments:appointment_list') # Chuyển hướng về danh sách

            # Nếu là GET request, hiển thị trang xác nhận xóa
            context = {
                'appointment': appointment_instance, # Đổi tên context variable cho rõ ràng
                'page_title': f'Xác nhận Xóa Lịch hẹn',
                'confirm_message': f"Bạn có chắc chắn muốn xóa lịch hẹn ngày {appointment_date_str} của bệnh nhân '{patient_name}' không? Hành động này không thể hoàn tác."
            }
            return render(request, 'appointments/appointment_confirm_delete.html', context)
        