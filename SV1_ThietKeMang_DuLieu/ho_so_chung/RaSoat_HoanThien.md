# Checklist hoàn thiện hồ sơ chung – Đề tài 22 (SV1-13, hạn 13/11/2026)

SV1 và SV4 cùng thực hiện. Hồ sơ chỉ được chốt khi tất cả mục dưới đây đã đánh dấu ☑.

## 1. Thu đủ bài (theo bảng “Theo dõi thu bài” trong khung hồ sơ)

- [ ] SV2: mã client, README chạy, ảnh 2 điểm quét, mục 4.2, phiếu đóng góp
- [ ] SV3: mã server, CSDL, sao lưu/khôi phục, mục 4.3, phiếu đóng góp
- [ ] SV4: bảng kiểm thử KT1–KT3 có bằng chứng thời gian, kết quả `tai_thu.py` (dữ liệu đo gốc), mục 4.4, chương 5–6, phiếu đóng góp
- [ ] SV1: file `.pkt` + ảnh N1–N13; biên bản Cổng 1, Cổng 2 đã ký
- [ ] Chạy `doi_chieu/doi_chieu_ten_truong.py --sv2 … --sv3 … --db …` trên mã cuối cùng → không còn LỆCH

## 2. Rà tự động

```
python ho_so_chung/ra_soat_ho_so.py <đường_dẫn_hồ_sơ_đã_ghép>.docx --thu-muc <thư_mục_nộp_của_nhóm>
```

- [ ] 0 “Ô hướng dẫn chưa xóa”
- [ ] 0 “Thuật ngữ không thống nhất” (trong hồ sơ và trong file minh chứng)
- [ ] 0 “Thiếu số liệu then chốt”, 0 “Thiếu chương bắt buộc”
- [ ] 0 cảnh báo “Bảng kiểm thử chưa điền kết quả”
- [ ] Lưu file `RaSoat_<thời điểm>.md` cuối cùng làm minh chứng

## 3. Rà số liệu bằng mắt (SV1 + SV4)

Mỗi số dưới đây phải giống nhau ở mọi chỗ xuất hiện. Nếu SV4 đo được số khác thì cập nhật ở **mọi** nơi và ghi vào `doi_chieu/NhatKyThayDoi.md`.

| Số liệu chuẩn | Nguồn gốc | Xuất hiện ở | Khớp |
|---|---|---|:-:|
| 3 VLAN: 10 máy chủ / 20 văn phòng / 30 điểm quét | `cau_hinh/*.txt` | Sơ đồ 01, 03 mục 4, hồ sơ chương 3 | ☐ |
| SRV-KHO 192.168.10.10, API cổng 8080 | `BangDiaChiIP.csv` | 01, 03, 05, hồ sơ, README | ☐ |
| 6 bảng, 38 trường | `TuDienDuLieu.csv` | 02, 03, 06, hồ sơ | ☐ |
| 14 mã lỗi, 4 vai trò | `05_GiaoUocAPI.md` | 03, hồ sơ 3.4, mã SV2/SV3 | ☐ |
| 301 byte/giao dịch | `ketqua_do_dung_luong.txt` | 03 mục 10, xlsx G07, hồ sơ 6.1 | ☐ |
| Tải đỉnh 0,67 → 1,33 GD/s | xlsx sheet UocLuong | 03 mục 12, BanGiao_SV4, hồ sơ 6.1 | ☐ |
| Băng thông 10,9 → 21,8 kbit/s | xlsx | BanGiao_SV4, hồ sơ 6.1 | ☐ |
| CSDL 1,73 → 3,47 GB/năm (cận trên); sao lưu 19,1 → 38,1 GB | xlsx | 03, BanGiao_SV4, hồ sơ 6.1 | ☐ |
| 9.600 / 9.999 giao dịch/ngày/điểm (96%) | xlsx | 03 mục 8.1, hồ sơ 6.3 | ☐ |
| KT1: tồn SP001 100 → 120 | `seed_data.sql` | Biên bản Cổng 1, hồ sơ chương 5 | ☐ |
| Số đo thật của SV4 (thông lượng, p95) | `tai_thu/ket_qua/…/tong_hop.md` | xlsx cột L–M, hồ sơ 6.1 | ☐ |

## 4. Rà hình thức

- [ ] Nội dung chính 12–18 trang (không tính bìa, mục lục, phụ lục cấu hình)
- [ ] Mục lục đã cập nhật (chuột phải → Update Field → Update entire table)
- [ ] Hình, bảng đánh số và có chú thích; sơ đồ đọc được khi in
- [ ] Xóa trang “Hướng dẫn dùng khung hồ sơ”
- [ ] Điền đủ họ tên, MSSV, lớp, nhóm ở bìa và README

## 5. Đối chiếu với “Hồ sơ nộp chung cho mọi đề”

- [ ] Báo cáo có: yêu cầu, giả định, kiến trúc, triển khai, kiểm thử, đánh giá, tài liệu tham khảo
- [ ] Sơ đồ hệ thống; bảng tài nguyên / IP / quyền
- [ ] File `.pkt`, cấu hình, script, mã nguồn
- [ ] README: phiên bản phần mềm, cách dựng lại, cách chạy kiểm thử, họ tên + MSSV
- [ ] Bảng kiểm thử: đầu vào, thao tác, mong đợi, thực tế, đạt/chưa đạt, bằng chứng có dấu thời gian
- [ ] Dữ liệu đo gốc (raw.csv) của phần đánh giá hiệu năng
- [ ] Video demo 5–7 phút
- [ ] Phiếu đóng góp cá nhân của **mọi** thành viên: nhiệm vụ, file tạo ra, bằng chứng, lỗi đã xử lý
- [ ] Nêu nguồn mã/cấu hình tham khảo và cách sử dụng AI

## 6. Chốt

- [ ] Xuất PDF; đặt tên `DeTai22_Nhom<số>_HoSoChung.pdf`
- [ ] Cả nhóm xem bản PDF cuối và xác nhận
- [ ] Nộp lên Drive giảng viên cung cấp

| Người rà | Ngày | Kết quả `ra_soat_ho_so.py` | Xác nhận |
|---|---|---|---|
| SV1 | | | |
| SV4 | | | |
