from django import forms
from .models import Patient # Import model Patient của bạn

class PatientForm(forms.ModelForm):
            class Meta:
                model = Patient
                # Liệt kê các trường bạn muốn hiển thị trong form
                # Bạn có thể dùng '__all__' để bao gồm tất cả các trường từ model,
                # hoặc liệt kê cụ thể.
                fields = [
                    'full_name',
                    'date_of_birth',
                    'gender',
                    'phone',
                    'address',
                    'email',
                    'blood_type',
                    'allergies',
                    # Các trường 'created_by', 'updated_by', 'created_at', 'updated_at'
                    # thường được xử lý tự động và không cần người dùng nhập trực tiếp.
                ]
                # Tùy chỉnh widgets (cách hiển thị các trường trong HTML) nếu cần
                widgets = {
                    'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập họ và tên'}),
                    'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}), # Sử dụng input type="date" của HTML5
                    'gender': forms.Select(attrs={'class': 'form-select'}),
                    'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập địa chỉ'}),
                    'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nhập số điện thoại'}),
                    'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Nhập địa chỉ email'}),
                    'blood_type': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ví dụ: A+, O-'}),
                    'allergies': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Mô tả các dị ứng (nếu có)'}),
                }
                # Tùy chỉnh nhãn (labels) cho các trường nếu cần
                labels = {
                    'full_name': 'Họ và tên',
                    'date_of_birth': 'Ngày sinh',
                    'gender': 'Giới tính',
                    'address': 'Địa chỉ',
                    'phone': 'Số điện thoại',
                    'email': 'Địa chỉ Email',
                    'blood_type': 'Nhóm máu',
                    'allergies': 'Dị ứng',
                }
                # Tùy chỉnh thông báo lỗi hoặc help_texts nếu cần
                # help_texts = {
                #     'phone': 'Định dạng số điện thoại hợp lệ.',
                # }

            # Bạn có thể thêm các phương thức clean_<fieldname>() để tùy chỉnh việc xác thực
            # cho từng trường cụ thể, hoặc phương thức clean() để xác thực toàn bộ form.
            # Ví dụ:
            # def clean_email(self):
            #     email = self.cleaned_data.get('email')
            #     # Thêm logic kiểm tra email tùy chỉnh ở đây nếu cần
            #     # Ví dụ: kiểm tra xem email có tồn tại ở một hệ thống khác không
            #     if email and Patient.objects.filter(email=email).exists() and not self.instance.pk: # Chỉ kiểm tra khi tạo mới
            #         raise forms.ValidationError("Địa chỉ email này đã được sử dụng cho một bệnh nhân khác.")
            #     return email
        