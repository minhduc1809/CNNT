# HỆ THỐNG QUẢN LÝ KHO HÀNG THÔNG MINH – ĐỀ TÀI 22

> **Học phần:** Nhập môn Công nghệ nền tảng (RIPT1304) – Học viện Công nghệ Bưu chính Viễn thông (PTIT)  
> **Nhóm thực hiện:** Nhóm 22  
> **Trọng tâm đề tài:** Hạ tầng CNTT (Mạng phân vùng VLAN 10/20/30, Tường lửa/ACL, Máy chủ & CSDL MySQL phân quyền 3 tầng, Điểm quét + hàng đợi ngoại tuyến + Docker Compose, Sao lưu/khôi phục định kỳ & Kiểm thử, đối chiếu, đánh giá mở rộng).

---

## 📁 Cấu trúc thư mục dự án (đồng nhất SV1–SV4)

```text
CNNT/
├── SV1_ThietKeMang_DuLieu/          # SV1 (Đỗ Thị Liên - B24DCCC174): Mạng 3 vùng VLAN, ACL, ERD, giao ước API
│   ├── bang_ip/                     # Bảng phân hoạch IP chi tiết các vùng mạng
│   ├── mo_hinh_du_lieu/             # Sơ đồ ERD, từ điển dữ liệu, luồng nghiệp vụ
│   ├── tai_thu/                     # Kịch bản sinh tải giả lập
│   └── uoc_luong/                   # Mô hình ước lượng tài nguyên khi mở rộng 2 -> 6 điểm quét
│
├── SV2_DiemQuet_HangDoi/            # SV2 (Trần Lê Minh Đức - B24DCCC073): Điểm quét SP01/SP02, hàng đợi & retry
│   ├── scanner.py                   # Ứng dụng điểm quét (đăng nhập, kiểm tra đầu vào, hàng đợi JSONL + fsync)
│   ├── config_sp01.json             # Cấu hình điểm quét khu Nhập (SP01)
│   ├── config_sp02.json             # Cấu hình điểm quét khu Xuất (SP02)
│   ├── thu_mat_mang_va_doi_chieu.py # Kịch bản thử mất kết nối, retry backoff & đối chiếu seq_no
│   ├── thu_dong_thoi_xuat.py        # Thử nghiệm xuất đồng thời 2 điểm quét (chống âm kho)
│   ├── logs/                        # Nhật ký giao dịch lưu vết tại máy khách
│   ├── queue/                       # Hàng đợi cục bộ JSONL chờ gửi lại
│   └── evidence/                    # Minh chứng vận hành SV2 (MC_SV2_01 .. MC_SV2_08)
│
├── SV3_MayChu_CSDL_API/             # SV3 (Phạm Công Mạnh - B24DCCC193): Máy chủ, CSDL MySQL, API & Sao lưu
│   ├── 01_CSDL_SQL/                 # Khởi tạo CSDL smart_warehouse, 100 sản phẩm, Stored Procedure, phân quyền
│   ├── 02_BACKUP_RESTORE/           # Lịch sao lưu định kỳ (Task Scheduler) & khôi phục đối chiếu RTO
│   ├── 03_API_CONTRACT/             # Đặc tả giao ước API chuẩn giữa SV1–SV2–SV3
│   ├── 04_DICH_VU_API/              # Dịch vụ Flask RESTful API (app.py, test_all_features.py, .env.example)
│   ├── 05_CAU_HINH_MAY_CHU/         # Cấu hình tường lửa, tài khoản OS, dịch vụ hệ thống
│   └── evidence/                    # Minh chứng triển khai SV3 (MC01 .. MC13)
│
├── SV4_KiemThu/                     # SV4 (Nguyễn Mạnh Dũng - B24DCCC082): Kiểm thử nghiệm thu, đo đạc & đối chiếu
│   ├── doi_chieu_sv4.py             # Đối chiếu hàng đợi cục bộ với CSDL sau ngắt mạng
│   ├── kt3a_viewer.py               # Kiểm thử phân quyền chỉ xem 2 tầng (API + MySQL)
│   ├── do_cpu_ram.py                # Đo đạc CPU, RAM, độ trễ p95 mở rộng 2 -> 6 điểm quét
│   ├── tao_v2_sql.py                # Tạo CSDL thử tách biệt smart_warehouse_v2
│   └── MinhChung/                   # Toàn bộ minh chứng kiểm thử (MC-KT1 .. MC-MR, MC-DC, MC-LICH)
│
├── docker/                          # SV2: Script khởi tạo tài khoản/quyền MySQL 8.0 trong Docker
├── docker-compose.yml               # SV2: Dựng container MySQL 8.0 (cnnt-mysql) tự nạp SQL từ SV3
├── .env.docker.example              # Mẫu biến môi trường cho Docker Compose (không chứa mật khẩu thật)
└── docs/                            # Báo cáo nhóm & 4 báo cáo cá nhân đồng bộ
    ├── BaoCaoNhom_DeTai22_Nhom22.docx
    ├── BaoCaoCaNhan_SV1_DoThiLien_B24DCCC174.docx
    ├── BaoCaoCaNhan_SV2_TranLeMinhDuc_B24DCCC073.docx
    ├── BaoCaoCaNhan_SV3_PhamCongManh_B24DCCC193.docx
    └── BaoCaoCaNhan_SV4_NguyenManhDung_B24DCCC082.docx
```

---

## 👥 Phân công nhiệm vụ các thành viên (Nhóm 22)

| Thành viên | Mã SV | Vai trò chính | Nhiệm vụ chuyên môn (CV01 – CV03) |
| :--- | :---: | :--- | :--- |
| **Đỗ Thị Liên** (SV1) | `B24DCCC174` | Thiết kế mạng & Mô hình dữ liệu | • Phân vùng 3 VLAN (10, 20, 30), bảng IP, chính sách tường lửa/ACL (Packet Tracer & VM).<br>• Thiết kế mô hình dữ liệu (ERD), từ điển dữ liệu, giao ước API & mô hình ước lượng tải. |
| **Trần Lê Minh Đức** (SV2) | `B24DCCC073` | Điểm quét, Hàng đợi & Docker | • Phát triển ứng dụng điểm quét `SP01`, `SP02`, kiểm tra đầu vào, sinh `txn_id`.<br>• Hàng đợi ngoại tuyến JSONL (`fsync`), gửi lại có kiểm soát (backoff), thử đồng thời & cấu hình Docker Compose MySQL 8.0. |
| **Phạm Công Mạnh** (SV3) | `B24DCCC193` | Máy chủ, CSDL, API & Sao lưu | • Dựng CSDL MySQL `smart_warehouse`, 100 sản phẩm, Stored Procedure khóa dòng `FOR UPDATE`.<br>• Dịch vụ Flask API, phân quyền 3 tầng (OS/NTFS, MySQL `wh_store`, API RBAC), sao lưu định kỳ & đo RTO. |
| **Nguyễn Mạnh Dũng** (SV4) | `B24DCCC082` | Kiểm thử, Đối chiếu & Mở rộng | • Kiểm thử nghiệm thu KT1, KT2, KT3a, KT3b, ca chịu lỗi L2/L3.<br>• Đo đạc tài nguyên CPU/RAM/độ trễ p95 (2 → 6 điểm quét) & đối chiếu toàn vẹn sau mất mạng. |

---

## 🚀 Hướng dẫn cài đặt & Vận hành nhanh

### 1. Chuẩn bị môi trường
* **Python:** Phiên bản 3.10 trở lên (`python --version`)
* **MySQL:** Dùng **Docker Compose** (`mysql:8.0`, khuyên dùng để tái lập nhanh) hoặc cài **MySQL Server 8.0 / 9.3** cục bộ tại cổng `3306`.

Cài đặt thư viện Python:
```powershell
python -m pip install -r SV3_MayChu_CSDL_API\04_DICH_VU_API\requirements.txt
python -m pip install -r SV2_DiemQuet_HangDoi\requirements.txt
```

---

### 2. Thiết lập Cơ sở dữ liệu MySQL

#### Cách A – Dùng Docker Compose (khuyến nghị, do SV2 đóng gói từ SQL của SV3)
1. Sao chép file mẫu biến môi trường và đặt mật khẩu quản trị riêng:
   ```powershell
   Copy-Item .env.docker.example .env.docker
   ```
2. Khởi chạy container `cnnt-mysql` (tự động nạp các file SQL từ `SV3_MayChu_CSDL_API/01_CSDL_SQL/`):
   ```powershell
   docker compose --env-file .env.docker up -d
   docker compose ps
   ```

#### Cách B – Cài MySQL trực tiếp trên máy chủ (SV3)
Chạy lần lượt các tệp trong `SV3_MayChu_CSDL_API/01_CSDL_SQL/` bằng tài khoản `root`:
1. `01_create_database.sql` – Tạo database `smart_warehouse` và 5 bảng.
2. `02_insert_sample_data.sql` – Nạp 100 mặt hàng, tồn đầu kỳ và tài khoản ứng dụng (lưu hash).
3. `03_create_procedure.sql` – Tạo Stored Procedure `sp_warehouse_transaction` (`FOR UPDATE`, chống âm kho).
4. `04_create_permissions.sql` – Tạo tài khoản phân quyền (`wh_admin`, `wh_store`, `wh_employee`, `wh_viewer`).
5. `06_sync_sv1_sv3_aliases.sql` – Đồng bộ mã điểm quét `SP01`, `SP02`.

*(Mật khẩu các tài khoản quản trị/CSDL được cấu hình riêng qua tệp `.env` cục bộ hoặc biến môi trường, không công khai trong tài liệu).*

---

### 3. Cấu hình tệp môi trường API (`.env`)
Sao chép từ mẫu `SV3_MayChu_CSDL_API/04_DICH_VU_API/.env.example`:
```powershell
Copy-Item SV3_MayChu_CSDL_API\04_DICH_VU_API\.env.example SV3_MayChu_CSDL_API\04_DICH_VU_API\.env
```
Điền thông số kết nối `DB_HOST`, `DB_PORT=3306`, `DB_USER=wh_store`, `DB_PASS=<mat_khau_wh_store>`, `DB_NAME=smart_warehouse`.

---

### 4. Khởi chạy Dịch vụ API Máy chủ (SV3)
```powershell
cd SV3_MayChu_CSDL_API\04_DICH_VU_API
python app.py
```
> Dịch vụ lắng nghe tại cổng `8080` và kết nối MySQL bằng tài khoản đặc quyền tối thiểu `wh_store` (`SELECT` + `EXECUTE`).

---

### 5. Vận hành 2 Điểm quét hàng hóa (SV2)
Mở 2 cửa sổ dòng lệnh độc lập (ví dụ Windows cho `SP01` và WSL/máy trạm thứ hai cho `SP02`):

```powershell
# Điểm quét 01 (Khu Nhập)
python SV2_DiemQuet_HangDoi\scanner.py SV2_DiemQuet_HangDoi\config_sp01.json --url http://<IP_MAY_CHU>:8080

# Điểm quét 02 (Khu Xuất)
python SV2_DiemQuet_HangDoi\scanner.py SV2_DiemQuet_HangDoi\config_sp02.json --url http://<IP_MAY_CHU>:8080
```

---

### 6. Chạy kiểm thử tự động & đối chiếu (SV3 & SV4)
```powershell
# Bộ kiểm thử 26 ca chức năng & phân quyền API (SV3)
cd SV3_MayChu_CSDL_API\04_DICH_VU_API
python test_all_features.py

# Kiểm thử phân quyền chỉ xem 2 tầng (SV4)
python SV4_KiemThu\kt3a_viewer.py

# Đối chiếu hàng đợi cục bộ với CSDL sau mất mạng (SV4)
python SV4_KiemThu\doi_chieu_sv4.py
```

---

## 🔒 Cơ chế bảo mật phân quyền 3 tầng

1. **Tầng Hệ điều hành (OS Layer):** Dịch vụ chạy dưới tài khoản riêng (`wh_service`), thư mục mã nguồn/dữ liệu/sao lưu cô lập quyền NTFS/Linux.
2. **Tầng Cơ sở dữ liệu (Database Layer):** API không dùng `root`; kết nối bằng tài khoản `wh_store` chỉ có quyền `SELECT` và `EXECUTE` Stored Procedure; tài khoản `wh_viewer` chỉ có quyền `SELECT`.
3. **Tầng Dịch vụ ứng dụng (API RBAC Layer):** Xác thực Bearer Token và phân tách 4 vai trò (`viewer`, `employee`, `warehouse`, `admin`), trả `403 Forbidden` với mọi thao tác vượt quyền.
