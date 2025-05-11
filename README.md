# 🏥 Clinic-Manager – Ứng dụng Web Quản Lý Phòng Khám

## 1. Giới thiệu
**Clinic-Manager** là hệ thống quản lý hồ sơ bệnh án chạy trên Django 5 (Python 3.13) giúp:
- **Nhập liệu & lưu trữ** hồ sơ bệnh án tập trung (PostgreSQL).  
- **Tra cứu nhanh** theo tên, mã bệnh nhân… trên web & di động (Bootstrap 5, responsive).  
- **Xuất bản in ấn**: kết xuất PDF chuẩn (ReportLab) và tải về trên cả PC lẫn mobile.  
- **Theo dõi hoạt động nhân sự**: đăng nhập, phân quyền, log thao tác.  
- **Triển khai cloud-native**: Railway (app), Amazon S3 (lưu trữ file), 2 môi trường Dev / Production.

---

## 2. Cây thư mục

clinic-manager/
├─ manage.py # Entrypoint Django
├─ README.md
├─ requirements/ # File lock/packages phụ thuộc
│ ├─ base.txt # Chung
│ ├─ dev.txt # Dev extras (debug-toolbar…)
│ └─ prod.txt # Gunicorn, Whitenoise…
│
├─ config/ # Project package
│ ├─ asgi.py / wsgi.py
│ ├─ urls.py
│ └─ settings/ # Tách settings
|   ├─ init.py # Đọc env DJANGO_ENV
|   ├─ base.py # Chung
|   ├─ local.py # Dev
|   └─ production.py # Prod
│
├─ apps/ # Business apps (Two-Scoops style)
│ ├─ accounts/ # CustomUser, phân quyền
│ ├─ patients/ # Thông tin bệnh nhân
│ ├─ medical_records/ # CRUD & tìm kiếm hồ sơ
│ ├─ reports/ # Xuất PDF, upload S3
│ └─ dashboard/ # Thống kê, biểu đồ
│
├─ templates/ # Base layout + component chung
└─ static/ # Bootstrap, JS, ảnh tĩnh


**Giải thích nhanh**

| Thư mục / file      | Vai trò                                                                                                                                      |
|---------------------|-----------------------------------------------------------------------------------------------------------------------------------------------|
| `config/settings/*` | Phân chia _base / local / production_ ⇒ dễ tùy biến cho nhiều môi trường, tránh “if DEBUG:” rải rác.                                         |
| `apps/`             | Mỗi **app** gói trọn models, views, urls, tests → tái sử dụng & maintain dễ.                                                                 |
| `templates/`        | Giao diện chung (_base.html_, partials) – override/extend templates của app khi cần.                                                         |
| `requirements/`     | **base.txt** = bắt buộc; **dev.txt** & **prod.txt** _pip-tools_ có thể include `-r base.txt` để lắp ghép nhanh.                              |

---

## 3. Cấu hình & biến môi trường

| Biến                   | Mặc định | Mô tả                                                         |
|------------------------|----------|--------------------------------------------------------------|
| `DJANGO_ENV`          | `local`  | `local` / `production` – quyết định file settings nạp.       |
| `DJANGO_SECRET_KEY`   | _unsafe_ | Bắt buộc đổi ở production.                                   |
| `DJANGO_ALLOWED_HOSTS`| `""`     | CSV hostnames (vd: `clinic.example.com,127.0.0.1`).          |
| `POSTGRES_*`          | …        | `DB, USER, PASSWORD, HOST, PORT` cho PostgreSQL.             |
| `AWS_ACCESS_KEY_ID`   |          | Truy cập S3 (lưu PDF).                                       |
| `AWS_S3_BUCKET_NAME`  |          | Bucket đích.                                                 |

> **Production hardening** đã bật: `SECURE_SSL_REDIRECT`, cookie secure, WhiteNoise nén static, v.v.

---

## 4. Các lệnh khởi tạo & chạy dự án

### 4.1 Lần đầu (Dev – Windows CMD)

```cmd
:: clone & vào thư mục
git clone https://github.com/your-org/clinic-manager.git
cd clinic-manager

:: tạo & kích hoạt venv
py -m venv .venv
.\.venv\Scripts\activate

:: cài gói
pip install -r requirements/base.txt
pip install -r requirements/dev.txt

:: cấu hình env (file .env hoặc set tạm)
set DJANGO_ENV=local
set POSTGRES_DB=clinic_db
set POSTGRES_USER=clinic_user
set POSTGRES_PASSWORD=changeme

:: migrate & tạo admin
python manage.py migrate
python manage.py createsuperuser

:: chạy server
python manage.py runserver

Truy cập http://127.0.0.1:8000/ và http://127.0.0.1:8000/admin/.

### 4.2 Deploy Production (Railway) - Lưu ý các bước này không được tự ý thực hiện

railway login
railway init --python

:: trên dashboard Railway
# 1. Add biến env DJANGO_ENV=production và các biến DB, SECRET_KEY
# 2. Kết nối PostgreSQL plugin hoặc external RDS
# 3. Enable disk build cache (tốc độ deployment)

# migrate & collectstatic
railway run "python manage.py migrate"
railway run "python manage.py collectstatic --noinput"

Railway tự gắn SSL; trỏ DNS CNAME → subdomain Railway là hoàn tất.

## 5. Đóng góp & Lộ trình

### 📌 Roadmap

- ✅ **Phase 1**: Hoàn thiện models + Setting Up Project  
- ⏳ **Phase 2**: Xây dựng giao diện CRUD và tìm kiếm hồ sơ  
- ⏳ **Phase 3**: Tích hợp ReportLab & upload file PDF lên Amazon S3  
- ⏳ **Phase 4**: Ghi nhận lịch sử thao tác (audit trail) và xây dựng dashboard quản lý  

---

🎯 **Pull request** welcome!  
Vui lòng xem thêm hướng dẫn trong [README.md](README.md)

---

Happy coding! 🎉
