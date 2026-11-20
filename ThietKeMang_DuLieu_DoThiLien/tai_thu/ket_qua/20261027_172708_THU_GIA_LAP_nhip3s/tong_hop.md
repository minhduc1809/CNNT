# Tổng hợp thử tải – 2026-10-27 17:27:48

Máy chủ `http://127.0.0.1:18080` · mỗi kịch bản 15.0 s · nhịp 3.0 s/lần/điểm · tỉ lệ gửi trùng 5%

| Chỉ tiêu | 2_diem_quet | 4_diem_quet |
|---|---|---|
| Số tiến trình (điểm quét) | 2 | 4 |
| Tổng yêu cầu | 10 | 20 |
| Giao dịch mới thành công (201) | 9 | 19 |
| Gửi trùng / nhận 409 | 1 / 1 | 1 / 1 |
| Thông lượng giao dịch mới (GD/s) | 0.6 | 1.267 |
| Độ trễ trung bình (ms) | 21.44 | 24.13 |
| Độ trễ p95 (ms) | 35.69 | 39.19 |
| Độ trễ lớn nhất (ms) | 39.77 | 45.22 |
| Lỗi khác (không mong đợi) | không có | không có |
| Đọc lại mẫu giao dịch 201 | 9/9 | 19/19 |
| Đối chiếu tồn all_match | True | True |
