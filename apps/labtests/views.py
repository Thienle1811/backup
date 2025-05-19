# apps/labtests/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from .models import LabTestTemplate, LabTestTemplateField, LabTest, LabTestResultValue, LabTestVersion
from .forms import (
    LabTestTemplateForm, 
    LabTestTemplateFieldFormSet, 
    LabTestForm,
    LabTestResultValueFormSet
)
from django.utils import timezone
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle, Spacer, Image
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from django.conf import settings
from reportlab.lib.utils import ImageReader

# --- Views cho LabTestTemplate và AJAX (giữ nguyên như trước) ---
@login_required
def lab_test_template_list(request): # ... (giữ nguyên) ...
    query = request.GET.get('q', '')
    templates_queryset = LabTestTemplate.objects.select_related('created_by').all()
    if query:
        templates_queryset = templates_queryset.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()
    templates = templates_queryset.order_by('name')
    context = {
        'lab_test_templates': templates, 'page_title': 'Danh sách Mẫu Xét nghiệm',
        'search_query': query, 'template_count': templates.count()
    }
    return render(request, 'labtests/lab_test_template_list.html', context)

@login_required
def lab_test_template_create(request): # ... (giữ nguyên) ...
    if request.method == 'POST':
        form = LabTestTemplateForm(request.POST)
        formset = LabTestTemplateFieldFormSet(request.POST, prefix='fields')
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic(): 
                    lab_test_template = form.save(commit=False)
                    if request.user.is_authenticated:
                        lab_test_template.created_by = request.user
                    lab_test_template.save() 
                    formset.instance = lab_test_template
                    formset.save()
                    messages.success(request, f"Đã tạo mẫu xét nghiệm '{lab_test_template.name}' thành công!")
                    return redirect('labtests:lab_test_template_list')
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra khi lưu mẫu xét nghiệm: {e}")
        else:
            messages.error(request, "Vui lòng sửa các lỗi trong form chính và/hoặc các chỉ số của mẫu xét nghiệm.")
            print("Lỗi Form Mẫu Xét Nghiệm (POST CREATE):", form.errors.as_json(escape_html=True))
            print("Lỗi Formset Chỉ Số (POST CREATE):", formset.errors)
            print("Lỗi Formset Non-form (Chỉ Số) (POST CREATE):", formset.non_form_errors())
    else: # GET request
        form = LabTestTemplateForm()
        formset = LabTestTemplateFieldFormSet(prefix='fields') 
    
    context = {
        'form': form, 'formset': formset, 
        'page_title': 'Thêm Mẫu Xét nghiệm Mới', 'form_title': 'Thông tin Mẫu Xét nghiệm',
        'submit_button_text': 'Lưu Mẫu Xét nghiệm'
    }
    return render(request, 'labtests/lab_test_template_form.html', context)

@login_required
def lab_test_template_update(request, pk): # ... (giữ nguyên) ...
    template_instance = get_object_or_404(LabTestTemplate, pk=pk)
    if request.method == 'POST':
        form = LabTestTemplateForm(request.POST, instance=template_instance)
        formset = LabTestTemplateFieldFormSet(request.POST, instance=template_instance, prefix='fields')
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    updated_template = form.save() 
                    formset.save() 
                    messages.success(request, f"Đã cập nhật mẫu xét nghiệm '{updated_template.name}' thành công!")
                    return redirect('labtests:lab_test_template_list')
            except Exception as e:
                messages.error(request, f"Có lỗi xảy ra khi cập nhật mẫu xét nghiệm: {e}")
        else:
            messages.error(request, "Vui lòng sửa các lỗi trong form chính và/hoặc các chỉ số của mẫu xét nghiệm.")
            print("Lỗi Form Cập Nhật Mẫu Xét Nghiệm (POST UPDATE):", form.errors.as_json(escape_html=True))
            print("Lỗi Formset Cập Nhật Chỉ Số (POST UPDATE):", formset.errors)
            print("Lỗi Formset Non-form Cập Nhật (Chỉ Số) (POST UPDATE):", formset.non_form_errors())
    else: # GET request
        form = LabTestTemplateForm(instance=template_instance)
        formset = LabTestTemplateFieldFormSet(instance=template_instance, prefix='fields')
    context = {
        'form': form, 'formset': formset,
        'page_title': f'Cập nhật Mẫu Xét nghiệm: {template_instance.name}',
        'form_title': 'Cập nhật Thông tin Mẫu Xét nghiệm',
        'submit_button_text': 'Lưu Thay đổi',
        'template_instance': template_instance
    }
    return render(request, 'labtests/lab_test_template_form.html', context)

@login_required
def lab_test_template_delete(request, pk): # ... (giữ nguyên) ...
    template_instance = get_object_or_404(LabTestTemplate, pk=pk)
    template_name = template_instance.name
    if request.method == 'POST':
        try:
            if template_instance.lab_tests.exists():
                messages.error(request, f"Không thể xóa mẫu xét nghiệm '{template_name}' vì nó đang được sử dụng.")
                return redirect('labtests:lab_test_template_list')
            template_instance.delete()
            messages.success(request, f"Đã xóa mẫu xét nghiệm '{template_name}' thành công!")
            return redirect('labtests:lab_test_template_list')
        except Exception as e:
             messages.error(request, f"Có lỗi xảy ra khi xóa mẫu xét nghiệm: {e}")
             return redirect('labtests:lab_test_template_list')
    context = {
        'template_instance': template_instance,
        'page_title': f'Xác nhận Xóa Mẫu Xét nghiệm: {template_name}',
        'confirm_message': f"Bạn có chắc chắn muốn xóa mẫu xét nghiệm '{template_name}' không?"
    }
    return render(request, 'labtests/lab_test_template_confirm_delete.html', context)

@login_required
def ajax_get_template_fields(request, template_id): # ... (giữ nguyên) ...
    try:
        template = LabTestTemplate.objects.get(pk=template_id)
        fields_data = list(template.fields.all().order_by('field_order').values(
            'id', 'field_name', 'unit', 'reference_range_text', 'result_guidance'
        ))
        return JsonResponse({'fields': fields_data})
    except LabTestTemplate.DoesNotExist:
        return JsonResponse({'error': 'Template not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def lab_test_create_and_enter_results(request):
    if request.method == 'POST':
        lab_test_form = LabTestForm(request.POST, prefix='labtest')
        result_formset = LabTestResultValueFormSet(request.POST, prefix='results')

        if lab_test_form.is_valid():
            lab_test = lab_test_form.save(commit=False)
            if request.user.is_authenticated:
                lab_test.requested_by = request.user
            lab_test.save() 

            result_formset.instance = lab_test 
            if result_formset.is_valid():
                try:
                    with transaction.atomic():
                        # Xóa các result_value cũ của lab_test này trước khi lưu mới (nếu cần)
                        # Điều này hữu ích nếu JS luôn gửi lại toàn bộ formset
                        # lab_test.result_values.all().delete() 
                        
                        result_formset.save() # Django formset sẽ tự động xử lý việc tạo/cập nhật
                                            # các LabTestResultValue liên quan đến lab_test.instance
                                            # và gán lab_test, template_field (nếu template_field là ModelChoiceField trong form)

                        # Gán entered_by cho các instance vừa được formset lưu
                        for form_in_formset in result_formset:
                            if form_in_formset.instance and form_in_formset.instance.pk: # Chỉ gán cho instance đã được lưu
                                if form_in_formset.has_changed() or not form_in_formset.instance.entered_by:
                                    form_in_formset.instance.entered_by = request.user
                                    form_in_formset.instance.save(update_fields=['entered_by'])
                        
                        lab_test.results_updated_at = timezone.now()
                        snapshot_details = "; ".join([f"{rv.template_field.field_name}: {rv.value or ''}" for rv in lab_test.result_values.all().order_by('template_field__field_order')])
                        first_version = LabTestVersion.objects.create(
                            lab_test=lab_test, version_number=1,
                            result_snapshot=snapshot_details,
                            changed_by=request.user,
                            change_reason="Phiếu xét nghiệm được tạo và nhập kết quả."
                        )
                        lab_test.latest_version = first_version
                        lab_test.save()
                        messages.success(request, f"Đã lưu kết quả xét nghiệm cho HSBA ID {lab_test.medical_record.id} thành công!")
                        return redirect('labtests:lab_test_list')
                except Exception as e:
                    messages.error(request, f"Lỗi khi lưu kết quả chi tiết: {e}")
                    print(f"Lỗi Exception khi lưu LabTest/Results (CREATE): {e}")
            else: 
                messages.error(request, "Vui lòng sửa các lỗi trong phần nhập kết quả chi tiết.")
                print("LabTest Form (valid):", lab_test_form.cleaned_data)
                print("Result Formset errors (POST CREATE):", result_formset.errors)
                for i, form_in_set in enumerate(result_formset.forms):
                    if form_in_set.errors: print(f"  Form {i} errors: {form_in_set.errors.as_json(escape_html=True)}")
                print("Result Formset non-form errors (POST CREATE):", result_formset.non_form_errors())
        else: 
            messages.error(request, "Vui lòng sửa các lỗi trong thông tin phiếu xét nghiệm.")
            print("LabTest Form errors (POST CREATE):", lab_test_form.errors.as_json(escape_html=True))
            if result_formset.is_bound:
                 print("Result Formset (bound but lab_test_form invalid) errors:", result_formset.errors)
                 print("Result Formset (bound but lab_test_form invalid) non-form errors:", result_formset.non_form_errors())
    else: # GET request
        lab_test_form = LabTestForm(prefix='labtest')
        result_formset = LabTestResultValueFormSet(queryset=LabTestResultValue.objects.none(), prefix='results')
    
    context = {
        'lab_test_form': lab_test_form,
        'result_formset': result_formset,
        'page_title': 'Nhập Kết quả Xét nghiệm Mới',
        'form_title': 'Thông tin Phiếu Xét nghiệm và Kết quả',
        'submit_button_text': 'Lưu Kết quả'
    }
    return render(request, 'labtests/lab_test_form_and_results.html', context)

@login_required 
def lab_test_list(request): # ... (giữ nguyên) ...
    query = request.GET.get('q', '')
    lab_tests_queryset = LabTest.objects.select_related(
        'medical_record__patient', 'template', 'requested_by', 'latest_version'
    ).all()
    if query:
        lab_tests_queryset = lab_tests_queryset.filter(
            Q(medical_record__patient__full_name__icontains=query) |
            Q(template__name__icontains=query) |
            Q(medical_record__id__icontains=query) | 
            Q(id__icontains=query) 
        ).distinct()
    lab_tests = lab_tests_queryset.order_by('-requested_at')
    context = {
        'lab_tests': lab_tests, 'page_title': 'Danh sách Phiếu Xét nghiệm',
        'search_query': query, 'test_count': lab_tests.count()
    }
    return render(request, 'labtests/lab_test_list.html', context)


@login_required # SỬA HÀM NÀY
def lab_test_update_results(request, pk):
    lab_test_instance = get_object_or_404(LabTest.objects.select_related('medical_record__patient', 'template'), pk=pk)
    
    if request.method == 'POST':
        lab_test_form = LabTestForm(request.POST, instance=lab_test_instance, prefix='labtest')
        result_formset = LabTestResultValueFormSet(request.POST, instance=lab_test_instance, prefix='results')
        
        if lab_test_form.is_valid() and result_formset.is_valid():
            try:
                with transaction.atomic():
                    updated_lab_test = lab_test_form.save(commit=False)
                    updated_lab_test.results_updated_at = timezone.now()
                    updated_lab_test.save()

                    significant_change_in_results = False
                    if result_formset.has_changed():
                        significant_change_in_results = True
                    
                    # Xử lý các form được đánh dấu xóa trước
                    for form_to_delete in result_formset.deleted_objects:
                        form_to_delete.delete()

                    # Lưu các form còn lại (cả cập nhật và tạo mới nếu có)
                    # formset.save() sẽ tự động xử lý việc này khi có instance
                    # Chúng ta cần đảm bảo template_field được gán đúng cho các form mới (nếu có)
                    # và entered_by được gán.
                    instances = result_formset.save(commit=False)
                    for i, instance in enumerate(instances): # instances là các LabTestResultValue
                        instance.lab_test = updated_lab_test # Đảm bảo liên kết đúng
                        
                        # Nếu là form mới (chưa có pk) và template_field chưa được gán (từ hidden input)
                        # thì JS phải đảm bảo gửi template_field_id
                        if not instance.template_field_id:
                            template_field_id_str = request.POST.get(f'results-{i}-template_field')
                            if template_field_id_str:
                                try:
                                    instance.template_field_id = int(template_field_id_str)
                                except ValueError:
                                    print(f"UPDATE: Invalid template_field_id '{template_field_id_str}' for new form {i}.")
                                    continue # Bỏ qua form này nếu template_field không hợp lệ
                            else:
                                print(f"UPDATE: Missing template_field_id for new form {i}.")
                                continue # Bỏ qua form mới không có template_field

                        if request.user.is_authenticated:
                            instance.entered_by = request.user
                        
                        if instance.template_field_id: # Chỉ lưu nếu có template_field
                            instance.save()
                    
                    if significant_change_in_results:
                        last_version_number = updated_lab_test.versions.aggregate(max_version=Max('version_number'))['max_version'] or 0
                        new_version_number = last_version_number + 1
                        current_results_snapshot = "; ".join([f"{rv.template_field.field_name}: {rv.value or ''}" for rv in updated_lab_test.result_values.all().order_by('template_field__field_order')])
                        LabTestVersion.objects.create(
                            lab_test=updated_lab_test, version_number=new_version_number,
                            result_snapshot=current_results_snapshot, 
                            changed_by=request.user,
                            change_reason="Kết quả xét nghiệm được cập nhật."
                        )
                        updated_lab_test.latest_version = updated_lab_test.versions.order_by('-version_number').first()
                        updated_lab_test.save(update_fields=['latest_version', 'results_updated_at'])
                    
                    messages.success(request, f"Đã cập nhật kết quả xét nghiệm cho HSBA ID {updated_lab_test.medical_record.id} thành công!")
                    return redirect('labtests:lab_test_list')
            except Exception as e:
                messages.error(request, f"Lỗi khi cập nhật kết quả: {str(e)}")
                print(f"Lỗi Exception khi cập nhật LabTest/Results: {e}")
        else: 
            messages.error(request, "Vui lòng sửa các lỗi trong form và/hoặc kết quả.")
            print("LabTest Form errors (update):", lab_test_form.errors.as_json(escape_html=True))
            print("Result Formset errors (update):", result_formset.errors)
            for i, form_in_set in enumerate(result_formset.forms):
                if form_in_set.errors: print(f"  Form {i} errors (update): {form_in_set.errors.as_json(escape_html=True)}")
            print("Result Formset non-form errors (update):", result_formset.non_form_errors())
    else: # GET request
        lab_test_form = LabTestForm(instance=lab_test_instance, prefix='labtest')
        # Khởi tạo formset với instance. Django sẽ tự động tìm LabTestResultValue liên quan.
        result_formset = LabTestResultValueFormSet(instance=lab_test_instance, prefix='results')
        
        # DEBUG: In ra để xem formset có dữ liệu không khi GET
        print(f"DEBUG GET - LabTest ID for update: {lab_test_instance.pk}")
        if result_formset.forms:
            for i, form_in_set in enumerate(result_formset.forms):
                print(f"  Form {i} (GET update) initial value: {form_in_set.initial.get('value')}, instance value: {form_in_set.instance.value if form_in_set.instance and hasattr(form_in_set.instance, 'value') else 'No instance or value'}")
                print(f"  Form {i} (GET update) instance template_field_id: {form_in_set.instance.template_field_id if form_in_set.instance and hasattr(form_in_set.instance, 'template_field_id') else 'No instance or template_field_id'}")
        else: # Nếu không có form nào, nghĩa là không có result_value nào được tạo cho các template_field của LabTest này
              # JavaScript sẽ cần tạo các dòng dựa trên template.
            print("  DEBUG GET - No forms in result_formset on GET for update. JS will populate based on template.")


    context = {
        'lab_test_form': lab_test_form, 'result_formset': result_formset,
        'lab_test_instance': lab_test_instance, 
        'page_title': f'Sửa/Xem Kết quả Xét nghiệm: {lab_test_instance.template.name}',
        'form_title': f'Kết quả cho {lab_test_instance.medical_record.patient.full_name} (HSBA: {lab_test_instance.medical_record.id})',
        'submit_button_text': 'Lưu Thay đổi Kết quả'
    }
    return render(request, 'labtests/lab_test_form_and_results.html', context)

# ... (lab_test_delete và generate_lab_test_pdf giữ nguyên) ...
@login_required
def lab_test_delete(request, pk): # ... (giữ nguyên) ...
    lab_test_instance = get_object_or_404(LabTest, pk=pk)
    lab_test_display = f"phiếu xét nghiệm #{lab_test_instance.pk} ({lab_test_instance.template.name}) cho bệnh nhân {lab_test_instance.medical_record.patient.full_name}"
    if request.method == 'POST':
        try:
            lab_test_instance.delete() 
            messages.success(request, f"Đã xóa {lab_test_display} thành công!")
            return redirect('labtests:lab_test_list')
        except Exception as e:
            messages.error(request, f"Có lỗi xảy ra khi xóa phiếu xét nghiệm: {e}")
            return redirect('labtests:lab_test_list')
    context = {
        'lab_test_instance': lab_test_instance,
        'page_title': 'Xác nhận Xóa Phiếu Xét nghiệm',
        'confirm_message': f"Bạn có chắc chắn muốn xóa {lab_test_display} không?"
    }
    return render(request, 'labtests/lab_test_confirm_delete.html', context)

@login_required
def generate_lab_test_pdf(request, lab_test_id): # ... (giữ nguyên như phiên bản trước - ID: labtest_views_py_pdf_font_logo_final_v2) ...
    lab_test = get_object_or_404(LabTest.objects.select_related(
        'medical_record__patient', 
        'template', 
        'requested_by',
    ), pk=lab_test_id)
    
    results = LabTestResultValue.objects.filter(lab_test=lab_test).select_related('template_field__template').order_by('template_field__field_order')

    buffer = io.BytesIO()
    p_canvas = canvas.Canvas(buffer, pagesize=A4)
    page_width, page_height = A4

    font_name = "Helvetica"; font_name_bold = "Helvetica-Bold"
    font_dir = os.path.join(settings.BASE_DIR, 'static', 'fonts')
    dejavu_sans_path = os.path.join(font_dir, 'DejaVuSans.ttf') 
    dejavu_sans_bold_path = os.path.join(font_dir, 'DejaVuSans-Bold.ttf')
    try:
        if os.path.exists(dejavu_sans_path) and os.path.exists(dejavu_sans_bold_path):
            pdfmetrics.registerFont(TTFont('VietFont', dejavu_sans_path))
            pdfmetrics.registerFont(TTFont('VietFont-Bold', dejavu_sans_bold_path))
            font_name = 'VietFont'; font_name_bold = 'VietFont-Bold'
    except Exception: pass 

    styles = getSampleStyleSheet()
    style_normal = ParagraphStyle('Normal_Vi', parent=styles['Normal'], fontName=font_name, fontSize=9, leading=11)
    style_bold_small = ParagraphStyle('Bold_Small_Vi', parent=styles['Normal'], fontName=font_name_bold, fontSize=9, leading=11)
    style_bold_large_centered = ParagraphStyle('Bold_Large_Centered_Vi', parent=styles['Normal'], fontName=font_name_bold, fontSize=16, leading=18, alignment=1)
    style_header_info = ParagraphStyle('Header_Info_Vi', parent=styles['Normal'], fontName=font_name, fontSize=8, leading=10)
    style_clinic_main_title = ParagraphStyle('Clinic_Name_Main_Vi', parent=styles['Normal'], fontName=font_name_bold, fontSize=11, leading=13) 
    style_clinic_sub_title = ParagraphStyle('Clinic_Sub_Title_Vi', parent=styles['Normal'], fontName=font_name_bold, fontSize=9, leading=11) 
    style_patient_info = ParagraphStyle('Patient_Info_Vi', parent=styles['Normal'], fontName=font_name, fontSize=10, leading=12)
    style_footer_note = ParagraphStyle('Footer_Note_Vi', parent=styles['Normal'], fontName=font_name, fontSize=7, leading=9) 
    style_slogan = ParagraphStyle('Slogan_Vi', parent=styles['Normal'], fontName=font_name_bold, fontSize=9, leading=11, alignment=1)

    logo_filename = 'medionco_logo.png' 
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'images', logo_filename)
    logo_x = 10*mm; logo_y_top = page_height - 10*mm; logo_max_height = 25*mm 
    text_x_offset_after_logo = logo_x 
    if os.path.exists(logo_path):
        try:
            img_reader = ImageReader(logo_path)
            orig_width, orig_height = img_reader.getSize(); aspect_ratio = orig_width / float(orig_height)
            logo_height_calc = logo_max_height; logo_width_calc = logo_height_calc * aspect_ratio
            p_canvas.drawImage(logo_path, logo_x, logo_y_top - logo_height_calc, width=logo_width_calc, height=logo_height_calc, preserveAspectRatio=True, mask='auto', anchor='nw')
            text_x_offset_after_logo = logo_x + logo_width_calc + 3*mm 
        except Exception as e: print(f"Error drawing logo image '{logo_path}': {e}")
    else: print(f"WARNING: Logo file not found at {logo_path}.")

    y_text_offset_clinic = logo_y_top - 5*mm 
    p_clinic_name = Paragraph("Y KHOA UNG BƯỚU CẦN THƠ", style_clinic_main_title)
    p_clinic_name.wrapOn(p_canvas, page_width - text_x_offset_after_logo - 20*mm, 10*mm); p_clinic_name.drawOn(p_canvas, text_x_offset_after_logo, y_text_offset_clinic)
    y_text_offset_clinic -= 5*mm
    p_clinic_subname = Paragraph("PHÒNG XÉT NGHIỆM MEDIONCO", style_clinic_sub_title)
    p_clinic_subname.wrapOn(p_canvas, page_width - text_x_offset_after_logo - 20*mm, 10*mm); p_clinic_subname.drawOn(p_canvas, text_x_offset_after_logo, y_text_offset_clinic)
    
    header_info_y_start = page_height - 38*mm 
    line_height_contact = 4*mm; left_col_x_contact = 20*mm; right_col_x_contact = 130*mm
    p_addr = Paragraph("Địa chỉ: Số 10, ĐS 5, Tổ 17, KV Bình Thường B, P. Long Tuyền, Q. Bình Thủy, TPCT.", style_header_info)
    p_addr.wrapOn(p_canvas, 105*mm, 10*mm); p_addr.drawOn(p_canvas, left_col_x_contact, header_info_y_start)
    stt_text = f"STT: {timezone.localtime(lab_test.requested_at).strftime('%y%m%d')}-{lab_test.pk}"
    p_stt = Paragraph(stt_text, style_header_info); p_stt.wrapOn(p_canvas, 70*mm, 10*mm); p_stt.drawOn(p_canvas, right_col_x_contact, header_info_y_start)
    header_info_y_start -= line_height_contact
    p_phone = Paragraph(f"Điện thoại: 0917.575656.", style_header_info)
    p_phone.wrapOn(p_canvas, 105*mm, 10*mm); p_phone.drawOn(p_canvas, left_col_x_contact, header_info_y_start)
    ngay_dk_text = f"Ngày đăng ký: {timezone.localtime(lab_test.requested_at).strftime('%d/%m/%Y - %H:%M')}"
    p_ngay_dk = Paragraph(ngay_dk_text, style_header_info); p_ngay_dk.wrapOn(p_canvas, 70*mm, 10*mm); p_ngay_dk.drawOn(p_canvas, right_col_x_contact, header_info_y_start)
    header_info_y_start -= line_height_contact
    p_web = Paragraph(f"Web: Ykhoaungbuoucantho.com.vn.", style_header_info)
    p_web.wrapOn(p_canvas, 105*mm, 10*mm); p_web.drawOn(p_canvas, left_col_x_contact, header_info_y_start)
    gio_xuat_text = f"Giờ xuất file: {timezone.localtime(timezone.now()).strftime('%d/%m/%Y - %H:%M')}"
    p_gio_xuat = Paragraph(gio_xuat_text, style_header_info); p_gio_xuat.wrapOn(p_canvas, 70*mm, 10*mm); p_gio_xuat.drawOn(p_canvas, right_col_x_contact, header_info_y_start)
    header_info_y_start -= line_height_contact
    p_email = Paragraph(f"Email: CSKH.MEDIONCO@GMAIL.COM.", style_header_info)
    p_email.wrapOn(p_canvas, 105*mm, 10*mm); p_email.drawOn(p_canvas, left_col_x_contact, header_info_y_start)

    y_title_kq = header_info_y_start - 12*mm 
    p_title = Paragraph("KẾT QUẢ XÉT NGHIỆM", style_bold_large_centered)
    title_w, title_h = p_title.wrapOn(p_canvas, page_width - 40*mm, 20*mm)
    p_title.drawOn(p_canvas, (page_width - title_w) / 2, y_title_kq - title_h)

    y_position_patient = y_title_kq - title_h - 10*mm 
    line_height_patient = 6*mm 
    patient = lab_test.medical_record.patient
    p_canvas.setFont(font_name, 10)
    p_canvas.drawString(20*mm, y_position_patient, f"Họ tên: {patient.full_name or ''}")
    p_canvas.drawString(100*mm, y_position_patient, f"Ngày tháng năm sinh: {patient.date_of_birth.strftime('%d/%m/%Y') if patient.date_of_birth else ''}")
    y_position_patient -= line_height_patient 
    p_canvas.drawString(20*mm, y_position_patient, f"Giới Tính: {patient.get_gender_display() or ''}")
    p_canvas.drawString(100*mm, y_position_patient, f"Điện thoại: {patient.phone or ''}") 
    y_position_patient -= line_height_patient
    
    p_diachi_text = f"Địa chỉ: {patient.address or ''}"
    p_diachi_para = Paragraph(p_diachi_text, style_patient_info)
    w_diachi, h_diachi = p_diachi_para.wrapOn(p_canvas, page_width - 40*mm, 15*mm) 
    p_diachi_para.drawOn(p_canvas, 20*mm, y_position_patient - h_diachi + style_patient_info.leading*0.2) 
    y_position_patient -= (h_diachi + 2*mm) 
    
    bs_chi_dinh_text = f"BS Chỉ định: {lab_test.requested_by.get_full_name() if lab_test.requested_by else 'N/A'}"
    p_canvas.drawString(20*mm, y_position_patient, bs_chi_dinh_text)
    bs_phone_text = f"Số điện Thoại BS: {lab_test.requested_by.phone if lab_test.requested_by and lab_test.requested_by.phone else 'N/A'}"
    p_canvas.drawString(100*mm, y_position_patient, bs_phone_text)
    y_position_patient -= line_height_patient

    p_chandoan_text = f"Chẩn đoán: {lab_test.medical_record.diagnosis or ''}"
    p_chandoan_para = Paragraph(p_chandoan_text, style_patient_info)
    w_cd, h_cd = p_chandoan_para.wrapOn(p_canvas, 85*mm, 15*mm)
    p_chandoan_para.drawOn(p_canvas, 20*mm, y_position_patient - h_cd + style_patient_info.leading*0.2)
    p_ghichu_hsba_text = f"Ghi chú: {lab_test.medical_record.notes or ''}"
    p_ghichu_hsba = Paragraph(p_ghichu_hsba_text, style_patient_info)
    available_w_ghichu = page_width - (110*mm) - 15*mm 
    _w_ghichu, _h_ghichu = p_ghichu_hsba.wrapOn(p_canvas, available_w_ghichu, 15*mm) 
    p_ghichu_hsba.drawOn(p_canvas, 110*mm, y_position_patient - _h_ghichu + style_patient_info.leading*0.2)
    y_position_for_table = y_position_patient - max(h_cd, _h_ghichu) - 7*mm

    table_data = [
        [Paragraph("XÉT NGHIỆM", style_bold_small), Paragraph("KẾT QUẢ", style_bold_small), Paragraph("KHOẢN THAM CHIẾU", style_bold_small), Paragraph("ĐƠN VỊ", style_bold_small)]
    ]
    if results.exists():
        for result in results:
            table_data.append([
                Paragraph(str(result.template_field.field_name or ''), style_normal),
                Paragraph(str(result.value or ''), style_normal),
                Paragraph(str(result.template_field.reference_range_text or ''), style_normal),
                Paragraph(str(result.template_field.unit or ''), style_normal)
            ])
    else:
        table_data.append([Paragraph("Chưa có kết quả chi tiết cho phiếu xét nghiệm này.", style_normal), "", "", ""])
    
    num_data_rows = results.count() if results.exists() else 1
    num_empty_rows_needed = 2 - num_data_rows 
    for _ in range(max(0, num_empty_rows_needed)): 
        table_data.append([Paragraph('', style_normal), Paragraph('', style_normal), Paragraph('', style_normal), Paragraph('', style_normal)])

    table_width = page_width - 40*mm 
    col_widths = [table_width*0.40, table_width*0.15, table_width*0.30, table_width*0.15] 
    result_table = Table(table_data, colWidths=col_widths, repeatRows=1)
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#D0D0D0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), font_name_bold), ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 5), ('TOPPADDING', (0,0), (-1,0), 5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('LEFTPADDING', (0,0), (-1,-1), 3), ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    
    frame_x = 20*mm; frame_y_bottom_margin = 60*mm 
    frame_width = page_width - 40*mm; frame_height = y_position_for_table - frame_y_bottom_margin 
    
    try:
        w_table, h_table = result_table.wrapOn(p_canvas, frame_width, frame_height)
        if h_table <= frame_height :
            result_table.drawOn(p_canvas, frame_x, y_position_for_table - h_table)
        else: 
            p_canvas.drawString(20*mm, y_position_for_table - 5*mm, "LƯU Ý: Kết quả quá dài, chức năng ngắt trang tự động cần hoàn thiện.")
    except Exception as e_table:
        print(f"Error drawing table: {e_table}")
        p_canvas.drawString(20*mm, y_position_for_table - 5*mm, "Lỗi khi vẽ bảng kết quả.")

    
    # --- Footer (Sửa khoảng cách ký tên) ---
    footer_y_start = 45*mm 
    p_kiem_duyet = Paragraph("Kết quả đã được kiểm duyệt /QA", style_normal)
    p_kiem_duyet.wrapOn(p_canvas, 80*mm, 10*mm); p_kiem_duyet.drawOn(p_canvas, 20*mm, footer_y_start)
    
    ngay_thang_nam_tp = f"TP. Cần Thơ, ngày {timezone.localtime(timezone.now()).day} tháng {timezone.localtime(timezone.now()).month} năm {timezone.localtime(timezone.now()).year}"
    p_ngay_tp = Paragraph(ngay_thang_nam_tp, style_normal)
    text_width_ngaytp = p_canvas.stringWidth(ngay_thang_nam_tp, font_name, 9)
    p_ngay_tp.wrapOn(p_canvas, text_width_ngaytp + 5*mm, 10*mm); p_ngay_tp.drawOn(p_canvas, page_width - 20*mm - text_width_ngaytp, footer_y_start)
    
    # Khoảng trống cho chữ ký (ĐÃ SỬA)
    signature_block_y_start = footer_y_start - 10*mm # Y bắt đầu cho khối "PHÒNG XÉT NGHIỆM"
    signature_space_above_text = 18*mm # Khoảng trống phía trên chữ "PHÒNG XÉT NGHIỆM" để ký (tăng lên)
    
    p_pxn_title = Paragraph("PHÒNG XÉT NGHIỆM", style_bold_small)
    pxn_title_width = p_canvas.stringWidth("PHÒNG XÉT NGHIỆM", font_name_bold, 9)
    p_pxn_title.wrapOn(p_canvas, pxn_title_width + 5*mm, 10*mm); p_pxn_title.drawOn(p_canvas, page_width - 20*mm - pxn_title_width - (70*mm - pxn_title_width)/2 , signature_block_y_start - signature_space_above_text)

    p_ky_ten = Paragraph("(Ký, đóng dấu và ghi rõ họ tên)", style_header_info)
    ky_ten_width = p_canvas.stringWidth("(Ký, đóng dấu và ghi rõ họ tên)", font_name, 8)
    p_ky_ten.wrapOn(p_canvas, ky_ten_width + 5*mm, 10*mm); p_ky_ten.drawOn(p_canvas, page_width - 20*mm - ky_ten_width - (70*mm - ky_ten_width)/2, signature_block_y_start - signature_space_above_text - 5*mm)


    p_ghichu_cuoi = Paragraph("*Ghi chú: Kết quả in đậm là ngoài khoảng tham chiếu, kết quả chỉ có giá trị trên mẫu thử. Tô đậm bên trái -Thấp. Tô đậm bên phải-Cao.", style_footer_note)
    p_ghichu_cuoi.wrapOn(p_canvas, page_width - 40*mm, 15*mm); p_ghichu_cuoi.drawOn(p_canvas, 20*mm, 15*mm)
    p_slogan = Paragraph("TẦM SOÁT SỚM - SỐNG KHỎE MẠNH", style_slogan)
    p_slogan.wrapOn(p_canvas, page_width - 40*mm, 10*mm); p_slogan.drawOn(p_canvas, 20*mm, 7*mm)

    p_canvas.save()
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="ket_qua_xet_nghiem_{lab_test.pk}.pdf"'
    response.write(pdf)
    return response

