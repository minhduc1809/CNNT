# SINH VIÊN 3: MÁY CHỦ, CSDL, PHÂN QUYỀN VÀ SAO LƯU (ĐỀ TÀI 22)

---

## 1. Danh mục các sản phẩm bàn giao theo mã công việc

| Thư mục | Tên thành phần | Mã việc | Mô tả nội dung |
|---|---|:---:|---|
| [`01_CSDL_SQL/`](01_CSDL_SQL/) | Cơ sở dữ liệu MySQL `smart_warehouse` | `CV01` | Script tạo bảng, 100 sản phẩm mẫu, Stored Procedure `sp_warehouse_transaction` chống trùng và chống âm tồn, phân quyền tài khoản MySQL. |
| [`02_BACKUP_RESTORE/`](02_BACKUP_RESTORE/) | Sao lưu & Khôi phục dữ liệu | `CV03` | Bản sao lưu `mysqldump`, kịch bản cron sao lưu tự động và hướng dẫn khôi phục, đối chiếu dữ liệu. |
| [`03_API_CONTRACT/`](03_API_CONTRACT/) | Giao ước API | `CV02` | Tài liệu giao ước API phối hợp giữa SV3 với SV1 và SV2. |
| [`04_DICH_VU_API/`](04_DICH_VU_API/) | Dịch vụ API & Phân quyền 3 tầng | `CV02` | Mã nguồn máy chủ API (Flask/Python), phân quyền RBAC 4 vai trò, kết nối tài khoản CSDL `wh_store`, kịch bản phân quyền HĐH Linux và bộ kiểm thử 10 ca tự động. |

---

## 2. Hướng dẫn chạy thử nghiệm nhanh toàn bộ hệ thống SV3

1. **Chạy dịch vụ API:**
   ```bash
   cd 04_DICH_VU_API
   python app.py --mock --port 8080
   ```
2. **Chạy kiểm thử tự động 10 ca nghiệp vụ:**
   ```bash
   cd 04_DICH_VU_API
   python test_api.py --url http://127.0.0.1:8080
   ```
