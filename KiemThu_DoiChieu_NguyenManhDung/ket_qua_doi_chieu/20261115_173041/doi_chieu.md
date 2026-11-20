# Đối chiếu điểm quét với máy chủ – 15/11/2026 17:30:41

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
| SP01 | khác (cần xem từng dòng) | 4 |
| SP01 | thử tải (tai_thu_sv4, số thứ tự từ 1001) | 78 |
| SP02 | khác (cần xem từng dòng) | 3 |
| SP02 | thử tải (tai_thu_sv4, số thứ tự từ 1001) | 71 |

Chi tiết từng dòng: chi_co_tren_may_chu.csv

## C. Tồn kho: tồn gốc + nhập − xuất so với tồn thực tế

Khớp ở cả 100 mặt hàng: tồn thực tế = tồn gốc (file seed 02) + tổng nhập − tổng xuất của mọi giao dịch trong bảng.

## D. Khoảng trống số thứ tự (seq_no) trong nhật ký điểm quét

- SP01, ngày 20261115: thiếu số [1, 2, 3, 4]
- SP02, ngày 20261115: thiếu số [1, 2, 3]

Lưu ý: nhật ký chỉ chứa giao dịch còn trong file queue; khoảng trống có thể do file bị xóa hoặc chạy trên máy khác.
