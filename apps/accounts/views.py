# apps/accounts/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.urls import reverse_lazy
from .models import CustomUser
from .forms import CustomUserAdminCreationForm, CustomUserAdminChangeForm, StaffUserCreationForm
from django.db.models import Q
# from apps.activity_logs.models import ActivityLog # Bỏ comment nếu bạn muốn ghi log
# from django.conf import settings # Cần nếu dùng settings.INSTALLED_APPS

# Hàm kiểm tra xem user có phải là SUPERUSER không
def is_superuser_check(user):
    return user.is_authenticated and user.is_superuser

# Hàm kiểm tra xem user có phải là staff (nhân viên được phép truy cập hệ thống)
def is_staff_user_check(user):
    return user.is_authenticated and user.is_staff


@login_required
# Sử dụng is_superuser_check cho các view quản lý người dùng
@user_passes_test(is_superuser_check, login_url=reverse_lazy('home_dashboard')) 
def user_list_admin_view(request):
    query = request.GET.get('q', '')
    users_queryset = CustomUser.objects.all()

    if query:
        users_queryset = users_queryset.filter(
            Q(email__icontains=query) |
            Q(username__icontains=query) |
            Q(full_name__icontains=query) |
            Q(phone__icontains=query)
        ).distinct()

    users = users_queryset.order_by('email')
    context = {
        'users_list': users,
        'page_title': 'Quản lý Người dùng (Admin)', # Rõ ràng hơn
        'search_query': query,
        'user_count': users.count()
    }
    return render(request, 'accounts/admin_user_list.html', context)

@login_required
@user_passes_test(is_superuser_check, login_url=reverse_lazy('home_dashboard'))
def user_create_admin_view(request): 
    if request.method == 'POST':
        form = StaffUserCreationForm(request.POST) 
        if form.is_valid():
            user = form.save() 
            messages.success(request, f"Đã tạo nhân viên '{user.email}' với quyền mặc định thành công.")
            return redirect('accounts_admin:user_list_admin')
        else:
            messages.error(request, "Vui lòng sửa các lỗi trong form.")
    else:
        form = StaffUserCreationForm() 
    
    context = {
        'form': form,
        'page_title': 'Tạo Nhân viên Mới (Admin)', # Rõ ràng hơn
        'form_title': 'Thông tin Nhân viên Mới',
        'submit_button_text': 'Tạo Nhân viên'
    }
    return render(request, 'accounts/admin_user_form.html', context)

@login_required
@user_passes_test(is_superuser_check, login_url=reverse_lazy('home_dashboard'))
def user_update_admin_view(request, pk): 
    user_instance = get_object_or_404(CustomUser, pk=pk)
    if request.method == 'POST':
        form = CustomUserAdminChangeForm(request.POST, instance=user_instance) 
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Đã cập nhật thông tin người dùng '{user.email}' thành công.")
            return redirect('accounts_admin:user_list_admin')
        else:
            messages.error(request, "Vui lòng sửa các lỗi trong form.")
    else:
        form = CustomUserAdminChangeForm(instance=user_instance)
    
    context = {
        'form': form,
        'user_instance': user_instance,
        'page_title': f'Cập nhật Người dùng (Admin): {user_instance.email}', # Rõ ràng hơn
        'form_title': 'Cập nhật Thông tin Người dùng',
        'submit_button_text': 'Lưu Thay đổi'
    }
    return render(request, 'accounts/admin_user_form.html', context)

@login_required
@user_passes_test(is_superuser_check, login_url=reverse_lazy('home_dashboard'))
def user_delete_admin_view(request, pk):
    user_to_delete = get_object_or_404(CustomUser, pk=pk)
    user_email_to_delete = user_to_delete.email

    if request.user.pk == user_to_delete.pk:
        messages.error(request, "Bạn không thể tự xóa tài khoản của chính mình.")
        return redirect('accounts_admin:user_list_admin')

    if request.method == 'POST':
        try:
            user_to_delete.delete()
            messages.success(request, f"Đã xóa người dùng '{user_email_to_delete}' thành công.")
            return redirect('accounts_admin:user_list_admin')
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra khi xóa người dùng: {e}")
            return redirect('accounts_admin:user_list_admin')

    context = {
        'user_to_delete': user_to_delete,
        'page_title': f'Xác nhận Xóa Người dùng (Admin): {user_email_to_delete}', # Rõ ràng hơn
        'confirm_message': f"Bạn có chắc chắn muốn xóa người dùng '{user_email_to_delete}' không? Hành động này không thể hoàn tác."
    }
    return render(request, 'accounts/admin_user_confirm_delete.html', context)
