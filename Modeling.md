# Data Modeling Guide – Clinic‑Manager

> **Mục tiêu**: mô tả ngắn gọn nhưng đầy đủ ý nghĩa, phạm vi và quan hệ giữa các bảng trong hệ thống quản lý phòng khám. Tài liệu này hỗ trợ dev front/back‑end, DBA, QA và người viết tài liệu.

---

## 1. Khung tổng quan

| Nhóm chức năng          | Model chính                                        | Vai trò cốt lõi                                      |
| ----------------------- | -------------------------------------------------- | ---------------------------------------------------- |
| **Tài khoản & bảo mật** | `CustomUser`, `Group`, `Permission`                | Xác thực, phân quyền, audit.                         |
| **Bệnh nhân & hồ sơ**   | `Patient`, `MedicalRecord`, `MedicalRecordVersion` | Lưu thông tin cá nhân & toàn bộ chẩn đoán, điều trị. |
| **Xét nghiệm**          | `LabTest`, `LabTestVersion`                        | Quản lý phiếu xét nghiệm và lịch sử chỉnh sửa.       |
| **Lịch hẹn**            | `Appointment`                                      | Điều phối bệnh nhân với bác sĩ/kỹ thuật viên.        |
| **Tệp đính kèm**        | `FileAttachment`                                   | Lưu trữ file (PDF, ảnh) trên S3 – dùng Generic FK.   |
| **Nhật ký**             | `ActivityLog`                                      | Ghi lại mọi hành động phát sinh bởi người dùng.      |

> **MVP** chưa bao gồm hoá đơn, khoa phòng, dịch vụ cận lâm sàng mở rộng – thêm sau.

---

## 2. Mô tả chi tiết từng model

### 2.1 `CustomUser`

- Kế thừa `AbstractUser`.
- Đăng nhập bằng **email** (`USERNAME_FIELD = "email"`).
- Trường bổ sung: `phone`, `date_of_birth`, `full_name`.
- Gắn M‑N tới `Group` (vai trò) và `Permission` (quyền).

### 2.2 `Patient`

- Thông tin cá nhân, liên hệ, nhóm máu, dị ứng.
- Trường `created_by`/`updated_by` (FK → User) để truy vết.
- 1‑N tới `MedicalRecord` & `Appointment`.

### 2.3 `MedicalRecord`

- Bản hiện hành của **một lần khám** (ngày khám, chẩn đoán).
- Shortcut `latest_version` ⇒ nhanh lấy version hiện tại.
- 1‑N tới `MedicalRecordVersion` & `LabTest`.

### 2.4 `MedicalRecordVersion`

- Lưu **lịch sử** thay đổi của `MedicalRecord`.
- `version_number` tăng dần; `is_post_print` = `true` nếu chỉnh sau khi đã in.
- `changed_by`, `change_reason` hỗ trợ audit & rollback.

### 2.5 `LabTest`

- Gắn FK tới `MedicalRecord` (phiếu xét nghiệm thuộc lần khám).
- Trường `test_type` (enum/text), `value`, `result`.
- `print_status`, `last_print_date`, `latest_version` tương tự MedicalRecord.

### 2.6 `LabTestVersion`

- Lịch sử chỉnh sửa kết quả xét nghiệm.
- Logic giống model version ở trên.

### 2.7 `Appointment`

- Lịch hẹn giữa `Patient` & `staff` (FK → User).
- Trường `status` (Pending/Confirmed/Done/Cancelled).

### 2.8 `FileAttachment`

- Generic FK (`content_type` + `object_id`) liên kết linh hoạt tới **bất kỳ** model nào.
- `file_url`: đường dẫn S3; `uploaded_by`, `uploaded_at`.

### 2.9 `ActivityLog`

- Generic FK như `FileAttachment`.
- Trường `user` (ai thực hiện), `action` (created, updated, deleted, printed...).
- Được tự động sinh bằng signal (post_save, post_delete).

---

## 3. Quan hệ then chốt

```
User 1─∞ ActivityLog      Generic
User 1─∞ Appointment      staff_id
User 1─∞ Patient          (created_by / updated_by)
Patient 1─∞ MedicalRecord
MedicalRecord 1─∞ MedicalRecordVersion
MedicalRecord 1─∞ LabTest
LabTest 1─∞ LabTestVersion
Patient 1─∞ Appointment
FileAttachment N─1 any model (Generic)
```

---

## 4. Luồng sinh dữ liệu (ví dụ)

1. **Nhân viên** (User) tạo _Patient_ → sinh `ActivityLog` (action=`created`).
2. Nhân viên tạo _MedicalRecord_ (+ _LabTest_) → sinh log.
3. Sau khi in, bác sĩ sửa chẩn đoán → ghi _MedicalRecordVersion_ (`is_post_print=true`) + log action=`updated`.
4. Hệ thống hiển thị lịch sử tại tab **Audit**, admin lọc theo User/Patient.

---

## 5. Phát triển & bảo trì

- Mọi model version dùng chung mixin `VersionedModelMixin` để giảm lặp.
- Index gợi ý:

  - (`patient_id`, `record_date`) trên `MedicalRecord`.
  - (`medical_record_id`, `test_type`) trên `LabTest`.
  - (`content_type`, `object_id`) trên `FileAttachment` & `ActivityLog`.

- Seed dữ liệu `Group` + quyền đặc thù qua data‑migration.

> **Kết thúc** – document này là baseline; update khi thêm entity mới.
