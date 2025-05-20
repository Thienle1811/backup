# apps/labtests/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import LabTestTemplate, LabTestTemplateField, LabTest, LabTestResultValue, LabTestVersion
from apps.patients.models import Patient
from apps.medical_records.models import MedicalRecord
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
from reportlab.lib.units import cm, mm # Đảm bảo cm và mm được import
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
from django.conf import settings
from reportlab.lib.utils import ImageReader


# --- Views cho LabTestTemplate (Giữ nguyên) ---
@login_required
def lab_test_template_list(request):
    query = request.GET.get('q', '')
    templates_queryset = LabTestTemplate.objects.select_related('created_by').all()
    if query:
        templates_queryset = templates_queryset.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        ).distinct()
    templates = templates_queryset.order_by('name')
    context = {
        'lab_test_templates': templates,
        'page_title': _('Danh sách Mẫu Xét nghiệm'),
        'search_query': query,
        'template_count': templates.count()
    }
    return render(request, 'labtests/lab_test_template_list.html', context)

@login_required
def lab_test_template_create(request):
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
                    messages.success(request, _("Đã tạo mẫu xét nghiệm '{name}' thành công!").format(name=lab_test_template.name))
                    return redirect('labtests:lab_test_template_list')
            except Exception as e:
                messages.error(request, _("Có lỗi xảy ra khi lưu mẫu xét nghiệm: {error}").format(error=e))
        else:
            messages.error(request, _("Vui lòng sửa các lỗi trong form chính và/hoặc các chỉ số của mẫu xét nghiệm."))
    else: # GET request
        form = LabTestTemplateForm()
        formset = LabTestTemplateFieldFormSet(prefix='fields')

    context = {
        'form': form, 'formset': formset,
        'page_title': _('Thêm Mẫu Xét nghiệm Mới'),
        'form_title': _('Thông tin Mẫu Xét nghiệm'),
        'submit_button_text': _('Lưu Mẫu Xét nghiệm')
    }
    return render(request, 'labtests/lab_test_template_form.html', context)

@login_required
def lab_test_template_update(request, pk):
    template_instance = get_object_or_404(LabTestTemplate, pk=pk)
    if request.method == 'POST':
        form = LabTestTemplateForm(request.POST, instance=template_instance)
        formset = LabTestTemplateFieldFormSet(request.POST, instance=template_instance, prefix='fields')
        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    updated_template = form.save()
                    formset.save()
                    messages.success(request, _("Đã cập nhật mẫu xét nghiệm '{name}' thành công!").format(name=updated_template.name))
                    return redirect('labtests:lab_test_template_list')
            except Exception as e:
                messages.error(request, _("Có lỗi xảy ra khi cập nhật mẫu xét nghiệm: {error}").format(error=e))
        else:
            messages.error(request, _("Vui lòng sửa các lỗi trong form chính và/hoặc các chỉ số của mẫu xét nghiệm."))
    else: # GET request
        form = LabTestTemplateForm(instance=template_instance)
        formset = LabTestTemplateFieldFormSet(instance=template_instance, prefix='fields')
    context = {
        'form': form, 'formset': formset,
        'page_title': _("Cập nhật Mẫu Xét nghiệm: {name}").format(name=template_instance.name),
        'form_title': _('Cập nhật Thông tin Mẫu Xét nghiệm'),
        'submit_button_text': _('Lưu Thay đổi'),
        'template_instance': template_instance
    }
    return render(request, 'labtests/lab_test_template_form.html', context)

@login_required
def lab_test_template_delete(request, pk):
    template_instance = get_object_or_404(LabTestTemplate, pk=pk)
    template_name = template_instance.name
    if request.method == 'POST':
        try:
            if template_instance.lab_tests.exists():
                messages.error(request, _("Không thể xóa mẫu xét nghiệm '{name}' vì nó đang được sử dụng trong các phiếu xét nghiệm.").format(name=template_name))
                return redirect('labtests:lab_test_template_list')
            template_instance.delete()
            messages.success(request, _("Đã xóa mẫu xét nghiệm '{name}' thành công!").format(name=template_name))
            return redirect('labtests:lab_test_template_list')
        except Exception as e:
             messages.error(request, _("Có lỗi xảy ra khi xóa mẫu xét nghiệm: {error}").format(error=e))
             return redirect('labtests:lab_test_template_list')
    context = {
        'template_instance': template_instance,
        'page_title': _("Xác nhận Xóa Mẫu Xét nghiệm: {name}").format(name=template_name),
        'confirm_message': _("Bạn có chắc chắn muốn xóa mẫu xét nghiệm '{name}' không? Hành động này không thể hoàn tác nếu mẫu không được sử dụng.").format(name=template_name)
    }
    return render(request, 'labtests/lab_test_template_confirm_delete.html', context)


# --- Views cho LabTest và LabTestResultValue ---
@login_required
def ajax_get_template_fields(request, template_id):
    try:
        template = get_object_or_404(LabTestTemplate, pk=template_id)
        fields_data = list(template.fields.all().order_by('field_order').values(
            'id', 'field_name', 'unit', 'reference_range_text', 'result_guidance'
        ))
        return JsonResponse({'fields': fields_data})
    except LabTestTemplate.DoesNotExist:
        return JsonResponse({'error': 'Template not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
@transaction.atomic
def lab_test_create_and_enter_results(request):
    patient_id_from_url = request.GET.get('patient_id')
    selected_patient = None
    initial_lab_test_data = {}
    medical_record_queryset = MedicalRecord.objects.select_related('patient').order_by('-record_date', 'patient__full_name')
    initial_medical_record_pk = None

    if patient_id_from_url:
        try:
            selected_patient = get_object_or_404(Patient.objects.select_related(None), pk=patient_id_from_url)
            medical_record_queryset = MedicalRecord.objects.filter(patient=selected_patient).select_related('patient').order_by('-record_date')
            latest_medical_record = medical_record_queryset.first()
            if latest_medical_record:
                initial_lab_test_data['medical_record'] = latest_medical_record.pk
                initial_medical_record_pk = latest_medical_record.pk
            else:
                messages.info(request, _("Bệnh nhân '{name}' (Mã: {ma_bn}) chưa có Hồ sơ bệnh án nào.").format(name=selected_patient.full_name, ma_bn=selected_patient.ma_benh_nhan))
        except Patient.DoesNotExist:
            messages.error(request, _("Không tìm thấy bệnh nhân được chọn từ URL."))
            selected_patient = None

    if request.method == 'POST':
        if patient_id_from_url and not selected_patient:
             try:
                selected_patient = get_object_or_404(Patient.objects.select_related(None), pk=patient_id_from_url)
             except Patient.DoesNotExist:
                messages.error(request, _("Tham số bệnh nhân không hợp lệ trong quá trình xử lý."))
                selected_patient = None

        lab_test_form = LabTestForm(request.POST, prefix='labtest')
        if selected_patient:
             lab_test_form.fields['medical_record'].queryset = medical_record_queryset

        result_formset = LabTestResultValueFormSet(request.POST, prefix='results')

        if lab_test_form.is_valid():
            lab_test = lab_test_form.save(commit=False)
            if request.user.is_authenticated:
                lab_test.requested_by = request.user
            lab_test.print_status = LabTest.PrintStatus.PENDING

            if selected_patient and lab_test.medical_record.patient != selected_patient:
                messages.error(request, _("Hồ sơ bệnh án đã chọn không thuộc về bệnh nhân '{name}'. Vui lòng chọn lại.").format(name=selected_patient.full_name))
                context = {
                    'lab_test_form': lab_test_form, 'result_formset': result_formset,
                    'page_title': _("Tạo Phiếu XN cho {name}").format(name=selected_patient.full_name) if selected_patient else _('Nhập Kết quả Xét nghiệm Mới'),
                    'form_title': _('Thông tin Phiếu Xét nghiệm và Kết quả'),
                    'submit_button_text': _('Lưu Kết quả'),
                    'selected_patient': selected_patient,
                    'initial_medical_record_pk': initial_medical_record_pk
                }
                return render(request, 'labtests/lab_test_form_and_results.html', context)

            lab_test.save() 

            result_formset.instance = lab_test
            if result_formset.is_valid():
                try:
                    with transaction.atomic():
                        instances = result_formset.save(commit=False)
                        saved_count = 0
                        for instance in instances:
                            if instance.template_field_id:
                                if request.user.is_authenticated:
                                    instance.entered_by = request.user
                                if instance.value or instance.comment or instance.pk:
                                    instance.save()
                                    saved_count += 1
                        
                        if saved_count > 0 or (lab_test.template and not lab_test.template.fields.exists()):
                            lab_test.results_updated_at = timezone.now()
                            snapshot_details_list = []
                            for rv in lab_test.result_values.select_related('template_field').all().order_by('template_field__field_order'):
                                snapshot_details_list.append(f"{rv.template_field.field_name}: {rv.value or ''}")
                            result_snapshot = "; ".join(snapshot_details_list)
                            
                            current_version = LabTestVersion.objects.create(
                                lab_test=lab_test, version_number=1,
                                result_snapshot=result_snapshot, changed_by=request.user,
                                change_reason=_("Phiếu xét nghiệm được tạo và nhập kết quả lần đầu.")
                            )
                            lab_test.latest_version = current_version

                            action = request.POST.get('action')
                            if action == 'save_and_print':
                                if lab_test.result_values.exists() or (lab_test.template and not lab_test.template.fields.exists()):
                                    lab_test.print_status = LabTest.PrintStatus.PRINTED
                                    lab_test.last_print_date = timezone.now()
                                else:
                                    messages.warning(request, _("Không thể 'Lưu và In' vì chưa có kết quả nào được nhập cho các chỉ số yêu cầu. Phiếu đã được lưu."))
                            
                            lab_test.save()
                            messages.success(request, _("Đã tạo và lưu thành công!"))
                            
                            if action == 'save_and_print' and lab_test.print_status == LabTest.PrintStatus.PRINTED:
                                return redirect('labtests:generate_lab_test_pdf', lab_test_id=lab_test.pk)
                            return redirect('labtests:lab_test_list')
                        else:
                             messages.warning(request, _("Phiếu xét nghiệm (ID: {lab_test_id}) đã được tạo nhưng chưa có kết quả chi tiết nào được nhập.").format(lab_test_id=lab_test.custom_id))
                             return redirect(reverse('labtests:lab_test_update_results', kwargs={'pk': lab_test.pk}))
                except Exception as e:
                    messages.error(request, _("Lỗi khi lưu kết quả chi tiết: {error}").format(error=e))
            else:
                error_messages_list = []
                for form_in_set in result_formset:
                    if form_in_set.errors:
                        for field, errors_content in form_in_set.errors.items():
                            field_label = form_in_set.fields[field].label if field in form_in_set.fields and form_in_set.fields[field].label else field
                            error_messages_list.append(_("Lỗi ở chỉ số '{label}': {errors}").format(label=field_label, errors=', '.join(errors_content)))
                if result_formset.non_form_errors():
                    error_messages_list.append(_("Lỗi chung của bộ kết quả: {errors}").format(errors=', '.join(result_formset.non_form_errors())))
                if not error_messages_list:
                     messages.error(request, _("Dữ liệu kết quả chi tiết không hợp lệ. Vui lòng kiểm tra lại."))
                else:
                     messages.error(request, " ".join(error_messages_list))
        else:
            messages.error(request, _("Vui lòng sửa các lỗi trong thông tin phiếu xét nghiệm."))
    else: 
        lab_test_form = LabTestForm(prefix='labtest', initial=initial_lab_test_data)
        if selected_patient:
            lab_test_form.fields['medical_record'].queryset = medical_record_queryset
        result_formset = LabTestResultValueFormSet(queryset=LabTestResultValue.objects.none(), prefix='results')

    context = {
        'lab_test_form': lab_test_form,
        'result_formset': result_formset,
        'page_title': _("Tạo Phiếu XN cho {name} (Mã BN: {ma_bn})").format(name=selected_patient.full_name, ma_bn=selected_patient.ma_benh_nhan) if selected_patient else _('Nhập Kết quả Xét nghiệm Mới'),
        'form_title': _('Thông tin Phiếu Xét nghiệm và Kết quả'),
        'submit_button_text': _('Lưu Kết quả'),
        'selected_patient': selected_patient,
        'initial_medical_record_pk': initial_medical_record_pk,
    }
    return render(request, 'labtests/lab_test_form_and_results.html', context)

@login_required
def lab_test_list(request):
    query = request.GET.get('q', '')
    lab_tests_queryset = LabTest.objects.select_related(
        'medical_record__patient', 'template', 'requested_by', 'latest_version'
    ).all()
    template_id_filter = request.GET.get('template_id')
    if template_id_filter:
        lab_tests_queryset = lab_tests_queryset.filter(template_id=template_id_filter)

    if query:
        lab_tests_queryset = lab_tests_queryset.filter(
            Q(custom_id__icontains=query) |
            Q(medical_record__patient__full_name__icontains=query) |
            Q(medical_record__patient__ma_benh_nhan__icontains=query) |
            Q(template__name__icontains=query) |
            Q(medical_record__id__icontains=query)
        ).distinct()
    lab_tests = lab_tests_queryset.order_by('-requested_at')
    context = {
        'lab_tests': lab_tests,
        'page_title': _('Danh sách Phiếu Xét nghiệm'),
        'search_query': query,
        'test_count': lab_tests.count(),
        'selected_template_id': template_id_filter
    }
    return render(request, 'labtests/lab_test_list.html', context)

@login_required
@transaction.atomic
def lab_test_update_results(request, pk):
    lab_test_instance = get_object_or_404(
        LabTest.objects.select_related('medical_record__patient', 'template', 'latest_version'), 
        pk=pk
    )
    selected_patient_for_edit = lab_test_instance.medical_record.patient if lab_test_instance.medical_record else None

    if request.method == 'POST':
        lab_test_form = LabTestForm(request.POST, instance=lab_test_instance, prefix='labtest')
        lab_test_form.fields['medical_record'].disabled = True
        lab_test_form.fields['template'].disabled = True
        
        result_formset = LabTestResultValueFormSet(request.POST, instance=lab_test_instance, prefix='results')

        if lab_test_form.is_valid() and result_formset.is_valid():
            updated_lab_test = lab_test_form.save(commit=False)
            updated_lab_test.results_updated_at = timezone.now()
            
            significant_change_in_results = False
            if result_formset.has_changed():
                significant_change_in_results = True
            
            for form_to_delete in result_formset.deleted_forms:
                if form_to_delete.instance.pk:
                    form_to_delete.instance.delete()
                    significant_change_in_results = True
            
            saved_forms_count = 0
            for form_in_set in result_formset.forms:
                if form_in_set.has_changed() or (form_in_set.instance.pk is None and form_in_set.cleaned_data.get('value')):
                    if form_in_set.is_valid() and form_in_set.cleaned_data.get('template_field'):
                        result_value_instance = form_in_set.save(commit=False)
                        if request.user.is_authenticated:
                            result_value_instance.entered_by = request.user
                        result_value_instance.save()
                        saved_forms_count +=1
            
            if saved_forms_count > 0:
                significant_change_in_results = True

            if significant_change_in_results:
                last_version_number = updated_lab_test.versions.aggregate(max_version=Max('version_number'))['max_version'] or 0
                new_version_number = last_version_number + 1
                
                current_results_snapshot_list = []
                for rv in updated_lab_test.result_values.select_related('template_field').all().order_by('template_field__field_order'):
                     current_results_snapshot_list.append(f"{rv.template_field.field_name}: {rv.value or ''}")
                current_results_snapshot = "; ".join(current_results_snapshot_list)
                
                new_version = LabTestVersion.objects.create(
                    lab_test=updated_lab_test, version_number=new_version_number,
                    result_snapshot=current_results_snapshot,
                    changed_by=request.user,
                    change_reason=_("Kết quả xét nghiệm được cập nhật.")
                )
                updated_lab_test.latest_version = new_version
                updated_lab_test.save(update_fields=['latest_version', 'results_updated_at']) 
            else:
                if lab_test_form.has_changed():
                    updated_lab_test.save()

            messages.success(request, _("Đã cập nhật và lưu thành công!"))
            
            action = request.POST.get('action')
            if action == 'save_and_print':
                if updated_lab_test.result_values.exists() or (updated_lab_test.template and not updated_lab_test.template.fields.exists()):
                    updated_lab_test.print_status = LabTest.PrintStatus.PRINTED
                    updated_lab_test.last_print_date = timezone.now()
                    updated_lab_test.save(update_fields=['print_status', 'last_print_date'])
                    return redirect('labtests:generate_lab_test_pdf', lab_test_id=updated_lab_test.pk)
                else:
                    messages.warning(request, _("Không thể 'In' vì chưa có kết quả nào được nhập. Thay đổi đã được lưu."))
            return redirect('labtests:lab_test_list')
        else:
            messages.error(request, _("Vui lòng sửa các lỗi trong form và/hoặc kết quả."))
    else:
        lab_test_form = LabTestForm(instance=lab_test_instance, prefix='labtest')
        lab_test_form.fields['medical_record'].disabled = True
        lab_test_form.fields['template'].disabled = True
        result_formset = LabTestResultValueFormSet(instance=lab_test_instance, prefix='results')

    context = {
        'lab_test_form': lab_test_form,
        'result_formset': result_formset,
        'lab_test_instance': lab_test_instance,
        'selected_patient': selected_patient_for_edit,
        'page_title': _("Sửa/Xem Kết quả Xét nghiệm (ID: {lab_test_id}) - {template_name}").format(lab_test_id=lab_test_instance.custom_id, template_name=lab_test_instance.template.name),
        'form_title': _("Kết quả cho {patient_name} (Mã BN: {ma_bn} - HSBA: {hsba_id})").format(
            patient_name=lab_test_instance.medical_record.patient.full_name, 
            ma_bn=lab_test_instance.medical_record.patient.ma_benh_nhan,
            hsba_id=lab_test_instance.medical_record.id
        ),
        'submit_button_text': _('Lưu Thay đổi Kết quả')
    }
    return render(request, 'labtests/lab_test_form_and_results.html', context)

@login_required
def lab_test_delete(request, pk):
    lab_test_instance = get_object_or_404(LabTest.objects.select_related('medical_record__patient', 'template'), pk=pk)
    lab_test_display_info = _("phiếu xét nghiệm ID {lab_test_id} ({template_name}) cho bệnh nhân {patient_name} (Mã BN: {ma_bn})").format(
        lab_test_id=lab_test_instance.custom_id if lab_test_instance.custom_id else f"#{lab_test_instance.pk}",
        template_name=lab_test_instance.template.name,
        patient_name=lab_test_instance.medical_record.patient.full_name,
        ma_bn=lab_test_instance.medical_record.patient.ma_benh_nhan
    )
    if request.method == 'POST':
        try:
            lab_test_instance.delete()
            messages.success(request, _("Đã xóa {info} thành công!").format(info=lab_test_display_info))
            return redirect('labtests:lab_test_list')
        except Exception as e:
            messages.error(request, _("Có lỗi xảy ra khi xóa phiếu xét nghiệm: {error}").format(error=e))
            return redirect('labtests:lab_test_list')
    context = {
        'lab_test_instance': lab_test_instance,
        'page_title': _('Xác nhận Xóa Phiếu Xét nghiệm'),
        'confirm_message': _("Bạn có chắc chắn muốn xóa {info} không? Hành động này không thể hoàn tác.").format(info=lab_test_display_info)
    }
    return render(request, 'labtests/lab_test_confirm_delete.html', context)


@login_required
def generate_lab_test_pdf(request, lab_test_id):
    lab_test = get_object_or_404(LabTest.objects.select_related(
        'medical_record__patient', 'template', 'requested_by', 'latest_version'
    ), pk=lab_test_id)
    results = LabTestResultValue.objects.filter(lab_test=lab_test).select_related('template_field').order_by('template_field__field_order')

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
    except Exception as e:
        pass

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
    logo_path_parts = [str(settings.BASE_DIR), 'static', 'images', logo_filename]
    if hasattr(settings, 'STATICFILES_DIRS') and settings.STATICFILES_DIRS:
        logo_path_parts = [str(settings.STATICFILES_DIRS[0]), 'images', logo_filename]
    elif hasattr(settings, 'STATIC_ROOT') and settings.STATIC_ROOT:
        logo_path_parts = [str(settings.STATIC_ROOT), 'images', logo_filename]
    logo_path = os.path.join(*logo_path_parts)
    
    logo_x = 10*mm
    logo_y_top = page_height - 10*mm + 2.5*mm 
    logo_max_height = 25*mm
    text_x_offset_after_logo = logo_x
    if os.path.exists(logo_path):
        try:
            img_reader = ImageReader(logo_path)
            orig_width, orig_height = img_reader.getSize()
            aspect_ratio = orig_width / float(orig_height) if orig_height else 1
            logo_height_calc = logo_max_height; logo_width_calc = logo_height_calc * aspect_ratio
            p_canvas.drawImage(logo_path, logo_x, logo_y_top - logo_height_calc, width=logo_width_calc, height=logo_height_calc, preserveAspectRatio=True, mask='auto', anchor='nw')
            text_x_offset_after_logo = logo_x + logo_width_calc + 3*mm
        except Exception:
            pass
    
    y_text_offset_clinic = logo_y_top - 5*mm 
    p_clinic_name = Paragraph(_("Y KHOA UNG BƯỚU CẦN THƠ"), style_clinic_main_title)
    p_clinic_name.wrapOn(p_canvas, page_width - text_x_offset_after_logo - 20*mm, 10*mm); p_clinic_name.drawOn(p_canvas, text_x_offset_after_logo, y_text_offset_clinic)
    y_text_offset_clinic -= 5*mm
    p_clinic_subname = Paragraph(_("PHÒNG XÉT NGHIỆM MEDIONCO"), style_clinic_sub_title)
    p_clinic_subname.wrapOn(p_canvas, page_width - text_x_offset_after_logo - 20*mm, 10*mm); p_clinic_subname.drawOn(p_canvas, text_x_offset_after_logo, y_text_offset_clinic)
    
    header_info_y_start = page_height - 38*mm 
    line_height_contact = 4*mm; left_col_x_contact = 20*mm; right_col_x_contact = 130*mm
    p_addr = Paragraph(_("Địa chỉ: Số 10, ĐS 5, Tổ 17, KV Bình Thường B, P. Long Tuyền, Q. Bình Thủy, TPCT."), style_header_info)
    p_addr.wrapOn(p_canvas, 105*mm, 10*mm); p_addr.drawOn(p_canvas, left_col_x_contact, header_info_y_start)
    
    id_phieu_text = _("ID Phiếu: {id_phieu}").format(id_phieu=lab_test.custom_id if lab_test.custom_id else f"#{lab_test.pk}")
    p_id_phieu = Paragraph(id_phieu_text, style_header_info); p_id_phieu.wrapOn(p_canvas, 70*mm, 10*mm); p_id_phieu.drawOn(p_canvas, right_col_x_contact, header_info_y_start)
    
    header_info_y_start -= line_height_contact
    p_phone = Paragraph(_("Điện thoại: 0917.575656."), style_header_info)
    p_phone.wrapOn(p_canvas, 105*mm, 10*mm); p_phone.drawOn(p_canvas, left_col_x_contact, header_info_y_start)
    ngay_dk_text = _("Ngày yêu cầu: {datetime}").format(datetime=timezone.localtime(lab_test.requested_at).strftime('%d/%m/%Y - %H:%M'))
    p_ngay_dk = Paragraph(ngay_dk_text, style_header_info); p_ngay_dk.wrapOn(p_canvas, 70*mm, 10*mm); p_ngay_dk.drawOn(p_canvas, right_col_x_contact, header_info_y_start)
    
    header_info_y_start -= line_height_contact
    p_web = Paragraph(_("Web: Ykhoaungbuoucantho.com.vn."), style_header_info)
    p_web.wrapOn(p_canvas, 105*mm, 10*mm); p_web.drawOn(p_canvas, left_col_x_contact, header_info_y_start)
    gio_xuat_text = _("Giờ xuất file: {datetime}").format(datetime=timezone.localtime(timezone.now()).strftime('%d/%m/%Y - %H:%M'))
    p_gio_xuat = Paragraph(gio_xuat_text, style_header_info); p_gio_xuat.wrapOn(p_canvas, 70*mm, 10*mm); p_gio_xuat.drawOn(p_canvas, right_col_x_contact, header_info_y_start)
    
    header_info_y_start -= line_height_contact
    p_email = Paragraph(_("Email: CSKH.MEDIONCO@GMAIL.COM."), style_header_info)
    p_email.wrapOn(p_canvas, 105*mm, 10*mm); p_email.drawOn(p_canvas, left_col_x_contact, header_info_y_start)

    y_title_kq = header_info_y_start - 12*mm
    p_title = Paragraph(_("KẾT QUẢ XÉT NGHIỆM {template_name}").format(template_name=lab_test.template.name.upper() if lab_test.template else ""), style_bold_large_centered)
    title_w, title_h = p_title.wrapOn(p_canvas, page_width - 40*mm, 20*mm)
    p_title.drawOn(p_canvas, (page_width - title_w) / 2, y_title_kq - title_h)

    y_position_patient = y_title_kq - title_h - 10*mm
    line_height_patient = 6*mm
    patient_obj = lab_test.medical_record.patient
    p_canvas.setFont(font_name, 10)
    p_canvas.drawString(20*mm, y_position_patient, _("Họ tên: {name}").format(name=patient_obj.full_name or ''))
    p_canvas.drawString(100*mm, y_position_patient, _("Mã BN: {ma_bn}").format(ma_bn=patient_obj.ma_benh_nhan or ''))
    
    y_position_patient -= line_height_patient
    p_canvas.drawString(20*mm, y_position_patient, _("Ngày sinh: {dob}").format(dob=patient_obj.date_of_birth.strftime('%d/%m/%Y') if patient_obj.date_of_birth else ''))
    p_canvas.drawString(100*mm, y_position_patient, _("Giới Tính: {gender}").format(gender=patient_obj.get_gender_display() or ''))

    y_position_patient -= line_height_patient
    p_diachi_text = _("Địa chỉ: {address}").format(address=patient_obj.address or '')
    p_diachi_para = Paragraph(p_diachi_text, style_patient_info)
    w_diachi, h_diachi = p_diachi_para.wrapOn(p_canvas, page_width - 40*mm - 80*mm, 15*mm)
    p_diachi_para.drawOn(p_canvas, 20*mm, y_position_patient - h_diachi + style_patient_info.leading*0.2)
    
    p_canvas.drawString(100*mm, y_position_patient, _("Điện thoại: {phone}").format(phone=patient_obj.phone or ''))
    y_position_patient -= (max(h_diachi, style_patient_info.leading) + 2*mm)
    
    bs_chi_dinh_text = _("BS Chỉ định: {name}").format(name=lab_test.requested_by.get_full_name() if lab_test.requested_by else 'N/A')
    p_canvas.drawString(20*mm, y_position_patient, bs_chi_dinh_text)
    y_position_patient -= line_height_patient

    p_chandoan_text = _("Chẩn đoán (HSBA): {diagnosis}").format(diagnosis=lab_test.medical_record.diagnosis or _('Chưa có'))
    p_chandoan_para = Paragraph(p_chandoan_text, style_patient_info)
    w_cd, h_cd = p_chandoan_para.wrapOn(p_canvas, page_width - 40*mm, 15*mm)
    p_chandoan_para.drawOn(p_canvas, 20*mm, y_position_patient - h_cd + style_patient_info.leading*0.2)
    y_position_for_table = y_position_patient - h_cd - 7*mm

    table_data = [
        [Paragraph(_("XÉT NGHIỆM"), style_bold_small), Paragraph(_("KẾT QUẢ"), style_bold_small), Paragraph(_("KHOẢNG THAM CHIẾU"), style_bold_small), Paragraph(_("ĐƠN VỊ"), style_bold_small)]
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
        table_data.append([Paragraph(_("Chưa có kết quả chi tiết cho phiếu xét nghiệm này."), style_normal), "", "", ""])
    
    num_data_rows = results.count() if results.exists() else 1
    min_table_rows = 5
    num_empty_rows_needed_in_data = min_table_rows - 1 - num_data_rows
    for _i in range(max(0, num_empty_rows_needed_in_data)):
        table_data.append(['', '', '', ''])

    table_width_pdf = page_width - 40*mm
    col_widths_pdf = [table_width_pdf*0.38, table_width_pdf*0.20, table_width_pdf*0.27, table_width_pdf*0.15]
    result_table = Table(table_data, colWidths=col_widths_pdf, repeatRows=1)
    result_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#D0D0D0")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), font_name_bold), ('FONTSIZE', (0,0), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3), ('TOPPADDING', (0,0), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('LEFTPADDING', (0,0), (-1,-1), 3), ('RIGHTPADDING', (0,0), (-1,-1), 3),
    ]))
    
    frame_x_pdf = 20*mm; frame_y_bottom_margin_pdf = 60*mm
    frame_width_pdf = page_width - 40*mm; frame_height_pdf = y_position_for_table - frame_y_bottom_margin_pdf
    try:
        w_table, h_table = result_table.wrapOn(p_canvas, frame_width_pdf, frame_height_pdf)
        if h_table <= frame_height_pdf :
            result_table.drawOn(p_canvas, frame_x_pdf, y_position_for_table - h_table)
        else:
            p_canvas.drawString(20*mm, y_position_for_table - 5*mm, _("LƯU Ý: Kết quả quá dài, chức năng ngắt trang tự động cần hoàn thiện."))
    except Exception:
        p_canvas.drawString(20*mm, y_position_for_table - 5*mm, _("Lỗi khi vẽ bảng kết quả."))

    y_kiem_duyet_bottom = 45*mm 
    p_kiem_duyet = Paragraph(_("Kết quả đã được kiểm duyệt /QA"), style_normal)
    p_kiem_duyet_w, p_kiem_duyet_h = p_kiem_duyet.wrapOn(p_canvas, 80*mm, 20*mm) 
    p_kiem_duyet.drawOn(p_canvas, 20*mm, y_kiem_duyet_bottom)

    signature_area_width_footer = 70*mm 
    signature_area_x_start_footer = page_width - 20*mm - signature_area_width_footer

    current_time_footer_val = timezone.localtime(timezone.now())
    ngay_thang_nam_tp_footer_str_val = _("TP. Cần Thơ, ngày {day} tháng {month} năm {year}").format(day=current_time_footer_val.day, month=current_time_footer_val.month, year=current_time_footer_val.year)
    p_ngay_tp = Paragraph(ngay_thang_nam_tp_footer_str_val, style_normal)
    ngay_tp_w_val, ngay_tp_h_val = p_ngay_tp.wrapOn(p_canvas, signature_area_width_footer, 20*mm) 
    y_ngay_tp_bottom_val = y_kiem_duyet_bottom 
    x_ngay_tp_val = signature_area_x_start_footer + (signature_area_width_footer - ngay_tp_w_val) / 2
    p_ngay_tp.drawOn(p_canvas, x_ngay_tp_val, y_ngay_tp_bottom_val)

    p_pxn_title = Paragraph(_("PHÒNG XÉT NGHIỆM"), style_bold_small)
    pxn_title_w_val, pxn_title_h_val = p_pxn_title.wrapOn(p_canvas, signature_area_width_footer, 20*mm)
    line_spacing_1_val = 1*mm 
    y_pxn_title_base_y = y_ngay_tp_bottom_val - ngay_tp_h_val - line_spacing_1_val 
    x_pxn_title_centered = signature_area_x_start_footer + (signature_area_width_footer - pxn_title_w_val) / 2
    # <<< THAY ĐỔI TỌA ĐỘ X CHO "PHÒNG XÉT NGHIỆM" >>>
    x_pxn_title_adjusted = x_pxn_title_centered + 1.5*cm 
    p_pxn_title.drawOn(p_canvas, x_pxn_title_adjusted, y_pxn_title_base_y - pxn_title_h_val)

    p_ky_ten = Paragraph(_("(Ký, đóng dấu và ghi rõ họ tên)"), style_header_info)
    ky_ten_w_val, ky_ten_h_val = p_ky_ten.wrapOn(p_canvas, signature_area_width_footer, 20*mm)
    line_spacing_2_val = 1*mm
    y_ky_ten_base_y = y_pxn_title_base_y - pxn_title_h_val - line_spacing_2_val # Tính từ y của "PHÒNG XÉT NGHIỆM"
    x_ky_ten_centered = signature_area_x_start_footer + (signature_area_width_footer - ky_ten_w_val) / 2
    # <<< THAY ĐỔI TỌA ĐỘ X CHO "(Ký, đóng dấu...)" >>>
    x_ky_ten_adjusted = x_ky_ten_centered + 1*cm
    p_ky_ten.drawOn(p_canvas, x_ky_ten_adjusted, y_ky_ten_base_y - ky_ten_h_val)

    p_ghichu_cuoi = Paragraph(_("*Ghi chú: Kết quả in đậm là ngoài khoảng tham chiếu, kết quả chỉ có giá trị trên mẫu thử. Tô đậm bên trái -Thấp. Tô đậm bên phải-Cao."), style_footer_note)
    _w_gc_val, h_gc_val = p_ghichu_cuoi.wrapOn(p_canvas, page_width - 40*mm, 20*mm)
    p_ghichu_cuoi.drawOn(p_canvas, 20*mm, 15*mm)

    p_slogan = Paragraph(_("TẦM SOÁT SỚM - SỐNG KHỎE MẠNH"), style_slogan)
    _w_sl_val, h_sl_val = p_slogan.wrapOn(p_canvas, page_width - 40*mm, 10*mm)
    p_slogan.drawOn(p_canvas, 20*mm, 15*mm - h_gc_val - 1*mm)

    p_canvas.save()
    pdf = buffer.getvalue()
    buffer.close()
    response = HttpResponse(content_type='application/pdf')
    
    patient_name_for_file = "".join(filter(str.isalnum, lab_test.medical_record.patient.full_name.replace(' ', '_'))) if lab_test.medical_record and lab_test.medical_record.patient and lab_test.medical_record.patient.full_name else "UnknownPatient"
    safe_filename = f"KQXT_{patient_name_for_file}_{lab_test.custom_id if lab_test.custom_id else lab_test.pk}.pdf"
    response['Content-Disposition'] = f'inline; filename="{safe_filename}"'
    response.write(pdf)

    if lab_test.print_status == LabTest.PrintStatus.PENDING and \
       (results.exists() or (lab_test.template and not lab_test.template.fields.exists())):
        lab_test.print_status = LabTest.PrintStatus.PRINTED
        lab_test.last_print_date = timezone.now()
        lab_test.save(update_fields=['print_status', 'last_print_date'])

    return response
