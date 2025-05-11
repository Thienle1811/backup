# Data Modeling Guide – Clinic-Manager

> **Mục tiêu**: mô tả ngắn gọn nhưng đầy đủ ý nghĩa, phạm vi và quan hệ giữa các bảng trong hệ thống quản lý phòng khám. Tài liệu này hỗ trợ dev front/back-end, DBA, QA và người viết tài liệu.

---

## 1. Khung tổng quan

| Nhóm chức năng               | Model chính                                                     | Vai trò cốt lõi                                           |
| ---------------------------- | --------------------------------------------------------------- | --------------------------------------------------------- |
| **Tài khoản & bảo mật**      | `CustomUser`, `Group`, `Permission`                             | Xác thực, phân quyền, audit.                              |
| **Bệnh nhân & hồ sơ**        | `Patient`, `MedicalRecord`, `MedicalRecordVersion`              | Lưu thông tin cá nhân & toàn bộ chẩn đoán, điều trị.      |
| **Xét nghiệm**               | `LabTest`, `LabTestVersion`                                     | Quản lý phiếu xét nghiệm và lịch sử chỉnh sửa.            |
| **Lab test form (skeleton)** | `LabTestTemplate`, `LabTestTemplateField`, `LabTestResultValue` | Khung định nghĩa & giá trị chi tiết cho phiếu xét nghiệm. |
| **Lịch hẹn**                 | `Appointment`                                                   | Điều phối bệnh nhân với bác sĩ/kỹ thuật viên.             |
| **Tệp đính kèm**             | `FileAttachment`                                                | Lưu trữ file (PDF, ảnh) trên S3 – dùng Generic FK.        |
| **Nhật ký**                  | `ActivityLog`                                                   | Ghi lại mọi hành động phát sinh bởi người dùng.           |

> Các module như **Invoice**, **Department** sẽ bổ sung sau giai đoạn MVP.

---

## 2. Mô tả chi tiết từng model

### 2.1 `CustomUser`

- Kế thừa `AbstractUser`. Đăng nhập bằng **email** (`USERNAME_FIELD = "email"`).
- Trường bổ sung: `phone`, `date_of_birth`, `full_name`.
- Quan hệ Many-to-Many đến `Group` (vai trò) & `Permission` (quyền).

### 2.2 `Patient`

- Thông tin cá nhân, nhóm máu, dị ứng, liên lạc.
- Trường `created_by`/`updated_by` (FK → User) để truy vết.
- 1-N tới `MedicalRecord`, `Appointment`, `FileAttachment` (qua GenericFK).

### 2.3 `MedicalRecord`

- Bản hiện hành của **một lần khám** (ngày khám, chẩn đoán).
- Shortcut `latest_version` ⇒ nhanh lấy version hiện tại.
- 1-N tới `MedicalRecordVersion` & `LabTest`.

### 2.4 `MedicalRecordVersion`

- Lưu **lịch sử** thay đổi của `MedicalRecord`.
- `version_number` tăng dần; `is_post_print` = `true` nếu chỉnh sau khi đã in.
- `changed_by`, `change_reason` hỗ trợ audit & rollback.

### 2.5 `LabTest`

- Gắn FK tới `MedicalRecord`.
- Thuộc một `LabTestTemplate` (định nghĩa form).
  ` LabTest` ⇢ `template` _Many-to-1_.
- Trường tổng hợp nhanh: `print_status`, `last_print_date`, `latest_version`.
- 1-N tới `LabTestVersion` & `LabTestResultValue`.

### 2.6 `LabTestVersion`

- Lịch sử chỉnh sửa toàn phiếu (toàn màn hình): bản snapshot PDF hoặc JSON.
- Tương tự `MedicalRecordVersion`.

### 2.7 `LabTestTemplate`

- Khung định nghĩa một loại phiếu xét nghiệm (ví dụ: “Huyết học thường quy”).
- Trường: `name`, `description`, `created_by`, `is_active`.
- 1-N tới `LabTestTemplateField`.

### 2.8 `LabTestTemplateField`

- Mỗi dòng/ô cần nhập: `field_name`, `unit`, `normal_min`, `normal_max`, `field_order`.
- FK tới `LabTestTemplate`.

### 2.9 `LabTestResultValue`

- Giá trị **thực** do kỹ thuật viên nhập cho từng trường.
- FK kép: `lab_test` + `template_field`.
- Trường `value`, `comment`.

### 2.10 `Appointment`

- Lịch hẹn giữa `Patient` & `staff` (FK → User).
- Trường `status` (Pending/Confirmed/Done/Cancelled).

### 2.11 `FileAttachment`

- Generic FK (`content_type`, `object_id`).
- `file_url` (S3), `uploaded_by`, `uploaded_at`.

### 2.12 `ActivityLog`

- Generic FK giống `FileAttachment`.
- Trường `user` (ai thực hiện), `action` (created, updated, deleted, printed...).
- Sinh tự động qua signals.

---

## 3. Quan hệ then chốt

```
User 1─∞ ActivityLog      (Generic)
User 1─∞ Appointment      staff_id
User 1─∞ Patient          created_by / updated_by
Patient 1─∞ MedicalRecord
MedicalRecord 1─∞ MedicalRecordVersion
MedicalRecord 1─∞ LabTest
LabTest 1─∞ LabTestVersion
LabTest 1─∞ LabTestResultValue
LabTestTemplate 1─∞ LabTestTemplateField
LabTestTemplate 1─∞ LabTest
LabTestTemplateField 1─∞ LabTestResultValue
Patient 1─∞ Appointment
FileAttachment N─1 any model (Generic)
```

---

## 4. Luồng sinh dữ liệu (ví dụ)

1. **Kỹ thuật viên** chọn `LabTestTemplate` ⟶ hệ thống tạo `LabTest` (status `Pending`) kèm `LabTestResultValue` trống cho từng `template_field`.
2. Kỹ thuật viên nhập giá trị, **lưu** → cập nhật `LabTestResultValue`, sinh `ActivityLog` action=`updated`.
3. **In PDF**: service lấy `template` + `LabTestResultValue` dựng HTML/PDF (ReportLab) và lưu `FileAttachment`.
4. Bác sĩ sửa kết quả sau in → thêm `LabTestVersion` (`is_post_print=true`) & update `LabTestResultValue`; log ghi nhận.

---

## 5. Phát triển & bảo trì

- Dùng mixin `VersionedModelMixin` cho hai bảng version để tái sử dụng (fields common).
- Index gợi ý:

  - (`template_id`, `lab_test_id`) trên `LabTestResultValue`.
  - (`lab_test_id`, `version_number`) trên `LabTestVersion`.
  - (`content_type`, `object_id`) trên `FileAttachment`, `ActivityLog`.

- Khi cần thêm loại dịch vụ cận lâm sàng khác, chỉ cần thêm `LabTestTemplate` + field, không chạm schema chính.

## 6. DiagramIO
```
// ==============================
// Clinic-Manager – Updated Data Model
// ==============================

Table accounts_customuser {
  id                integer    [pk]
  email             varchar(255) [not null, unique]
  full_name         varchar(255)
  phone             varchar(50)
  date_of_birth     date
  is_active         boolean     [default: true]
  created_at        timestamp   [default: `now()`]
  updated_at        timestamp   [default: `now()`]
}

Table patients_patient {
  id                integer    [pk]
  full_name         varchar(255) [not null]
  date_of_birth     date
  gender            varchar(10)
  address           varchar(255)
  phone             varchar(50)
  email             varchar(255)
  blood_type        varchar(10)
  allergies         text
  created_by        integer
  updated_by        integer
  created_at        timestamp [default: `now()`]
  updated_at        timestamp [default: `now()`]
}

Table medical_records_medicalrecord {
  id                integer    [pk]
  patient_id        integer    [not null]
  record_date       date
  diagnosis         text
  notes             text
  latest_version    integer
  created_by        integer
  updated_by        integer
  created_at        timestamp [default: `now()`]
  updated_at        timestamp [default: `now()`]
}

Table medical_record_versions {
  id                 integer    [pk]
  medical_record_id  integer    [not null]
  version_number     integer    [not null]
  diagnosis          text
  notes              text
  is_post_print      boolean    [default: false]
  changed_by         integer
  change_reason      text
  changed_at         timestamp [default: `now()`]
}

Table lab_test_template {
  id                integer    [pk]
  name              varchar(255) [not null]
  description       text
  created_by        integer
  is_active         boolean    [default: true]
  created_at        timestamp [default: `now()`]
  updated_at        timestamp [default: `now()`]
}

Table lab_test_template_field {
  id                integer    [pk]
  template_id       integer    [not null]
  field_name        varchar(255) [not null]
  unit              varchar(50)
  normal_min        decimal(10,2)
  normal_max        decimal(10,2)
  field_order       integer
}

Table lab_tests_labtest {
  id                integer    [pk]
  medical_record_id integer    [not null]
  template_id       integer    [not null]
  value             decimal(10,2)
  result            text
  print_status      varchar(20) [default: 'Pending']
  last_print_date   timestamp
  latest_version    integer
  created_at        timestamp [default: `now()`]
  updated_at        timestamp [default: `now()`]
}

Table lab_test_versions {
  id               integer    [pk]
  lab_test_id      integer    [not null]
  version_number   integer    [not null]
  result_value     text
  is_post_print    boolean    [default: false]
  changed_by       integer
  change_reason    text
  changed_at       timestamp [default: `now()`]
}

Table lab_test_result_value {
  id                integer    [pk]
  lab_test_id       integer    [not null]
  template_field_id integer    [not null]
  value             text
  comment           text
}

Table appointments_appointment {
  id                integer    [pk]
  patient_id        integer    [not null]
  staff_id          integer    [not null]
  appointment_date  date
  appointment_time  time
  status            varchar(20)
}

Table files_fileattachment {
  id                integer    [pk]
  content_type      varchar(50)
  object_id         integer
  file_url          varchar(255)
  uploaded_by       integer
  uploaded_at       timestamp [default: `now()`]
}

Table activity_logs_activitylog {
  id                integer    [pk]
  user_id           integer
  content_type      varchar(50) [not null]
  object_id         integer    [not null]
  action            varchar(255)
  log_timestamp     timestamp [default: `now()`]
}

// ====================
// Relationships
// ====================

Ref: patients_patient.created_by               > accounts_customuser.id
Ref: patients_patient.updated_by               > accounts_customuser.id

Ref: medical_records_medicalrecord.patient_id  > patients_patient.id
Ref: medical_records_medicalrecord.created_by  > accounts_customuser.id
Ref: medical_records_medicalrecord.updated_by  > accounts_customuser.id

Ref: medical_record_versions.medical_record_id > medical_records_medicalrecord.id
Ref: medical_record_versions.changed_by        > accounts_customuser.id

Ref: lab_test_template_field.template_id       > lab_test_template.id
Ref: lab_test_template.created_by              > accounts_customuser.id

Ref: lab_tests_labtest.medical_record_id       > medical_records_medicalrecord.id
Ref: lab_tests_labtest.template_id             > lab_test_template.id

Ref: lab_test_versions.lab_test_id             > lab_tests_labtest.id
Ref: lab_test_versions.changed_by              > accounts_customuser.id

Ref: lab_test_result_value.lab_test_id         > lab_tests_labtest.id
Ref: lab_test_result_value.template_field_id   > lab_test_template_field.id

Ref: appointments_appointment.patient_id       > patients_patient.id
Ref: appointments_appointment.staff_id         > accounts_customuser.id

Ref: files_fileattachment.uploaded_by          > accounts_customuser.id

Ref: activity_logs_activitylog.user_id         > accounts_customuser.id
```