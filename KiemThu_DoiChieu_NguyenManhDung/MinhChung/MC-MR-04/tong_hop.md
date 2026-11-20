# Tổng hợp thử tải – 2026-11-15 07:42:08

Máy chủ `http://127.0.0.1:5000` · mỗi kịch bản 60 s · nhịp 3.0 s/lần/điểm · tỉ lệ gửi trùng 5%

| Chỉ tiêu | 2_diem_quet | 4_diem_quet |
|---|---|---|
| Số tiến trình (điểm quét) | 2 | 4 |
| Tổng yêu cầu | 40 | 80 |
| Giao dịch mới thành công (201) | 37 | 76 |
| Gửi trùng / nhận 409 | 3 / 3 | 4 / 4 |
| Thông lượng giao dịch mới (GD/s) | 0.617 | 1.267 |
| Độ trễ trung bình (ms) | 348.7 | 597.12 |
| Độ trễ p95 (ms) | 442.82 | 644.5 |
| Độ trễ lớn nhất (ms) | 511.6 | 747.83 |
| Lỗi khác (không mong đợi) | không có | không có |
| Đọc lại mẫu giao dịch 201 | 20/20 | 20/20 |
| Đối chiếu tồn all_match | HTTP 404 | HTTP 404 |
