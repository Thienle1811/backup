# apps/labtests/management/commands/populate_lab_templates.py
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from apps.labtests.models import LabTestTemplate, LabTestTemplateField
# Giả sử CustomUser được dùng cho created_by, nếu không có user cụ thể, có thể bỏ qua hoặc gán None
# from django.contrib.auth import get_user_model 
# User = get_user_model()

# Dữ liệu mẫu xét nghiệm và chỉ số (chuyển đổi từ predefinedFieldsData và BASE_TEST_TYPES)
# BASE_TEST_TYPES cung cấp tên hiển thị cho LabTestTemplate
# predefinedFieldsData cung cấp các chỉ số cho mỗi loại
PREDEFINED_TEMPLATES_DATA = {
    'HUYET_HOC_TONG_QUAT': {
        'display_name': _('HUYẾT HỌC (Tổng phân tích tế bào máu)'),
        'description': _('Xét nghiệm tổng phân tích tế bào máu ngoại vi.'),
        'fields': [
            {'name': 'Số lượng bạch cầu (WBC)', 'unit': 'K/µL', 'ref_range': '4.8-10.0'},
            {'name': 'NEU#', 'unit': 'K/µL', 'ref_range': '1.8-6.4'},
            {'name': 'LYM#', 'unit': 'K/µL', 'ref_range': '1.0-3.3'},
            {'name': 'MONO#', 'unit': 'K/µL', 'ref_range': '0.1-0.6'},
            {'name': 'EOS#', 'unit': 'K/µL', 'ref_range': '0.0-0.7'},
            {'name': 'BASO#', 'unit': 'K/µL', 'ref_range': '0.0-0.1'},
            {'name': 'NEU%', 'unit': '%', 'ref_range': '45.0-75.0'},
            {'name': 'LYM%', 'unit': '%', 'ref_range': '20.0-45.0'},
            {'name': 'MONO%', 'unit': '%', 'ref_range': '1.7-9.3'},
            {'name': 'EOS%', 'unit': '%', 'ref_range': '0.0-6.0'},
            {'name': 'BASO%', 'unit': '%', 'ref_range': '0.0-2.0'},
            {'name': 'Số lượng hồng cầu (RBC)', 'unit': 'M/µL', 'ref_range': '3.8-5.8'},
            {'name': 'HGB (Huyết sắc tố)', 'unit': 'g/dL', 'ref_range': '11.0-16.0'}, # Sửa lại tên cho rõ
            {'name': 'HCT (Hematocrit)', 'unit': '%', 'ref_range': '35.0-52.0'}, # Sửa lại tên
            {'name': 'MCV (Thể tích trung bình HC)', 'unit': 'fL', 'ref_range': '80.0-100.0'}, # Sửa lại tên
            {'name': 'MCH (Lượng HSTB HC)', 'unit': 'pg', 'ref_range': '27.0-32.0'}, # Sửa lại tên
            {'name': 'MCHC (Nồng độ HSTB HC)', 'unit': 'g/dL', 'ref_range': '32.0-36.0'}, # Sửa lại tên
            {'name': 'RDW (Dải phân bố HC)', 'unit': '%', 'ref_range': '11.5-14.5'}, # Sửa lại tên
            {'name': 'Số lượng tiểu cầu (PLT)', 'unit': 'K/µL', 'ref_range': '150-400'},
            {'name': 'MPV (Thể tích trung bình TC)', 'unit': 'fL', 'ref_range': '7.0-12.0'}, # Sửa lại tên
            {'name': 'PCT (Thể tích khối TC)', 'unit': '%', 'ref_range': '0.1-0.35'}, # Sửa lại tên
            {'name': 'PDW (Dải phân bố TC)', 'unit': '%', 'ref_range': '9-25'} # Sửa lại tên
        ]
    },
    'HUYET_HOC_DONG_MAU': {
        'display_name': _('HUYẾT HỌC (Đông máu)'),
        'description': _('Xét nghiệm các chỉ số đông máu.'),
        'fields': [
            {'name': 'Thời gian Prothrombin (PT)', 'unit': 'Giây', 'ref_range': '10-15'}, # Rút gọn tên
            {'name': 'Định lượng Fibrinogen', 'unit': 'mg/dl', 'ref_range': '200-400'},
            {'name': 'Thời gian thromboplastin hoạt hoá từng phần (APTT)', 'unit': 'Giây', 'ref_range': '<40'}
        ]
    },
    'SINH_HOA': {
        'display_name': _('SINH HÓA MÁU'), # Đổi tên cho rõ hơn
        'description': _('Xét nghiệm các chỉ số sinh hóa máu.'),
        'fields': [
            {'name': 'Creatinin', 'unit': 'µmol/L', 'ref_range': '(Nam: 62-120, Nữ: 44-100)'},
            {'name': 'eGFR (MDRD)', 'unit': 'mL/phut/1.73m2', 'ref_range': '>60 (Tùy độ tuổi)'}, # Thêm giá trị tham khảo
            {'name': 'Urea', 'unit': 'mmol/L', 'ref_range': '2.5-7.5'},
            {'name': 'SGOT (AST)', 'unit': 'U/L', 'ref_range': '<37'},
            {'name': 'SGPT (ALT)', 'unit': 'U/L', 'ref_range': '<40'},
            {'name': 'Acid Uric', 'unit': 'µmol/L', 'ref_range': '(Nam: 180-420, Nữ: 150-360)'}, # Sửa tên
            {'name': 'Cholesterol Toàn phần', 'unit': 'mmol/L', 'ref_range': '3.9-5.2'}, # Sửa tên
            {'name': 'Triglycerides', 'unit': 'mmol/L', 'ref_range': '0.46-1.88'},
            {'name': 'LDL-Cholesterol', 'unit': 'mmol/L', 'ref_range': '<3.4'}, # Sửa tên
            {'name': 'HDL-Cholesterol', 'unit': 'mmol/L', 'ref_range': '>0.9'}, # Sửa tên
            {'name': 'GGT', 'unit': 'UI/L', 'ref_range': 'Nam: 11-50, Nữ: 7-32'},
            {'name': 'Bilirubin Toàn phần (T.P)', 'unit': 'µmol/L', 'ref_range': '0-17'}, # Sửa tên
            {'name': 'Bilirubin Gián tiếp (I.P)', 'unit': 'µmol/L', 'ref_range': '0.0-12.62'}, # Sửa tên
            {'name': 'Albumin', 'unit': 'g/L', 'ref_range': '35-50'},
            {'name': 'Protein Toàn phần (T.P)', 'unit': 'g/L', 'ref_range': '60-80'}, # Sửa tên
            {'name': 'Amylase', 'unit': 'UI/L', 'ref_range': '22-100'},
            {'name': 'Glucose (Đường huyết)', 'unit': 'mmol/L', 'ref_range': '3.9-6.4'}, # Sửa tên
            {'name': 'Na+ (Natri)', 'unit': 'mmol/L', 'ref_range': '135-145'}, # Sửa tên
            {'name': 'K+ (Kali)', 'unit': 'mmol/L', 'ref_range': '3.5-5.0'}, # Sửa tên
            {'name': 'Cl- (Clo)', 'unit': 'mmol/L', 'ref_range': '98-108'}, # Sửa tên
            {'name': 'Calci ion hóa', 'unit': 'mmol/L', 'ref_range': '1.15-1.35'}
        ]
    },
    'MIEN_DICH': {
        'display_name': _('MIỄN DỊCH - NỘI TIẾT'), # Đổi tên
        'description': _('Xét nghiệm các chỉ số miễn dịch và nội tiết.'),
        'fields': [
            {'name': 'AFP (Định lượng)', 'unit': 'ng/ml', 'ref_range': '<10.0'},
            {'name': 'CA 125', 'unit': 'U/mL', 'ref_range': '<35'},
            {'name': 'CA 15-3', 'unit': 'U/mL', 'ref_range': '<28'}, # Sửa tên
            {'name': 'CA 19-9', 'unit': 'UI/mL', 'ref_range': '<37'}, # Sửa tên
            {'name': 'TSH', 'unit': 'µUI/mL', 'ref_range': '0.38-4.31'},
            {'name': 'Free T3 (FT3)', 'unit': 'pg/mL', 'ref_range': '2.0-4.4'}, # Sửa tên
            {'name': 'Free T4 (FT4)', 'unit': 'ng/dL', 'ref_range': '0.82-1.63'}, # Sửa tên
            {'name': 'Ferritin', 'unit': 'ng/ml', 'ref_range': '11-300'},
            {'name': 'CEA', 'unit': 'ng/ml', 'ref_range': '<5.0'},
            {'name': 'PSA Toàn phần', 'unit': 'ng/ml', 'ref_range': '0.0-4.0'}, # Sửa tên
            {'name': 'BNP (B-Type Natriuretic Peptide)', 'unit': 'pg/mL', 'ref_range': '<100'} # Sửa tên
        ]
    },
    'NUOC_TIEU': {
        'display_name': _('NƯỚC TIỂU (Tổng phân tích)'),
        'description': _('Xét nghiệm tổng phân tích nước tiểu.'),
        'fields': [
            {'name': 'pH', 'unit': '', 'ref_range': '5.0-7.5'},
            {'name': 'Nitrite (NIT)', 'unit': '', 'ref_range': 'Âm tính'}, # Sửa tên
            {'name': 'Glucose Nước tiểu (GLU)', 'unit': 'mg/dL', 'ref_range': 'Âm tính'}, # Sửa tên
            {'name': 'Tỷ trọng (SG)', 'unit': '', 'ref_range': '1.005-1.030'}, # Sửa tên
            {'name': 'Máu (BLO)', 'unit': 'Ery/µL', 'ref_range': 'Âm tính'}, # Sửa tên
            {'name': 'Protein Nước tiểu (PRO)', 'unit': 'mg/dL', 'ref_range': 'Âm tính'}, # Sửa tên
            {'name': 'Bilirubin Nước tiểu (BIL)', 'unit': 'mg/dL', 'ref_range': 'Âm tính'}, # Sửa tên
            {'name': 'Urobilinogen (URO)', 'unit': 'mg/dL', 'ref_range': '0.2-1.0'}, # Sửa tên
            {'name': 'Ketone (KET)', 'unit': 'mg/dL', 'ref_range': 'Âm tính'}, # Sửa tên
            {'name': 'Bạch cầu Nước tiểu (LEU)', 'unit': 'Leu/µL', 'ref_range': 'Âm tính'}, # Sửa tên
            {'name': 'Micro Albumin niệu (MAU)', 'unit': 'mg/L', 'ref_range': '<20'} # Gộp và sửa tên
        ]
    }
}


class Command(BaseCommand):
    help = 'Populates the database with predefined LabTestTemplates and LabTestTemplateFields.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting to populate lab test templates...'))
        
        # Lấy người dùng admin đầu tiên để gán cho created_by, hoặc bỏ qua nếu không quan trọng
        # admin_user = User.objects.filter(is_superuser=True).first()

        for template_key, template_data in PREDEFINED_TEMPLATES_DATA.items():
            template_name = str(template_data['display_name']) # Chuyển lazy string thành string
            description = str(template_data.get('description', ''))

            template_obj, created = LabTestTemplate.objects.update_or_create(
                name=template_name,
                defaults={
                    'description': description,
                    'is_active': True,
                    # 'created_by': admin_user, # Bỏ comment nếu muốn gán người tạo
                }
            )

            if created:
                self.stdout.write(self.style.SUCCESS(f"Successfully created LabTestTemplate: '{template_name}'"))
            else:
                self.stdout.write(self.style.WARNING(f"LabTestTemplate '{template_name}' already exists. Updated if necessary."))

            for order_index, field_data in enumerate(template_data['fields']):
                field_name_str = str(field_data['name'])
                
                # Kiểm tra xem field đã tồn tại với tên đó cho template này chưa
                # Nếu muốn cập nhật dựa trên tên, thì dùng field_name cho defaults và name cho lookup
                field_obj, field_created = LabTestTemplateField.objects.update_or_create(
                    template=template_obj,
                    field_name=field_name_str, # Dùng field_name làm khóa để update_or_create
                    defaults={
                        'unit': field_data.get('unit', ''),
                        'reference_range_text': field_data.get('ref_range', ''),
                        'field_order': field_data.get('order', order_index + 1), # Sử dụng order nếu có, nếu không thì theo thứ tự
                        'result_guidance': field_data.get('result_guidance', '') # Thêm result_guidance nếu có
                        # 'normal_min', 'normal_max' có thể thêm nếu có trong field_data
                    }
                )
                if field_created:
                    self.stdout.write(self.style.SUCCESS(f"  - Added field: '{field_name_str}' to '{template_name}'"))
                # else:
                    # self.stdout.write(self.style.NOTICE(f"  - Field '{field_name_str}' for '{template_name}' already exists. Updated if necessary."))

        self.stdout.write(self.style.SUCCESS('Finished populating lab test templates.'))

