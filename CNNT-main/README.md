# HỆ THỐNG QUẢN LÝ KHO HÀNG THÔNG MINH – ĐỀ TÀI 22
> **Học phần:** Nhập môn công nghệ nền tảng (RIPT1304) – Học viện Công nghệ Bưu chính Viễn thông (PTIT)  
> **Trọng tâm đề tài:** Hạ tầng CNTT (Mạng phân vùng VLAN, Tường lửa, Máy chủ Linux, CSDL MySQL phân quyền 3 tầng, Điểm quét gửi tin qua mạng, Cơ chế xử lý mất mạng hàng đợi & Kiểm thử đo đạc tài nguyên).

---

## 📁 Cấu trúc thư mục dự án

```text
CNNT-main/
├── SV1_ThietKeMang_DuLieu/          # SV1: Thiết kế mạng 3 vùng VLAN, tường lửa, mô hình CSDL
│   ├── bang_ip/                     # Bảng phân hoạch IP chi tiết các vùng mạng
│   ├── mo_hinh_du_lieu/             # Sơ đồ ERD, luồng dữ liệu nghiệp vụ
│   ├── tai_thu/                     # Kịch bản sinh tải giả lập
│   └── uoc_luong/                   # Mô hình ước lượng tài nguyên khi tăng điểm quét
│
├── diem-quet/                       # SV2: Chương trình dòng lệnh 2 điểm quét SCAN01 & SCAN02
│   ├── scanner.py                   # Ứng dụng điểm quét (gửi API, hàng đợi gửi lại khi mất mạng)
│   ├── config_scan01.json           # Cấu hình điểm quét khu Nhập (SCAN01)
│   ├── config_scan02.json           # Cấu hình điểm quét khu Xuất (SCAN02)
│   ├── logs/                        # Nhật ký giao dịch lưu vết tại máy khách
│   └── queue/                       # Hàng đợi cục bộ lưu trữ giao dịch chờ gửi lại
│
├── sinh-vien-3/                     # SV3: Máy chủ, CSDL MySQL, Dịch vụ API & Sao lưu
│   ├── 01_CSDL_SQL/                 # Kịch bản khởi tạo database, dữ liệu mẫu, Stored Procedure, phân quyền
│   │   ├── 01_create_database.sql   # Tạo schema smart_warehouse và các bảng
│   │   ├── 02_insert_sample_data.sql# Nạp 100 sản phẩm và tồn kho ban đầu
│   │   ├── 03_create_procedure.sql  # Thủ tục sp_warehouse_transaction (ACID, chống âm kho)
│   │   ├── 04_create_permissions.sql# Phân quyền CSDL (wh_admin, wh_store, wh_employee, wh_viewer)
│   │   └── 05_test_transactions.sql # SQL kiểm thử giao dịch trực tiếp
│   ├── 02_BACKUP_RESTORE/           # Bản sao lưu định kỳ và kịch bản khôi phục (CV03)
│   ├── 03_API_CONTRACT/             # Đặc tả giao ước API chuẩn giữa SV1 và SV3
│   └── 04_DICH_VU_API/              # Dịch vụ API chính thức của hệ thống (Flask RESTful)
│       ├── app.py                   # Mã nguồn API Server (Phân quyền 3 tầng, kết nối wh_store)
│       ├── test_all_features.py     # Bộ kiểm thử tự động 25 ca nghiệm thu toàn diện (KT1, KT2, KT3)
│       ├── test_rbac.py             # Bộ kiểm thử ma trận phân quyền RBAC
│       ├── .env                     # Cấu hình kết nối MySQL an toàn
│       └── requirements.txt         # Thư viện phụ thuộc
│
└── docs/                            # SV4 & Nhóm: Báo cáo chung, kế hoạch kiểm thử và minh chứng đo đạc
```

---

## 👥 Phân công nhiệm vụ các thành viên (25 điểm/thành viên)

| Thành viên | Vai trò chính | Nhiệm vụ chuyên môn (CV01 - CV03) |
| :--- | :--- | :--- |
| **SV1** | Thiết kế mạng & Mô hình dữ liệu | • Dựng 3 vùng mạng (VLAN 10, 20, 30) & Tường lửa.<br>• Thiết kế mô hình dữ liệu (ERD) & Từ điển dữ liệu.<br>• Xây dựng giao ước API & Mô hình ước lượng tải. |
| **SV2** | Hai điểm quét giả lập | • Phát triển ứng dụng điểm quét `SCAN01`, `SCAN02`.<br>• Gửi giao dịch qua mạng, kiểm tra hợp lệ đầu vào.<br>• Hàng đợi lưu tạm tại máy trạm, gửi lại có kiểm soát (Backoff) khi mất mạng. |
| **SV3** | Máy chủ, CSDL, Phân quyền & Sao lưu | • Thiết lập máy chủ Linux & CSDL MySQL `smart_warehouse`.<br>• Dịch vụ API tối thiểu & Phân quyền 3 tầng (Hệ điều hành, CSDL `wh_store`, Dịch vụ RBAC).<br>• Sao lưu định kỳ tự động & Đo lường thời gian khôi phục CSDL. |
| **SV4** | Kiểm thử & Đo đạc hạ tầng | • Kiểm thử nghiệm thu giao dịch hợp lệ & Chống trùng (KT1, KT2).<br>• Kiểm thử bảo mật phân quyền & Chống âm kho (KT3a, KT3b).<br>• Đo đạc tài nguyên (CPU, RAM, Băng thông) & Đối chiếu sau mất mạng. |

---

## 🚀 Hướng dẫn cài đặt & Vận hành nhanh

### 1. Chuẩn bị môi trường
* **Python:** Phiên bản 3.10 trở lên (`python --version`)
* **MySQL Server:** Phiên bản 8.0 hoặc 9.0+ đang chạy tại cổng `3306`

Cài đặt thư viện Python cần thiết:
```powershell
pip install flask pymysql python-dotenv requests
```

---

### 2. Thiết lập Cơ sở dữ liệu MySQL (SV3)
Mở **MySQL Workbench** hoặc terminal MySQL với tài khoản `root`, chạy lần lượt các file trong thư mục `sinh-vien-3/01_CSDL_SQL/`:
1. `01_create_database.sql`: Tạo database `smart_warehouse` và các bảng (`products`, `inventory`, `scanpoints`, `users`, `warehouse_transactions`).
2. `02_insert_sample_data.sql`: Nạp danh mục 100 sản phẩm và tồn kho đầu kỳ.
3. `03_create_procedure.sql`: Tạo Stored Procedure `sp_warehouse_transaction` hỗ trợ khóa dòng `FOR UPDATE`.
4. `04_create_permissions.sql`: Tạo tài khoản và phân quyền:
   * `wh_store`: Dùng cho API, chỉ có quyền `SELECT` và `EXECUTE` procedure. Mật khẩu: `StoreUser@2026`.
   * `wh_viewer`: Chỉ xem (`SELECT`), mật khẩu: `ViewerUser@2026`.
   * `wh_employee`: Chỉ xem thông tin kho, mật khẩu: `EmpUser@2026`.
   * `wh_admin`: Toàn quyền quản trị, mật khẩu: `AdminUser@2026`.

*(Hoặc dùng lệnh script thiết lập nhanh nếu đã có quyền root).*

---

### 3. Cấu hình file môi trường (`.env`)
Để dịch vụ API có thể kết nối đến cơ sở dữ liệu MySQL một cách an toàn và tự động, hệ thống sử dụng file cấu hình `.env` đặt tại thư mục:
📂 `CNNT-main/sinh-vien-3/04_DICH_VU_API/.env`

> [!TIP]
> Dự án đã tạo sẵn file mẫu `CNNT-main/sinh-vien-3/04_DICH_VU_API/.env.example`. Nếu bạn clone dự án từ Git về mà chưa có `.env`, chỉ cần sao chép hoặc đổi tên file `.env.example` thành `.env`:
> ```powershell
> cp CNNT-main/sinh-vien-3/04_DICH_VU_API/.env.example CNNT-main/sinh-vien-3/04_DICH_VU_API/.env
> ```

**Nội dung chi tiết của file `.env`:**
```env
# Địa chỉ IP của máy chủ MySQL (127.0.0.1 nếu chạy cục bộ, hoặc IP VLAN 30 của SV3)
DB_HOST=127.0.0.1

# Cổng dịch vụ MySQL mặc định
DB_PORT=3306

# Tài khoản CSDL đặc quyền tối thiểu theo chuẩn CV02 (không dùng root)
DB_USER=wh_store

# Mật khẩu tài khoản wh_store
DB_PASS=StoreUser@2026

# Tên cơ sở dữ liệu
DB_NAME=smart_warehouse
```

---

### 4. Khởi chạy Dịch vụ API Máy chủ (SV3)
Mở cửa sổ dòng lệnh thứ nhất:
```powershell
cd CNNT-main/sinh-vien-3/04_DICH_VU_API
python app.py
```
> Server sẽ khởi chạy tại: `http://localhost:5000` (kết nối CSDL bằng user đặc quyền tối thiểu `wh_store`).

---

### 5. Vận hành Điểm quét hàng hóa (SV2)
Mở 2 cửa sổ dòng lệnh độc lập tượng trưng cho 2 máy trạm tại kho:

* **Điểm quét 01 (Khu vực Nhập kho):**
  ```powershell
  cd CNNT-main/diem-quet
  python scanner.py config_scan01.json
  ```

* **Điểm quét 02 (Khu vực Xuất kho):**
  ```powershell
  cd CNNT-main/diem-quet
  python scanner.py config_scan02.json
  ```

**Nhập thử nghiệm:**
* Nhập mã hàng: `SP001`
* Loại giao dịch: `NHAP` (hoặc `XUAT`)
* Số lượng: `10`
* Chương trình sẽ sinh mã giao dịch định dạng `SPxx-YYYYMMDD-nnnn`, ghi hàng đợi và gửi lên máy chủ xác nhận `DA_XAC_NHAN`.

---

### 6. Chạy bộ kiểm thử tự động toàn diện (SV4)
Mở một cửa sổ dòng lệnh khác để chạy kiểm thử nghiệm thu 25 ca chức năng:
```powershell
cd CNNT-main/sinh-vien-3/04_DICH_VU_API
python test_all_features.py
```

---

## 🧪 Danh mục các ca kiểm thử nghiệm thu

| Nhóm kiểm thử | Các ca kiểm thử (TC) | Kết quả kiểm chứng |
| :--- | :--- | :---: |
| **Phân quyền RBAC (KT3a)** | `TC01` - `TC11`: Đăng nhập cấp Token 4 vai trò (`admin`, `warehouse`, `employee`, `viewer`). Chặn viewer ghi dữ liệu (`403`), chặn nhân viên xuất kho (`403`), bảo vệ danh sách user. | ✅ PASS 100% |
| **Nhập/Xuất kho (KT1)** | `TC12` - `TC14`: Nhập kho `SP002` tại SCAN01 (+20), Xuất kho `SP002` tại SCAN02 (-8), đọc lại chi tiết giao dịch từ MySQL. | ✅ PASS 100% |
| **Chống trùng lặp (KT2)** | `TC15`: Gửi lại cùng mã `txn_id`. CSDL trả lỗi `409 DUPLICATE_TXN`, số lượng tồn kho giữ nguyên không đổi lần hai. | ✅ PASS 100% |
| **Chống âm kho (KT3)** | `TC16`: Thử xuất vượt quá tồn hiện có. Stored Procedure kích hoạt chặn `INSUFFICIENT_STOCK`, tồn kho không bị âm. | ✅ PASS 100% |
| **Kiểm tra biên & Bắt lỗi** | `TC17` - `TC23`: Kiểm tra sản phẩm giả, điểm quét giả, số lượng âm, số lượng = 0, vượt ngưỡng 10.000, sai định dạng giao dịch, thiếu trường dữ liệu. | ✅ PASS 100% |
| **Báo cáo & Giám sát** | `TC24` - `TC25`: Lấy danh sách giao dịch gần nhất và toàn bộ danh mục tồn kho 100 sản phẩm. | ✅ PASS 100% |

---

## 🔒 Cơ chế bảo mật phân quyền 3 tầng

1. **Tầng Hệ điều hành (OS Layer):**
   * Dịch vụ chạy dưới tài khoản dịch vụ riêng biệt. Thư mục dữ liệu và sao lưu được phân tách quyền đọc/ghi nghiêm ngặt.
2. **Tầng Cơ sở dữ liệu (Database Layer):**
   * Backend không dùng tài khoản `root`, chỉ kết nối bằng tài khoản **`wh_store`** có quyền tối thiểu (`SELECT` và `EXECUTE` Stored Procedure). Ngăn chặn rủi ro xóa bảng hoặc SQL Injection.
3. **Tầng Dịch vụ ứng dụng (API RBAC Layer):**
   * Phân định chặt chẽ quyền hạn của 4 vai trò:
     * `viewer` (`viewer_demo`): Chỉ có quyền đọc báo cáo (`GET`), cấm mọi thao tác ghi (`403 Forbidden`).
     * `employee` (`nhanvien_demo`): Chỉ được quét nhập kho (`IMPORT`), cấm xuất kho (`403 Forbidden`).
     * `warehouse` (`thukho_demo`): Toàn quyền nhập/xuất kho vật lý.
     * `admin` (`admin_demo`): Quản trị viên tối cao, quản lý người dùng và cấu hình hệ thống.
