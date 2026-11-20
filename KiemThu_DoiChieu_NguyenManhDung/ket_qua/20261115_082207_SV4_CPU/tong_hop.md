# Tổng hợp thử tải – 2026-11-15 08:24:20

Máy chủ `http://127.0.0.1:5000` · mỗi kịch bản 60 s · nhịp 3.0 s/lần/điểm · tỉ lệ gửi trùng 5%

| Chỉ tiêu | 2_diem_quet | 4_diem_quet |
|---|---|---|
| Số tiến trình (điểm quét) | 2 | 4 |
| Tổng yêu cầu | 40 | 80 |
| Giao dịch mới thành công (201) | 36 | 76 |
| Gửi trùng / nhận 409 | 4 / 4 | 4 / 4 |
| Thông lượng giao dịch mới (GD/s) | 0.6 | 1.267 |
| Độ trễ trung bình (ms) | 304.11 | 539.02 |
| Độ trễ p95 (ms) | 355.63 | 633.47 |
| Độ trễ lớn nhất (ms) | 407.45 | 769.48 |
| Lỗi khác (không mong đợi) | không có | không có |
| Đọc lại mẫu giao dịch 201 | 20/20 | 20/20 |
| Đối chiếu tồn all_match | HTTP 404 | HTTP 404 |
