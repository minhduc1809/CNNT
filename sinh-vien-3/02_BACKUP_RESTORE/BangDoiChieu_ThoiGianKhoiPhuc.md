# Bảng đối chiếu và thời gian khôi phục (SV3 – CV03)

**Quy tắc:** số liệu dưới đây lấy từ lần chạy thật của `03_khoi_phuc_va_doi_chieu.ps1` ngày 14/11/2026
(file kết quả: `restore_test_20261114_202742.txt`). Các ô mã minh chứng (MC) điền sau khi lưu ảnh/file vào hồ sơ.

## 1. Bản sao lưu dùng để khôi phục

| Mục | Giá trị |
|---|---|
| Tên file | `smart_warehouse_20261114_202746.sql` |
| Nguồn tạo (trong `backup.log`) | `ThuCong` – tạo bằng tùy chọn `-SaoLuuMoiTruoc` ngay trước khi khôi phục, để CSDL gốc và bản sao lưu cùng thời điểm |
| Thời điểm tạo | 2026-11-14 20:27:46 |
| Kích thước | 22527 bytes |
| SHA256 | `7122CFE0243318C40E3D54868DD7D444EDAA79AECC7247EE99E673E40ABCE98B` |
| Phiên bản MySQL | 9.3.0 |
| Môi trường | Máy thật Windows 10 (chưa phải máy ảo) |

## 2. Bằng chứng sao lưu theo lịch

| Mục | Giá trị / mã minh chứng |
|---|---|
| Tên tác vụ, lịch chạy | `WH-SaoLuu-CSDL`, Windows Task Scheduler, chạy bằng tài khoản SYSTEM; giai đoạn thử dùng chu kỳ 5 phút (MC....) |
| Dòng `Nguon=Lich` + `KetQua=OK` trong `backup.log` | Có. Lần do trigger tự kích hoạt: 2026-11-14 20:27:21, file `smart_warehouse_20261114_202721.sql` (MC....) |
| Ghi chú | Lần chạy 20:26:23 do lệnh chạy thử `-ChayNgay` kích hoạt (không tính là lịch tự động). Bốn dòng `KetQua=LOI` lúc 20:19–20:24 do sai mật khẩu tài khoản `wh_dump`, đã sửa và giữ nguyên trong nhật ký |
| Lịch chính thức | Tác vụ `WH-SaoLuu-CSDL`, Windows Task Scheduler, chu kỳ **mỗi 2 giờ** (tham số `-ChuKyPhut 120`), đăng ký lúc 15:04 ngày 16/11/2026, chạy bằng tài khoản SYSTEM. Lần chạy tự động đầu tiên: 2026-11-16 15:04:15, file `smart_warehouse_20261116_150415.sql` (xem `backup.log`). |

## 3. Đối chiếu CSDL gốc và CSDL khôi phục

| Hạng mục | CSDL gốc | CSDL khôi phục | Kết luận |
|---|---|---|---|
| Số bản ghi Products | 100 | 100 | Khớp |
| Số bản ghi Inventory | 100 | 100 | Khớp |
| Số bản ghi Users | 5 | 5 | Khớp |
| Số bản ghi ScanPoints | 2 | 2 | Khớp |
| Số bản ghi warehouse_transactions | 37 | 37 | Khớp |
| Tổng tồn (SUM quantity) | 2866 | 2866 | Khớp |
| CHECKSUM Products | 1262308272 | 1262308272 | Khớp |
| CHECKSUM Inventory | 2614722626 | 2614722626 | Khớp |
| CHECKSUM Users | 2370493006 | 2370493006 | Khớp |
| CHECKSUM ScanPoints | 286800786 | 286800786 | Khớp |
| CHECKSUM warehouse_transactions | 2037940467 | 2037940467 | Khớp |
| Số stored procedure | 1 | 1 | Khớp |

**Chênh lệch:** không có.

## 4. Thời gian khôi phục so với RTO

| Mục | Giá trị |
|---|---|
| Thời gian khôi phục đo được (tạo CSDL + nạp file) | 0,6 giây |
| Thời gian cả quy trình (gồm đối chiếu) | 1,7 giây |
| RTO giả định | 1800 giây (30 phút) |
| Kết luận | Trong RTO |
| Điều kiện đo | Máy thật Windows 10, MySQL 9.3.0, dữ liệu mẫu 100 mặt hàng và 37 giao dịch, file sao lưu 22527 bytes; số lần đo: 1 (........ ghi thêm nếu đo lại) |

Lưu ý khi viết báo cáo: đây là số đo trên dữ liệu mẫu rất nhỏ nên thời gian ngắn; chưa phản ánh dữ liệu thật của kho.
Hai bản dump tạo ở các thời điểm khác nhau có SHA256 khác nhau dù dữ liệu như nhau, vì mysqldump ghi dòng thời điểm hoàn tất (`Dump completed on ...`) vào cuối file.
