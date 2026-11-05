# DỊCH VỤ API MÁY CHỦ CSDL MYSQL (SV3 - MÃ VIỆC CV02)
**Hệ thống Quản lý Kho Hàng Thông Minh – Đề tài 22**

---

## 1. Giới thiệu tổng quan
Dịch vụ API máy chủ được xây dựng nhằm đáp ứng toàn bộ các yêu cầu của **Sinh viên 3 (Mã việc CV02: Dịch vụ tối thiểu và phân quyền nhiều tầng)**, đồng thời tương thích 100% với **Giao ước API của SV1 (`05_GiaoUocAPI.md`)** và kết nối trực tiếp vào CSDL MySQL `smart_warehouse`.

### Điểm nổi bật:
1. **Kiến trúc đồng bộ tối thiểu (RESTful JSON):**
   - Không sử dụng hàng đợi tin nhắn (Message Queue) ở tầng lõi theo đúng yêu cầu đề bài.
   - Mọi giao dịch ghi kho đều thực thi nguyên tử (ACID Transaction) và chỉ trả về `201 Created` sau khi đã **COMMIT** vào MySQL.
2. **Khóa dòng và chống trùng giao dịch:**
   - Sử dụng lệnh `FOR UPDATE` (hoặc gọi Stored Procedure `sp_warehouse_transaction`) để chống âm kho khi nhiều điểm quét xuất hàng đồng thời.
   - Chặn tuyệt đối gửi trùng mã giao dịch `txn_id` (`409 Conflict`), trả về kết quả cũ và không thay đổi số lượng tồn.
3. **Phân quyền 3 tầng nghiêm ngặt (3-Tier Security):**
   - **Tầng Dịch vụ (API Layer):** RBAC phân định 4 vai trò (`ADMIN`, `THUKHO`, `NHANVIEN`, `QUANLY`). Tài khoản `QUANLY`/`xem01` bị chặn khi cố tình ghi giao dịch (`403 FORBIDDEN`).
   - **Tầng CSDL (Database Layer):** Dịch vụ kết nối bằng tài khoản `wh_store` (chỉ có quyền `SELECT` và `EXECUTE` Stored Procedure, không dùng `root`).
   - **Tầng Hệ điều hành (OS Layer):** Dịch vụ chạy dưới user không đặc quyền `wh_service`, thư mục dữ liệu `/var/lib/mysql` và thư mục sao lưu `/var/backups/warehouse` được phân quyền độc lập (`chmod 700`).
4. **Linh hoạt thử nghiệm:**
   - Tự động kết nối MySQL thật nếu có CSDL.
   - Tự động kích hoạt In-Memory Mock CSDL nếu đang chạy thử nghiệm trên máy trạm Windows chưa có MySQL.

---

## 2. Cấu trúc thư mục `04_DICH_VU_API/`

```text
sinh-vien-3/04_DICH_VU_API/
├── app.py                     # Mã nguồn máy chủ API chính (Flask)
├── config.json                # File cấu hình cổng mạng, kết nối MySQL, JWT
├── requirements.txt           # Danh mục thư viện Python phụ thuộc
├── test_api.py                # Script tự động kiểm thử 10 ca kiểm thử
├── README.md                  # Tài liệu hướng dẫn sử dụng và triển khai
└── service_config/
    ├── smart_warehouse_api.service  # File cấu hình systemd cho Linux
    └── setup_linux_permissions.sh   # Script cấu hình phân quyền 3 tầng Linux
```

---

## 3. Hướng dẫn chạy thử nghiệm nhanh trên máy cá nhân

### Bước 1: Cài đặt thư viện
```bash
pip install -r requirements.txt
```

### Bước 2: Chạy máy chủ API
* **Chạy với chế độ Mock DB (để test ngay không cần bật MySQL):**
  ```bash
  python app.py --mock --port 8080
  ```
* **Chạy kết nối MySQL thật:**
  ```bash
  python app.py --port 8080
  ```

### Bước 3: Chạy kịch bản kiểm thử tự động
Mở một cửa sổ dòng lệnh khác và gõ:
```bash
python test_api.py --url http://127.0.0.1:8080
```
Kết quả kiểm thử 10/10 ca sẽ được in ra với màu sắc trực quan, dùng để chụp ảnh minh chứng cho báo cáo của SV3.

---

## 4. Hướng dẫn triển khai lên máy chủ Linux thật (VLAN 30 - IP `192.168.30.10`)

### Bước 1: Đồng bộ mã nguồn lên máy chủ Linux
Sao chép thư mục `04_DICH_VU_API` vào thư mục `/opt/smart_warehouse_api` trên máy chủ Ubuntu.

### Bước 2: Chạy script phân quyền 3 tầng
```bash
cd /opt/smart_warehouse_api/service_config
chmod +x setup_linux_permissions.sh
sudo ./setup_linux_permissions.sh
```

### Bước 3: Cấu hình tài khoản CSDL `wh_store` trong MySQL
Đăng nhập vào MySQL bằng quyền `root`:
```bash
mysql -u root -p < ../../01_CSDL_SQL/04_create_permissions.sql
mysql -u root -p < ../../01_CSDL_SQL/06_sync_sv1_sv3_aliases.sql
```

### Bước 4: Khởi động dịch vụ tự động bằng systemd
```bash
sudo systemctl daemon-reload
sudo systemctl start smart_warehouse_api.service
sudo systemctl status smart_warehouse_api.service
```

---

## 5. Danh mục các Endpoint chuẩn theo Giao ước SV1

| Phương thức | Đường dẫn API | Mục đích | Quyền tối thiểu | Phản hồi chính |
|---|---|---|---|---|
| `POST` | `/api/login` | Đăng nhập cấp Bearer Token | Bất kỳ | `200 OK` (token, role) |
| `POST` | `/api/transactions` | Ghi nhận giao dịch nhập/xuất kho | `NHANVIEN`, `THUKHO`, `ADMIN` | `201 Created` / `409 Conflict` / `422 Unprocessable` / `403 Forbidden` |
| `GET` | `/api/transactions/{txn_id}` | Điểm quét đọc lại xác nhận đã lưu | `NHANVIEN` (chính mình), `THUKHO`, `ADMIN` | `200 OK` / `404 Not Found` |
| `GET` | `/api/transactions` | Tra cứu lịch sử giao dịch | Mọi vai trò (nhân viên chỉ xem của mình) | `200 OK` (danh sách) |
| `GET` | `/api/inventory` | Tra cứu tồn kho toàn bộ sản phẩm | Mọi vai trò | `200 OK` (danh sách) |
| `GET` | `/api/inventory/{product_code}` | Tra cứu tồn kho 1 sản phẩm | Mọi vai trò | `200 OK` / `404 Not Found` |
| `GET` | `/api/reconcile` | Đối chiếu tồn kho hệ thống | `THUKHO`, `ADMIN`, `QUANLY` | `200 OK` (bảng đối chiếu) |
| `GET` | `/api/health` | Kiểm tra trạng thái máy chủ | Không cần token | `200 OK` |
