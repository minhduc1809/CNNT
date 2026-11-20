# Kết quả kiểm tra Cổng 2 – 2026-10-27 17:25:31

Máy chủ: `http://127.0.0.1:18080` · Kết quả: **10/10 bước ĐẠT**

| Bước | Thời điểm | Nội dung | Thực tế | Kết quả |
|---|---|---|---|---|
| C2-01 | 2026-10-27 17:25:31 | nv01 đăng nhập tại SP01 | HTTP 200, role=NHANVIEN | ĐẠT |
| C2-02 | 2026-10-27 17:25:31 | Đọc tồn SP001 trước khi gửi | tồn = 100 | ĐẠT |
| C2-03 | 2026-10-27 17:25:31 | GỬI: SP01 NHAP 5 SP001, txn_id SP01-20261027-9731 | HTTP 201, stock_after=105, server_time=2026-10-27T17:25:31 | ĐẠT |
| C2-04 | 2026-10-27 17:25:31 | LƯU + ĐỌC LẠI: GET /api/transactions/{txn_id} khớp dữ liệu đã gửi | HTTP 200, trường lệch=không, username=nv01, server_time=2026-10-27T17:25:31 | ĐẠT |
| C2-05 | 2026-10-27 17:25:31 | Tồn SP001 sau giao dịch = tồn trước + 5, last_txn_id đúng | tồn 100 -> 105, last_txn_id=SP01-20261027-9731 | ĐẠT |
| C2-06 | 2026-10-27 17:25:31 | Gửi lại CÙNG txn_id (mô phỏng mất phản hồi) | HTTP 409 DUPLICATE_TXN, tồn 105 -> 105 | ĐẠT |
| C2-07 | 2026-10-27 17:25:31 | GỬI từ điểm quét thứ hai: SP02/nv02 XUAT 2 SP001, txn_id SP02-20261027-9731 | HTTP 201, stock_after=103 | ĐẠT |
| C2-08 | 2026-10-27 17:25:31 | ĐỌC LẠI lịch sử bằng tài khoản khác (thukho01), lọc SP02 | HTTP 200, thấy SP02-20261027-9731 của nv02: True | ĐẠT |
| C2-09 | 2026-10-27 17:25:31 | quanly01 (chỉ xem) cố ghi giao dịch | HTTP 403 FORBIDDEN, tồn = 103 | ĐẠT |
| C2-10 | 2026-10-27 17:25:31 | Đối chiếu tồn lưu trữ với Σ NHAP − Σ XUAT | HTTP 200, all_match=True | ĐẠT |
