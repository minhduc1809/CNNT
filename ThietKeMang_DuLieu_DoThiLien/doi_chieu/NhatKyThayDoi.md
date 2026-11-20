# Nhật ký thay đổi chuẩn chung – Đề tài 22

Áp dụng cho: `05_GiaoUocAPI.md`, `06_TuDienDuLieu.md` / `du_lieu/TuDienDuLieu.csv`, `du_lieu/schema.sql`, bảng IP và quy tắc truy cập.

Quy tắc:
1. Sau Cổng 1, **không ai tự đổi** tên trường, mã lỗi, định dạng mã giao dịch hay địa chỉ máy chủ trong mã của mình.
2. Muốn đổi: báo SV1 → nhóm đồng ý → SV1 sửa tài liệu chuẩn, **tăng phiên bản**, ghi một dòng vào bảng dưới, báo cả nhóm.
3. Sau mỗi thay đổi, SV1 chạy lại `doi_chieu_ten_truong.py` và `du_lieu/xuat_tu_dien.py`.

| Phiên bản | Ngày | Thay đổi | Lý do | Ảnh hưởng tới | Người đề xuất | Đã báo nhóm |
|---|---|---|---|---|---|---|
| v0.9 | 26/10/2026 | Bản nháp: 4 VLAN (10, 20, 30 + 99 quản lý thiết bị) | Bản thiết kế đầu | — | SV1 | — |
| v1.0 | 26/10/2026 | Rút về **3 VLAN** theo thẻ việc; IP quản lý switch chuyển sang 192.168.10.2 (VLAN 10), chỉ PC-QUANTRI telnet được | Đúng yêu cầu “sơ đồ mạng 3 VLAN”, đơn giản hóa cấu hình | Cấu hình PT, bảng IP, ACL | SV1 | Tại Cổng 1 |
| v1.0 | 26/10/2026 | Luồng dữ liệu tách thành 6 bước (lưu và cập nhật tồn là 2 bước, cùng một COMMIT); tách riêng nhánh trùng | Đúng yêu cầu thẻ việc; rõ cho SV3/SV4 | Sơ đồ 01, 04; tài liệu 03 | SV1 | Tại Cổng 1 |
| | | | | | | |
