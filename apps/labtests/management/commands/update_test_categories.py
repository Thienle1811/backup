from django.core.management.base import BaseCommand
from django.db import transaction
from apps.labtests.models import TestCategory, TestItem

class Command(BaseCommand):
    help = 'Update test categories and their items'

    def handle(self, *args, **options):
        with transaction.atomic():
            # Define the test categories and their items
            categories_data = {
                'Nước Tiểu': [
                    {'name': 'pH', 'reference_range': '5.0 - 7.5', 'unit': ''},
                    {'name': 'Nitrite', 'reference_range': '', 'unit': ''},
                    {'name': 'Glucose NT', 'reference_range': '', 'unit': 'mg/dL'},
                    {'name': 'SG', 'reference_range': '1.005 - 1.030', 'unit': ''},
                    {'name': 'Blood', 'reference_range': '', 'unit': 'Ery/µL'},
                    {'name': 'Protein', 'reference_range': '', 'unit': 'mg/dL'},
                    {'name': 'Bilirubin', 'reference_range': '', 'unit': 'mg/dL'},
                    {'name': 'Urobilinogen', 'reference_range': '0.2 - 1.0', 'unit': 'mg/dL'},
                    {'name': 'Ketone', 'reference_range': '', 'unit': 'mg/dL'},
                    {'name': 'Leukocytes', 'reference_range': '', 'unit': 'Leu/µL'},
                    {'name': 'Định lượng Micro Albumin niệu', 'reference_range': '≤20', 'unit': 'mg/L'},
                    {'name': 'Định lượng Microalbumin niệu (MAU)', 'reference_range': '<20', 'unit': 'mg/L'},
                ],
                'Miễn Dịch': [
                    {'name': 'AFP (Định lượng)', 'reference_range': '', 'unit': 'ng/ml'},
                    {'name': 'CA 125', 'reference_range': '', 'unit': 'U/mL'},
                    {'name': 'CA 153', 'reference_range': '', 'unit': 'U/mL'},
                    {'name': 'CA 19.9', 'reference_range': '', 'unit': 'UI/mL'},
                    {'name': 'TSH', 'reference_range': '0.38 - 4.31', 'unit': 'µUI/mL'},
                    {'name': 'Free T3', 'reference_range': '2.0 - 4.4', 'unit': 'pg/mL'},
                    {'name': 'Free T4', 'reference_range': '0.82 - 1.63', 'unit': 'ng/dL'},
                    {'name': 'Ferritin', 'reference_range': '11 - 300', 'unit': 'ng/mL'},
                    {'name': 'CEA', 'reference_range': '', 'unit': 'ng/mL'},
                    {'name': 'PSA Total', 'reference_range': '0.0 - 4.0', 'unit': 'ng/ml'},
                    {'name': 'Định lượng BNP (B-Type Natriuretic Peptide) [Máu]', 'reference_range': '<100', 'unit': 'pg/mL'},
                ],
                'Huyết Học': [
                    {'name': 'Số lượng bạch cầu (WBC)', 'reference_range': '4.8 - 10.0', 'unit': 'K/µL'},
                    {'name': 'NEU#', 'reference_range': '1.8 - 6.4', 'unit': 'K/µL'},
                    {'name': 'LYM#', 'reference_range': '0.1 - 0.6', 'unit': 'K/µL'},
                    {'name': 'MONO#', 'reference_range': '0.0 - 0.7', 'unit': 'K/µL'},
                    {'name': 'EOS#', 'reference_range': '0.0 - 0.7', 'unit': 'K/µL'},
                    {'name': 'BASO#', 'reference_range': '0.0 - 0.1', 'unit': 'K/µL'},
                    {'name': 'NEU%', 'reference_range': '45.0 - 75.0', 'unit': '%'},
                    {'name': 'LYM%', 'reference_range': '20.0 - 45.0', 'unit': '%'},
                    {'name': 'MONO%', 'reference_range': '1.7 - 9.3', 'unit': '%'},
                    {'name': 'EOS%', 'reference_range': '0.0 - 6.0', 'unit': '%'},
                    {'name': 'BASO%', 'reference_range': '0.0 - 2.0', 'unit': '%'},
                    {'name': 'Số lượng hồng cầu (RBC)', 'reference_range': '3.8 - 5.8', 'unit': 'M/µL'},
                    {'name': 'HGB', 'reference_range': '11.0 - 16.0', 'unit': 'g/dL'},
                    {'name': 'HCT', 'reference_range': '35.0 - 52.0', 'unit': '%'},
                    {'name': 'MCV', 'reference_range': '80.0 - 100.0', 'unit': 'fL'},
                    {'name': 'MCH', 'reference_range': '27.0 - 32.0', 'unit': 'pg'},
                    {'name': 'MCHC', 'reference_range': '32.0 - 36.0', 'unit': 'g/dL'},
                    {'name': 'RDW', 'reference_range': '11.5 - 14.5', 'unit': '%'},
                    {'name': 'Số lượng tiểu cầu (PLT)', 'reference_range': '150 - 400', 'unit': 'K/µL'},
                    {'name': 'MPV', 'reference_range': '7.0 - 12.0', 'unit': 'fL'},
                    {'name': 'PCT', 'reference_range': '0.1 - 0.35', 'unit': '%'},
                    {'name': 'PDW', 'reference_range': '9 - 25', 'unit': '%'},
                    {'name': 'Thời gian Prothrombin (PT)', 'reference_range': '10 - 15', 'unit': 'Giây'},
                    {'name': 'Định lượng Fibrinogen', 'reference_range': '200 - 400', 'unit': 'mg/dL'},
                    {'name': 'Thời gian thromboplastin hoạt hóa từng phần (APTT)', 'reference_range': '<40', 'unit': 'Giây'},
                ],
                'Sinh Hóa': [
                    {'name': 'Creatinin', 'reference_range': 'Nam: 62 - 120 / Nữ: 44 - 100', 'unit': 'µmol/L'},
                    {'name': 'eGFR (MDRD)', 'reference_range': '', 'unit': 'mL/phút/1.73m2'},
                    {'name': 'Urea', 'reference_range': '2.5 - 7.5', 'unit': 'mmol/L'},
                    {'name': 'SGOT (AST)', 'reference_range': '<37', 'unit': 'U/L'},
                    {'name': 'SGPT (ALT)', 'reference_range': '<40', 'unit': 'U/L'},
                    {'name': 'Uric Acid', 'reference_range': 'Nam: 180 - 420 / Nữ: 150 - 360', 'unit': 'µmol/L'},
                    {'name': 'Cholesterol Total', 'reference_range': '3.9 - 5.2', 'unit': 'mmol/L'},
                    {'name': 'Triglycerides', 'reference_range': '0.46 - 1.88', 'unit': 'mmol/L'},
                    {'name': 'LDL Cholesterol', 'reference_range': '<3.4', 'unit': 'mmol/L'},
                    {'name': 'HDL Cholesterol', 'reference_range': '>0.9', 'unit': 'mmol/L'},
                    {'name': 'GGT', 'reference_range': 'Nam: 11 - 50 / Nữ: 7 - 32', 'unit': 'UI/L'},
                    {'name': 'Bilirubin T', 'reference_range': '0 - 17', 'unit': 'µmol/L'},
                    {'name': 'Bilirubin I', 'reference_range': '0.0 - 12.62', 'unit': 'µmol/L'},
                    {'name': 'Albumin', 'reference_range': '35 - 50', 'unit': 'g/L'},
                    {'name': 'Protein TP', 'reference_range': '60 - 80', 'unit': 'g/L'},
                    {'name': 'Amylase', 'reference_range': '22 - 100', 'unit': 'UI/L'},
                    {'name': 'Glucose', 'reference_range': '3.9 - 6.4', 'unit': 'mmol/L'},
                    {'name': 'Na+', 'reference_range': '135 - 145', 'unit': 'mmol/L'},
                    {'name': 'K+', 'reference_range': '3.5 - 5.0', 'unit': 'mmol/L'},
                    {'name': 'Cl-', 'reference_range': '98 - 108', 'unit': 'mmol/L'},
                    {'name': 'Calci ion hóa', 'reference_range': '1.15 - 1.35', 'unit': 'mmol/L'},
                ],
            }

            # Update or create categories and their items
            for category_name, items in categories_data.items():
                # Get or create category
                category, created = TestCategory.objects.get_or_create(
                    name=category_name,
                    defaults={'is_active': True}
                )
                
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created category: {category_name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Found existing category: {category_name}'))
                
                # Delete existing items for this category
                category.items.all().delete()
                
                # Create new items
                for order, item_data in enumerate(items, 1):
                    TestItem.objects.create(
                        category=category,
                        name=item_data['name'],
                        reference_range=item_data['reference_range'],
                        unit=item_data['unit'],
                        order=order
                    )
                
                self.stdout.write(self.style.SUCCESS(f'Updated {len(items)} items for {category_name}'))

            self.stdout.write(self.style.SUCCESS('Successfully updated all test categories and items')) 