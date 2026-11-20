# Phiếu bàn giao mô hình ước lượng và script tải cho SV4 – Đề tài 22

| | |
|---|---|
| Bên giao | SV1 – ........................ (MSSV ..........) |
| Bên nhận | SV4 – ........................ (MSSV ..........) |
| Ngày bàn giao | ..../11/2026 (hạn thẻ SV1-10: 7/11/2026) |
| Mục đích | SV4 dùng để kiểm thử tải và đánh giá khả năng mở rộng 2 → 4 điểm quét (yêu cầu bắt buộc 4) |

## 1. Danh sách bàn giao

| # | File | Nội dung | Đã nhận |
|---|---|---|:-:|
| 1 | `07_UocLuong_MoRong.xlsx` | Bảng ước lượng có công thức: sheet GiaDinh (20 giả định), UocLuong (17 chỉ tiêu, 2 và 4 điểm), KetLuan (nhận định tự cập nhật), ThuTai_GiaLap | ☐ |
| 2 | `uoc_luong/tao_bang_uoc_luong.ps1` | Script tạo lại file Excel (cần Microsoft Excel) | ☐ |
| 3 | `tai_thu/tai_thu.py` | Script tải: chạy 2 rồi 4 tiến trình khách, ghi dữ liệu đo gốc | ☐ |
| 4 | `tai_thu/tham_so_tai.json` | Tham số tải (địa chỉ, thời gian, nhịp quét, tỉ lệ gửi trùng, mã hàng) | ☐ |
| 5 | `du_lieu/seed_mo_rong_4_diem.sql` | Khai báo SP03, SP04 và tài khoản nv03, nv04 (bắt buộc cho kịch bản 4 điểm) | ☐ |
| 6 | `tai_thu/ket_qua/*THU_GIA_LAP*` | Kết quả chạy thử với máy chủ giả lập (mẫu định dạng kết quả, **không** phải số đo thật) | ☐ |
| 7 | `cong_cu_thu/may_chu_gia_lap.py` | Máy chủ giả lập theo giao ước API để tập chạy script khi chưa có máy chủ SV3 | ☐ |

## 2. Kết quả ước lượng chính (chưa đo thực tế)

Theo giả định G2: 1 giao dịch / 3 giây / điểm quét lúc cao điểm, 8 giờ/ngày, 300 ngày/năm; 301 byte CSDL/giao dịch (đo thật).

| Chỉ tiêu | 2 điểm | 4 điểm | Giới hạn | Đánh giá |
|---|---:|---:|---:|---|
| Tải đỉnh (GD/s) | 0,67 | 1,33 | 50 (giả định G10) | Đủ – 2,7% |
| Băng thông đỉnh (kbit/s) | 10,9 | 21,8 | 100.000 | Đủ – 0,02% |
| CSDL tăng mỗi ngày, đỉnh (MB) | 5,78 | 11,56 | — | — |
| CSDL sau 1 năm, cận trên (GB) | 1,73 | 3,47 | — | — |
| Sao lưu 11 bản, cận trên (GB) | 19,1 | 38,1 | 1.000 (NAS) | Đủ – 3,8% |
| Cổng switch có dây / máy Wi-Fi | 1 / 1 | 2 / 2 | 7 / 25 | Đủ |
| Giao dịch/ngày/điểm (đỉnh) | 9.600 | 9.600 | 9.999 (txn_id) | **Cảnh báo 96%** – chạy 2 ca phải tăng lên 5 chữ số |

## 3. SV4 cần làm

1. **Chuẩn bị máy chủ SV3 với CSDL sạch:** `schema.sql` → `seed_data.sql` → `seed_mo_rong_4_diem.sql`. Script dùng `txn_id` theo ngày; chạy lại trong cùng ngày trên cùng CSDL sẽ báo 409 ở giao dịch mới.
2. **Sửa `url` trong `tham_so_tai.json`** (hoặc dùng `--url`) trỏ tới máy chủ SV3.
3. **Lần đo 1 – nhịp thật (theo giả định G2):** `python tai_thu.py --thoi-gian 120 --nhan nhip3s`
   → so thông lượng, độ trễ với dòng “Tải đỉnh” của bảng ước lượng.
4. **Lần đo 2 – gắng sức (năng lực tối đa):** khôi phục CSDL sạch, rồi `python tai_thu.py --thoi-gian 30 --gang-suc --nhan gangsuc`
   → kết quả dùng để thay giả định G10 (năng lực máy chủ) bằng số đo.
5. **Đo băng thông** (tùy chọn): bắt gói bằng Wireshark một giao dịch để thay giả định G08 (byte mạng/giao dịch).
6. **Điền sheet `UocLuong`, cột L–M (nền vàng):**

   | Dòng (STT) | Lấy từ | Cột |
   |---|---|---|
   | 2 – Tải đỉnh | `tong_hop.md` lần đo 1: “Thông lượng giao dịch mới (GD/s)” | L (2 điểm), M (4 điểm) |
   | 5 – GD/ngày toàn kho | Thông lượng lần đo 1 × 3600 × 8 | L, M |
   | 8 – CSDL tăng mỗi ngày | (kích thước kho.db sau − trước) ÷ số GD × GD/ngày | L, M |
   | 12 – Băng thông đỉnh | Wireshark hoặc thông lượng × byte đo được | L, M |
   | 17 – Độ trễ p95 | `tong_hop.md` lần đo 1: “Độ trễ p95 (ms)” | L, M |

   Cột N tự tính sai lệch ước lượng – đo. Sai lệch lớn (> 30%) phải giải thích trong báo cáo.
7. **Nộp dữ liệu đo gốc:** toàn bộ thư mục `tai_thu/ket_qua/<thời điểm>_<nhãn>/` (raw.csv, tong_hop.json, tong_hop.md).

## 4. Tiêu chí đạt khi kiểm thử tải

| Tiêu chí | Ngưỡng |
|---|---|
| Lỗi không mong đợi (“Lỗi khác”) | 0 |
| Gửi trùng nhận 409 | 100% số lần gửi trùng |
| Đọc lại mẫu giao dịch 201 | 100% |
| Đối chiếu tồn sau tải (`all_match`) | True |
| Độ trễ p95 ở nhịp thật, 4 điểm | ≤ 500 ms |

## 5. Xác nhận

| Bên | Họ tên | Chữ ký / xác nhận | Ngày |
|---|---|---|---|
| SV1 (giao) | | | |
| SV4 (nhận) | | | |

Ghi chú của SV4 khi nhận (câu hỏi, đề nghị sửa giả định): ..........................................................
