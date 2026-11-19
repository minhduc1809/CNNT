# BÁO CÁO KỸ THUẬT & HƯỚNG DẪN TRIỂN KHAI PHẦN VIỆC SINH VIÊN 3 (SV3)
**Hệ Thống Quản Lý Kho Hàng Thông Minh (Đề Tài 22)**

* **Sinh viên phụ trách:** Phạm Công Mạnh
* **Mã sinh viên:** B24DCCC193
* **Vai trò:** SV3 – Máy chủ, Cơ sở dữ liệu, Phân quyền 3 tầng, Sao lưu & Khôi phục dữ liệu
* **Môi trường triển khai:** Windows Server / Windows 10 (hỗ trợ Linux systemd), MySQL Server 9.3 (cổng 3306), Python 3.11 (Flask API cổng 8080)

---

## 📑 MỤC LỤC
1. [Tổng quan nhiệm vụ SV3](#1-tổng-quan-nhiệm-vụ-sv3)
2. [Cấu trúc thư mục bàn giao](#2-cấu-trúc-thư-mục-bàn-giao)
3. [Chi tiết triển khai kỹ thuật](#3-chi-tiết-triển-khai-kỹ-thuật)
   - [CV01 – Thiết kế CSDL & Cơ chế ACID, Chống trùng, Chống âm kho](#cv01--thiết-kế-csdl--cơ-chế-acid-chống-trùng-chống-âm-kho-7-điểm)
   - [CV02 – Dịch vụ API & Mô hình Phân quyền 3 tầng](#cv02--dịch-vụ-api--mô-hình-phân-quyền-3-tầng-6-điểm)
   - [CV03 – Sao lưu theo lịch, Khôi phục thật & Đo kiểm RTO](#cv03--sao-lưu-theo-lịch-khôi-phục-thật--đo-kiểm-rto-7-điểm)
4. [Danh sách tài khoản kiểm thử](#4-danh-sách-tài-khoản-kiểm-thử)
5. [Quy trình chạy và kiểm thử nhanh khi bảo vệ](#5-quy-trình-chạy-và-kiểm-thử-nhanh-khi-bảo-vệ)

---

## 1. TỔNG QUAN NHIỆM VỤ SV3

Theo phân công đề tài, SV3 chịu trách nhiệm toàn bộ tầng máy chủ trung tâm và dữ liệu:
* **CV01 (7 điểm):** Cài đặt CSDL, tạo bảng theo mô hình dữ liệu chuẩn của SV1, cài đặt ràng buộc chống âm kho, chống trùng mã giao dịch, nạp 100 mặt hàng và tồn kho ban đầu.
* **CV02 (6 điểm):** Xây dựng dịch vụ RESTful API đồng bộ với điểm quét (SV2), phân quyền 3 tầng độc lập (Tầng Ứng dụng RBAC, Tầng CSDL đặc quyền tối thiểu, Tầng Hệ điều hành cô lập thư mục).
* **CV03 (7 điểm):** Thiết lập lịch sao lưu tự động định kỳ (Task Scheduler), script khôi phục vào CSDL độc lập, tự động đối chiếu số bản ghi / CHECKSUM và đo lường thời gian khôi phục thực tế so với chỉ số RTO.

---

## 2. CẤU TRÚC THƯ MỤC BÀN GIAO

```text
sinh-vien-3/
├── README.md                              <- Tài liệu hướng dẫn chi tiết toàn bộ phần việc SV3
├── BaoCaoCaNhan_B24DCCC193_PhamCongManh.docx <- Báo cáo cá nhân chính thức
│
├── 01_CSDL_SQL/                           <- Toàn bộ script CSDL MySQL
│   ├── 01_create_database.sql             <- Khởi tạo CSDL smart_warehouse và 5 bảng chính
│   ├── 02_insert_sample_data.sql          <- Nạp 100 sản phẩm, tồn đầu, 5 tài khoản mẫu có hash
│   ├── 03_create_procedure.sql            <- Stored Procedure ACID cập nhật giao dịch kho
│   ├── 04_create_permissions.sql          <- Phân quyền tài khoản MySQL (wh_store, wh_employee,...)
│   ├── 05_test_transactions.sql          <- Kịch bản kiểm thử SQL trực tiếp
│   ├── 06_sync_sv1_sv3_aliases.sql        <- Đồng bộ alias điểm quét (SP01, SP02) và tài khoản SV1
│   └── Cơ chế chống trùng chống tồn âm.md <- Tài liệu chi tiết 3 lớp bảo vệ dữ liệu
│
├── 02_BACKUP_RESTORE/                     <- Hệ thống sao lưu & khôi phục tự động
│   ├── 00_tao_user_sao_luu.sql            <- Tạo user MySQL 'wh_dump' đặc quyền tối thiểu
│   ├── 01_sao_luu.ps1                     <- Script thực thi mysqldump an toàn, ghi hash SHA-256
│   ├── 02_dang_ky_lich.ps1                <- Đăng ký Windows Task Scheduler (chu kỳ 2h)
│   ├── 03_khoi_phuc_va_doi_chieu.ps1      <- Script khôi phục CSDL tạm & đối chiếu checksum
│   ├── BangDoiChieu_ThoiGianKhoiPhuc.md   <- Bảng kết quả đối chiếu số liệu và đo lường RTO
│   └── smart_warehouse_backup_latest.sql  <- Bản sao lưu chuẩn mới nhất
│
├── 03_API_CONTRACT/                       <- Hợp đồng giao tiếp API
│   └── api_contract.md                    <- Quy chuẩn JSON, endpoint, HTTP status code
│
├── 04_DICH_VU_API/                        <- Dịch vụ máy chủ Backend (RESTful API)
│   ├── app.py                             <- Source code chính (Flask, PyMySQL, RBAC, Stored Procedure)
│   ├── config.json                        <- Cấu hình tham số dịch vụ
│   ├── requirements.txt                   <- Danh sách thư viện Python cần thiết
│   ├── test_all_features.py               <- Bộ kiểm thử tự động 26 ca kiểm thử toàn diện
│   └── service_config/                    <- File cấu hình dịch vụ trên Linux (systemd)
│       ├── setup_linux_permissions.sh     <- Script phân quyền Linux
│       └── smart_warehouse_api.service    <- Cấu hình Systemd daemon
│
└── 05_CAU_HINH_MAY_CHU/                   <- Bảo mật và thiết lập máy chủ
    ├── 02_my.ini.mau                      <- Mẫu cấu hình bảo mật MySQL (bind 127.0.0.1)
    ├── 03_tuong_lua_windows.ps1           <- Cấu hình Windows Defender Firewall
    ├── 04_tao_user_thu_muc.ps1            <- Tạo user OS (wh_service, wh_backup) & phân quyền NTFS
    └── 05_kiem_tra_may_chu.ps1            <- Script kiểm tra sức khỏe và bảo mật máy chủ
```

---

## 3. CHI TIẾT TRIỂN KHAI KỸ THUẬT

### CV01 – Thiết kế CSDL & Cơ chế ACID, Chống trùng, Chống âm kho (7 điểm)
1. **Mô hình 5 bảng CSDL chuẩn:**
   * `Products`: Mã sản phẩm (`product_id` - PK), tên, đơn vị tính.
   * `Inventory`: Quản lý tồn kho theo sản phẩm (`product_id` - PK, FK tham chiếu `Products`), số lượng `quantity`.
   * `Users`: Quản lý người dùng (`user_id` - PK, `username` - UNIQUE, `password_hash`, `role`).
   * `ScanPoints`: Quản lý điểm quét (`scan_point_id` - PK, tên điểm quét).
   * `warehouse_transactions`: Lịch sử giao dịch (`transaction_id` - PK, `product_id`, `transaction_type`, `quantity`, `transaction_time`, `user_id`, `scan_point_id`).

2. **Cơ chế chống trùng giao dịch (3 lớp):**
   * *Lớp 1 (Ứng dụng/Procedure):* Kiểm tra `SELECT COUNT(*)` theo `transaction_id`. Nếu đã tồn tại, báo lỗi `Ma giao dich da ton tai` và `ROLLBACK` ngay lập tức.
   * *Lớp 2 (Ràng buộc CSDL):* `PRIMARY KEY (transaction_id)` ngăn chặn triệt để 2 giao dịch cùng mã lọt vào CSDL.
   * *Lớp 3 (Mã phản hồi API):* Bắt lỗi trùng và trả về HTTP `409 Conflict` kèm thông báo rõ ràng, không làm thay đổi tồn kho.

3. **Cơ chế chống tồn âm kho (3 lớp):**
   * *Lớp 1 (Khóa dòng chống tranh chấp):* Sử dụng `SELECT quantity FROM Inventory ... FOR UPDATE`. Khi 2 điểm quét cùng xuất 1 mặt hàng, giao dịch thứ hai bắt buộc phải xếp hàng chờ giao dịch thứ nhất `COMMIT`.
   * *Lớp 2 (Kiểm tra logic):* Khi `transaction_type = 'EXPORT'`, nếu `quantity > v_stock` thì phát tín hiệu `SIGNAL SQLSTATE '45000'` từ chối xuất.
   * *Lớp 3 (Ràng buộc toàn vẹn CSDL):* `CONSTRAINT chk_inventory_nonnegative CHECK (quantity >= 0)` trên bảng `Inventory`.

---

### CV02 – Dịch vụ API & Mô hình Phân quyền 3 tầng (6 điểm)

#### Mô hình Phân quyền 3 tầng độc lập:
```
+-----------------------------------------------------------------------+
| TẦNG 1: ỨNG DỤNG (RBAC & SHA-256 Authentication)                      |
| - Xác thực qua POST /api/login bằng mật khẩu băm SHA-256.             |
| - Phân quyền theo 4 vai trò:                                          |
|   * admin:     Toàn quyền (Nhập, Xuất, Xem tồn, Quản lý User).        |
|   * warehouse: Thủ kho (Nhập, Xuất, Xem tồn).                         |
|   * employee:  Nhân viên quét (Chỉ được Nhập, cấm Xuất kho - 403).     |
|   * viewer:    Chỉ xem (Cấm mọi thao tác ghi nhập/xuất - 403).        |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
| TẦNG 2: CƠ SỞ DỮ LIỆU (Nguyên tắc Đặc quyền tối thiểu - Least Priv)  |
| - Dịch vụ API kết nối CSDL bằng tài khoản riêng: 'wh_store'           |
| - Không dùng tài khoản root / admin.                                  |
| - Quyền hạn cấp phát: Chỉ SELECT trên các bảng danh mục và EXECUTE    |
|   trên Stored Procedure 'sp_warehouse_transaction'.                  |
| - Không cấp quyền trực tiếp INSERT/UPDATE/DELETE trên bảng Inventory. |
+-----------------------------------------------------------------------+
                                   |
                                   v
+-----------------------------------------------------------------------+
| TẦNG 3: HỆ ĐIỀU HÀNH (Cô lập người dùng & Phân quyền thư mục)        |
| - Dịch vụ API chạy dưới tài khoản OS riêng: 'wh_service'              |
| - Tác vụ sao lưu chạy dưới tài khoản OS riêng: 'wh_backup'            |
| - C:\SmartWarehouse\app:     wh_service chỉ có quyền đọc + chạy (RX). |
| - C:\SmartWarehouse\backup:  Chỉ wh_backup có quyền ghi (M).          |
|   wh_service hoàn toàn không có quyền truy cập vào thư mục backup!     |
+-----------------------------------------------------------------------+
```

#### Danh sách Endpoint RESTful API (Cổng 8080):
| Phương thức | Endpoint | Mô tả | Quyền truy cập |
|---|---|---|---|
| `POST` | `/api/login` | Xác thực đăng nhập qua mật khẩu băm SHA-256, cấp Bearer Token | Public |
| `POST` | `/api/transactions` | Ghi nhận giao dịch nhập/xuất kho (ACID qua Stored Procedure) | admin, warehouse, employee (chỉ NHẬP) |
| `GET` | `/api/transactions/<txn_id>` | Tra cứu chi tiết một giao dịch theo mã | Mọi user hợp lệ |
| `GET` | `/api/transactions/recent` | Lấy 10 giao dịch mới nhất trong hệ thống | Mọi user hợp lệ |
| `GET` | `/api/inventory` | Xem danh sách tồn kho toàn bộ 100 sản phẩm | Mọi user hợp lệ |
| `GET` | `/api/inventory/<product_id>`| Xem tồn kho chi tiết của một mặt hàng cụ thể | Mọi user hợp lệ |
| `GET` | `/api/users` | Xem danh sách người dùng hệ thống | Chỉ `admin` |

---

### CV03 – Sao lưu theo lịch, Khôi phục thật & Đo kiểm RTO (7 điểm)

1. **Lịch sao lưu tự động định kỳ:**
   * Tác vụ: `WH-SaoLuu-CSDL` đăng ký trong **Windows Task Scheduler**.
   * Tài khoản thực thi: `NT AUTHORITY\SYSTEM` (đảm bảo quyền hạn độc lập).
   * Chu kỳ chính thức: **Mỗi 2 giờ (120 phút)** tự động thực thi 1 lần.

2. **Quy trình sao lưu an toàn (`01_sao_luu.ps1`):**
   * Sử dụng công cụ chuẩn `mysqldump` xuất toàn bộ Schema, Table, Data, Stored Procedure (`--routines`), Triggers, Events.
   * Tham số xác thực nạp qua `--defaults-extra-file="C:\SmartWarehouse\backup\.my_dump.cnf"` (file được khóa quyền nghiêm ngặt, không lộ mật khẩu trên dòng lệnh).
   * Ghi nhật ký đầy đủ vào `C:\SmartWarehouse\backup\backup.log` gồm: Thời điểm, Nguồn kích hoạt (`Lich`/`ThuCong`), Tên file, Kích thước, Mã băm SHA-256, Thời gian chạy, Kết quả (`OK`/`LOI`).
   * Tự động dọn dẹp các bản sao lưu cũ hơn 14 ngày.

3. **Khôi phục độc lập & Đối chiếu tính toàn vẹn (`03_khoi_phuc_va_doi_chieu.ps1`):**
   * Khôi phục bản dump mới nhất vào CSDL độc lập: `smart_warehouse_restore`.
   * Tự động kiểm tra và so khớp 100% 12 hạng mục giữa CSDL gốc và CSDL khôi phục:
     * Số bản ghi các bảng: `Products`, `Inventory`, `Users`, `ScanPoints`, `warehouse_transactions`.
     * Tổng số lượng tồn kho (`SUM(quantity)`).
     * Mã băm bảng `CHECKSUM TABLE` của cả 5 bảng.
     * Số lượng Stored Procedure.
   * **Đo kiểm chỉ số RTO:**
     * RTO cam kết giả định: 1800 giây (30 phút).
     * Thời gian khôi phục thực tế đo được: **0.4 – 0.6 giây** $\rightarrow$ Nằm an toàn sâu trong ngưỡng RTO cho phép.
     * Kết quả được tự động kết xuất ra file minh chứng tại `C:\SmartWarehouse\evidence\restore_test_*.txt`.

---

## 4. DANH SÁCH TÀI KHOẢN KIỂM THỬ

Toàn bộ mật khẩu đã được băm SHA-256 lưu trong CSDL. Khi kiểm thử qua API hoặc test script, sử dụng các tài khoản sau:

| Username | Mật khẩu gốc | Vai trò (Role) | Quyền hạn nghiệp vụ |
|---|---|---|---|
| `admin_demo` / `admin` | `Admin@2026` | `admin` | Toàn quyền: Nhập kho, Xuất kho, Xem tồn kho, Quản lý Users |
| `thukho_demo` / `thukho01` | `Kho@2026` | `warehouse` | Thủ kho: Nhập kho, Xuất kho, Xem tồn kho (Cấm xem Users - 403) |
| `nhanvien_demo` / `nv01` | `Kho@2026` | `employee` | Nhân viên điểm quét: Chỉ được Nhập kho (Cấm Xuất kho - 403) |
| `nv02_demo` / `nv02` | `Kho@2026` | `employee` | Nhân viên điểm quét: Chỉ được Nhập kho (Cấm Xuất kho - 403) |
| `viewer_demo` / `quanly01` | `View@2026` | `viewer` | Quản lý/Khách: Chỉ xem tồn kho (Cấm mọi thao tác ghi kho - 403) |

---

## 5. QUY TRÌNH CHẠY VÀ KIỂM THỬ NHANH KHI BẢO VỆ

### Bước 1: Khởi tạo/Làm mới CSDL MySQL (Nếu cần dựng lại từ đầu)
Mở PowerShell và chạy lần lượt các file SQL theo thứ tự:
```powershell
cd "D:\Dowloads\CNNT-main\sinh-vien-3\01_CSDL_SQL"

# 1. Tạo CSDL & bảng
Get-Content 01_create_database.sql -Raw | & "C:\Program Files\MySQL\MySQL Server 9.3\bin\mysql.exe" -u root -p smart_warehouse

# 2. Nạp dữ liệu 100 sản phẩm & tài khoản mẫu
Get-Content 02_insert_sample_data.sql -Raw | & "C:\Program Files\MySQL\MySQL Server 9.3\bin\mysql.exe" -u root -p smart_warehouse

# 3. Tạo Stored Procedure
Get-Content 03_create_procedure.sql -Raw | & "C:\Program Files\MySQL\MySQL Server 9.3\bin\mysql.exe" -u root -p smart_warehouse

# 4. Phân quyền tài khoản wh_store
Get-Content 04_create_permissions.sql -Raw | & "C:\Program Files\MySQL\MySQL Server 9.3\bin\mysql.exe" -u root -p smart_warehouse

# 5. Đồng bộ alias điểm quét SP01, SP02
Get-Content 06_sync_sv1_sv3_aliases.sql -Raw | & "C:\Program Files\MySQL\MySQL Server 9.3\bin\mysql.exe" -u root -p smart_warehouse
```

### Bước 2: Khởi động API Server
```powershell
cd "D:\Dowloads\CNNT-main\sinh-vien-3\04_DICH_VU_API"
python app.py
```
*Server sẽ khởi động và lắng nghe tại `http://0.0.0.0:8080`.*

### Bước 3: Chạy bộ kiểm thử tự động 26 ca kiểm thử
Mở một cửa sổ PowerShell mới:
```powershell
cd "D:\Dowloads\CNNT-main\sinh-vien-3\04_DICH_VU_API"
python test_all_features.py
```
👉 **Kết quả kỳ vọng:** Đạt chuẩn **26/26 ca PASS 100%**, bao gồm xác thực sai mật khẩu (401), phân quyền RBAC (403), nhập/xuất kho (201), chống trùng mã giao dịch (409), chống âm kho (400), kiểm tra dữ liệu 100 mặt hàng.

### Bước 4: Kiểm tra Lịch sao lưu Task Scheduler & Khôi phục đối chiếu
```powershell
# 1. Xem trạng thái lịch sao lưu tự động (Cần mở PowerShell Run as administrator)
Get-ScheduledTask -TaskName "WH-SaoLuu-CSDL" | Get-ScheduledTaskInfo

# 2. Chạy thử nghiệm quy trình khôi phục và đối chiếu tự động
cd "D:\Dowloads\CNNT-main\sinh-vien-3\02_BACKUP_RESTORE"
.\03_khoi_phuc_va_doi_chieu.ps1 -SaoLuuMoiTruoc
```
👉 **Kết quả:** Màn hình sẽ in bảng đối chiếu chi tiết toàn bộ các bảng CSDL gốc và CSDL khôi phục đều khớp 100%, thời gian khôi phục đạt chuẩn RTO. File kết quả được tự động lưu vào `C:\SmartWarehouse\evidence\`.
