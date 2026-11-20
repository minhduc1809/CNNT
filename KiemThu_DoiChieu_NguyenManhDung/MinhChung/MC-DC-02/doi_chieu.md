# Đối chiếu điểm quét với máy chủ – 15/11/2026 17:39:35

- Nhật ký điểm quét: diem-quet\queue (11 giao dịch)
- CSDL: bảng warehouse_transactions có 244 bản ghi (mọi nguồn)

## A. Từng giao dịch của điểm quét so với máy chủ

| Điểm quét | Kết luận | Số giao dịch |
|---|---|---|
| SP01 | KHỚP | 3 |
| SP01 | KHỚP (từ chối đúng, không lưu) | 2 |
| SP01 | THIẾU TRÊN MÁY CHỦ | 2 |
| SP02 | KHỚP (từ chối đúng, không lưu) | 2 |
| SP02 | THIẾU TRÊN MÁY CHỦ | 2 |

### Các dòng cần xem (không phải KHỚP)

| Điểm quét | txn_id | Ngày trong txn_id | Trạng thái điểm quét | Kết luận |
|---|---|---|---|---|
| SP01 | SP01-20261109-0001 | 20261109 | DA_XAC_NHAN | THIẾU TRÊN MÁY CHỦ |
| SP01 | SP01-20261109-0004 | 20261109 | DA_XAC_NHAN | THIẾU TRÊN MÁY CHỦ |
| SP02 | SP02-20261109-0001 | 20261109 | DA_XAC_NHAN | THIẾU TRÊN MÁY CHỦ |
| SP02 | SP02-20261109-0003 | 20261109 | DA_XAC_NHAN | THIẾU TRÊN MÁY CHỦ |

## B. Giao dịch chỉ có trên máy chủ (điểm quét không có trong nhật ký)

| Điểm quét | Nhóm | Số giao dịch |
|---|---|---|
| SP01 | khác (cần xem từng dòng) | 5 |
| SP01 | thử tải (tai_thu_sv4: ngày 20261115, số thứ tự từ 1001) | 77 |
| SP02 | khác (cần xem từng dòng) | 3 |
| SP02 | thử tải (tai_thu_sv4: ngày 20261115, số thứ tự từ 1001) | 71 |

### Chi tiết nhóm "khác"

| txn_id | Mặt hàng | Loại | SL | Tài khoản | Thời gian |
|---|---|---|---|---|---|
| SP01-20261114-0001 | SP002 | IMPORT | 10 | NV01 | 2026-11-14 21:50:40 |
| SP01-20261114-0002 | SP002 | IMPORT | 10 | NV01 | 2026-11-14 21:51:18 |
| SP02-20261114-0001 | SP002 | IMPORT | 10 | thukho01 | 2026-11-14 21:52:10 |
| SP02-20261114-0002 | SP002 | EXPORT | 4 | thukho01 | 2026-11-14 21:52:10 |
| SP02-20261114-0003 | SP002 | EXPORT | 4 | thukho01 | 2026-11-14 21:52:31 |
| SP01-20261114-5323 | SP002 | EXPORT | 30 | TK01 | 2026-11-14 22:54:25 |
| SP01-20261115-0003 | SP002 | IMPORT | 5 | NV01 | 2026-11-15 00:28:32 |
| SP01-20261115-0004 | SP002 | IMPORT | 5 | NV01 | 2026-11-15 00:42:00 |

Chi tiết toàn bộ: chi_co_tren_may_chu.csv

## C. Tồn kho: tồn gốc + nhập − xuất so với tồn thực tế

Khớp ở cả 100 mặt hàng: tồn thực tế = tồn gốc (file seed 02) + tổng nhập − tổng xuất của mọi giao dịch trong bảng.

## D. Khoảng trống số thứ tự (seq_no) trong nhật ký điểm quét

seq_no tăng liên tục theo từng điểm quét, không đặt lại mỗi ngày; nên gộp mọi ngày của một điểm quét.

- SP01: có 7 số, từ 1 đến 7 (các ngày trong txn_id: 20261109, 20261115)
- SP02: có 4 số, từ 1 đến 4 (các ngày trong txn_id: 20261109, 20261115)

Không có khoảng trống.

Lưu ý: nhật ký chỉ chứa giao dịch còn trong file queue; khoảng trống có thể do file bị xóa hoặc chạy trên máy khác.
