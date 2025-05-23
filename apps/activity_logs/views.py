# apps/activity_logs/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import ActivityLog

# Hàm kiểm tra superuser (bạn có thể import từ app khác nếu đã định nghĩa ở đó)
def is_superuser_check(user):
    return user.is_authenticated and user.is_superuser

@login_required
@user_passes_test(is_superuser_check) # Chỉ superuser mới xem được toàn bộ log
def full_activity_log_list_view(request):
    log_list_qs = ActivityLog.objects.select_related('user', 'content_type').order_by('-log_timestamp')

    query = request.GET.get('q_log', '')
    if query:
        log_list_qs = log_list_qs.filter(
            Q(user__email__icontains=query) |
            Q(user__full_name__icontains=query) |
            Q(action__icontains=query) |
            Q(details__icontains=query) |
            Q(ip_address__icontains=query)
            # Bạn không thể tìm trực tiếp trên content_object vì nó là GenericForeignKey,
            # nhưng có thể lọc theo content_type và object_id nếu cần.
        ).distinct()

    items_per_page = 25 # Số lượng log trên mỗi trang
    paginator = Paginator(log_list_qs, items_per_page)
    page_number = request.GET.get('page')

    try:
        logs_page = paginator.page(page_number)
    except PageNotAnInteger:
        # Nếu page không phải là số nguyên, trả về trang đầu tiên.
        logs_page = paginator.page(1)
    except EmptyPage:
        # Nếu page vượt quá tổng số trang, trả về trang cuối cùng.
        logs_page = paginator.page(paginator.num_pages)

    context = {
        'page_title': 'Nhật ký hoạt động hệ thống',
        'logs_page': logs_page,
        'search_query_log': query,
        'total_logs': paginator.count,
    }
    return render(request, 'activity_logs/full_activity_log_list.html', context)