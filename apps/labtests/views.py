        # apps/labtests/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Max
from django.db import transaction
from django.http import JsonResponse
from .models import LabTestTemplate, LabTestTemplateField, LabTest, LabTestResultValue, LabTestVersion
from .forms import (
            LabTestTemplateForm, 
            LabTestTemplateFieldFormSet, 
            LabTestForm,
            LabTestResultValueFormSet
        )
from django.utils import timezone

        # --- Views cho LabTestTemplate (giữ nguyên) ---
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
                'lab_test_templates': templates, 'page_title': 'Danh sách Mẫu Xét nghiệm',
                'search_query': query, 'template_count': templates.count()
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
                            messages.success(request, f"Đã tạo mẫu xét nghiệm '{lab_test_template.name}' thành công!")
                            return redirect('labtests:lab_test_template_list')
                    except Exception as e:
                        messages.error(request, f"Có lỗi xảy ra khi lưu mẫu xét nghiệm: {e}")
                        print(f"Lỗi Exception khi lưu mẫu xét nghiệm: {e}") 
                else:
                    print("Lỗi Form Mẫu Xét Nghiệm (POST):", form.errors.as_json(escape_html=True))
                    print("Lỗi Formset Chỉ Số (POST):", formset.errors)
                    print("Lỗi Formset Non-form (Chỉ Số) (POST):", formset.non_form_errors())
                    messages.error(request, "Vui lòng sửa các lỗi trong form chính và/hoặc các chỉ số của mẫu xét nghiệm.")
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
                            messages.success(request, f"Đã cập nhật mẫu xét nghiệm '{updated_template.name}' thành công!")
                            return redirect('labtests:lab_test_template_list')
                    except Exception as e:
                        messages.error(request, f"Có lỗi xảy ra khi cập nhật mẫu xét nghiệm: {e}")
                        print(f"Lỗi Exception khi cập nhật mẫu xét nghiệm: {e}")
                else:
                    print("Lỗi Form Cập Nhật Mẫu Xét Nghiệm (POST):", form.errors.as_json(escape_html=True))
                    print("Lỗi Formset Cập Nhật Chỉ Số (POST):", formset.errors)
                    print("Lỗi Formset Non-form Cập Nhật (Chỉ Số) (POST):", formset.non_form_errors())
                    messages.error(request, "Vui lòng sửa các lỗi trong form chính và/hoặc các chỉ số của mẫu xét nghiệm.")
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
def lab_test_template_delete(request, pk):
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


        # --- Views cho LabTest và LabTestResultValue ---
@login_required
def ajax_get_template_fields(request, template_id):
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
                                results = result_formset.save(commit=False)
                                for result_value_instance in results:
                                    if request.user.is_authenticated:
                                        result_value_instance.entered_by = request.user
                                    result_value_instance.save() 
                                
                                lab_test.results_updated_at = timezone.now()
                                
                                first_version = LabTestVersion.objects.create(
                                    lab_test=lab_test, version_number=1,
                                    result_snapshot=f"Kết quả ban đầu cho {lab_test.template.name}",
                                    changed_by=request.user,
                                    change_reason="Phiếu xét nghiệm được tạo và nhập kết quả."
                                )
                                lab_test.latest_version = first_version
                                lab_test.save()

                                messages.success(request, f"Đã lưu kết quả xét nghiệm cho HSBA ID {lab_test.medical_record.id} thành công!")
                                return redirect('labtests:lab_test_list')
                        except Exception as e:
                            messages.error(request, f"Lỗi khi lưu (sau valid): {e}")
                            print(f"Lỗi Exception khi lưu LabTest/Results: {e}")
                    else: 
                        messages.error(request, "Vui lòng sửa các lỗi trong phần nhập kết quả chi tiết.")
                        print("LabTest Form errors (đã valid):", lab_test_form.errors.as_json(escape_html=True))
                        print("Result Formset errors (POST):", result_formset.errors)
                        print("Result Formset non-form errors (POST):", result_formset.non_form_errors())
                else: 
                    messages.error(request, "Vui lòng sửa các lỗi trong thông tin phiếu xét nghiệm.")
                    print("LabTest Form errors (POST):", lab_test_form.errors.as_json(escape_html=True))
                    if result_formset.is_bound:
                         print("Result Formset errors (khi lab_test_form lỗi) (POST):", result_formset.errors)
                         print("Result Formset non-form errors (khi lab_test_form lỗi) (POST):", result_formset.non_form_errors())
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
def lab_test_list(request):
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

@login_required
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

                            results = result_formset.save(commit=False)
                            significant_change_in_results = False
                            for result_value_instance in results:
                                if result_formset.has_changed() or not result_value_instance.pk : 
                                    if request.user.is_authenticated:
                                        result_value_instance.entered_by = request.user
                                    significant_change_in_results = True
                                result_value_instance.save()
                            
                            if significant_change_in_results:
                                last_version_number = updated_lab_test.versions.aggregate(max_version=Max('version_number'))['max_version'] or 0
                                new_version_number = last_version_number + 1
                                current_results_snapshot = "; ".join([f"{rv.template_field.field_name}: {rv.value or ''}" for rv in updated_lab_test.result_values.all().order_by('template_field__field_order')])
                                new_version = LabTestVersion.objects.create(
                                    lab_test=updated_lab_test, version_number=new_version_number,
                                    result_snapshot=current_results_snapshot, 
                                    changed_by=request.user,
                                    change_reason="Kết quả xét nghiệm được cập nhật."
                                )
                                updated_lab_test.latest_version = new_version
                                updated_lab_test.save(update_fields=['latest_version', 'results_updated_at'])
                            messages.success(request, f"Đã cập nhật kết quả xét nghiệm cho HSBA ID {updated_lab_test.medical_record.id} thành công!")
                            return redirect('labtests:lab_test_list')
                    except Exception as e:
                        messages.error(request, f"Lỗi khi cập nhật kết quả: {e}")
                        print(f"Lỗi Exception khi cập nhật LabTest/Results: {e}")
                else:
                    messages.error(request, "Vui lòng sửa các lỗi trong form và/hoặc kết quả.")
                    print("LabTest Form errors (update):", lab_test_form.errors.as_json(escape_html=True))
                    print("Result Formset errors (update):", result_formset.errors)
                    print("Result Formset non-form errors (update):", result_formset.non_form_errors())
            else: 
                lab_test_form = LabTestForm(instance=lab_test_instance, prefix='labtest')
                # Khởi tạo formset với các result_values hiện có
                # Đảm bảo các form con được tạo đúng thứ tự của template_field
                initial_formset_data = []
                if lab_test_instance.template:
                    for field_template in lab_test_instance.template.fields.order_by('field_order'):
                        result_value_obj = LabTestResultValue.objects.filter(lab_test=lab_test_instance, template_field=field_template).first()
                        initial_data_for_form = {
                            'template_field': field_template.pk, # Quan trọng để Django biết field nào
                            'value': result_value_obj.value if result_value_obj else '',
                            'comment': result_value_obj.comment if result_value_obj else ''
                        }
                        # Thêm các thông tin hiển thị readonly cho template (nếu cần)
                        # initial_data_for_form['template_field_name'] = field_template.field_name
                        # initial_data_for_form['template_field_unit'] = field_template.unit
                        # initial_data_for_form['template_field_ref_range'] = field_template.reference_range_text
                        initial_formset_data.append(initial_data_for_form)

                result_formset = LabTestResultValueFormSet(instance=lab_test_instance, prefix='results', initial=initial_formset_data)
            
            context = {
                'lab_test_form': lab_test_form, 'result_formset': result_formset,
                'lab_test_instance': lab_test_instance, 
                'page_title': f'Sửa/Xem Kết quả Xét nghiệm: {lab_test_instance.template.name}',
                'form_title': f'Kết quả cho {lab_test_instance.medical_record.patient.full_name} (HSBA: {lab_test_instance.medical_record.id})',
                'submit_button_text': 'Lưu Thay đổi Kết quả'
            }
            return render(request, 'labtests/lab_test_form_and_results.html', context)

@login_required # View mới để xóa LabTest
def lab_test_delete(request, pk):
            lab_test_instance = get_object_or_404(LabTest, pk=pk)
            lab_test_display = f"phiếu xét nghiệm #{lab_test_instance.pk} ({lab_test_instance.template.name}) cho bệnh nhân {lab_test_instance.medical_record.patient.full_name}"

            if request.method == 'POST':
                try:
                    lab_test_instance.delete() # Sẽ xóa cả LabTestResultValue và LabTestVersion liên quan do on_delete=CASCADE
                    messages.success(request, f"Đã xóa {lab_test_display} thành công!")
                    return redirect('labtests:lab_test_list')
                except Exception as e:
                    messages.error(request, f"Có lỗi xảy ra khi xóa phiếu xét nghiệm: {e}")
                    return redirect('labtests:lab_test_list')

            context = {
                'lab_test_instance': lab_test_instance,
                'page_title': 'Xác nhận Xóa Phiếu Xét nghiệm',
                'confirm_message': f"Bạn có chắc chắn muốn xóa {lab_test_display} không? Hành động này không thể hoàn tác."
            }
            return render(request, 'labtests/lab_test_confirm_delete.html', context)

        