# SV1 – Thiết kế mạng và mô hình dữ liệu · Đề tài 22

**Đề tài:** Thiết kế hạ tầng CNTT cho hệ thống quản lý kho hàng thông minh – học phần Nhập môn Công nghệ nền tảng (RIPT1304)
**Người thực hiện:** ................................ · MSSV: .................... · Lớp/Nhóm: ....................
**Phiên bản bộ thiết kế:** v1.0 (chốt tại Cổng 1) · cập nhật 27/10/2026

## 1. Sản phẩm theo từng thẻ việc

| Thẻ | Việc | Minh chứng | Trạng thái |
|---|---|---|---|
| 1 | Sơ đồ quan hệ 5 bảng + từ điển dữ liệu | `02_MoHinhDuLieu.png`, `06_TuDienDuLieu.md`, `du_lieu/TuDienDuLieu.csv`, `du_lieu/schema.sql` | Xong – 38/38 trường khớp schema |
| 2 | Giao ước API + ma trận quyền | `05_GiaoUocAPI.md` (ghi GD, đọc tồn, đọc lịch sử, 14 mã lỗi, ma trận 13 chức năng × 4 vai trò) | Xong |
| 3 | Bàn giao bộ thiết kế, chủ trì Cổng 1 | `cong_phoi_hop/Cong1_BienBanBanGiao.docx` | Mẫu xong – **chờ họp và ký** |
| 4 | Sơ đồ mạng 3 VLAN, bảng IP, quy tắc truy cập; phần chạy thật / chỉ trên sơ đồ | `01_SoDoHaTang.png`, `cau_hinh/BangDiaChiIP.csv`, `cau_hinh/QuyTacTruyCap.csv`, `cau_hinh/*.txt`, `cau_hinh/HuongDan_PacketTracer.md` | Xong – **còn file .pkt** |
| 5 | Sơ đồ luồng quét → gửi → kiểm tra → lưu → cập nhật tồn → phản hồi (nhánh lỗi, nhánh trùng) + 03_ThietKeDuLieu | `04_SoDoLuongDuLieu.png`, `03_ThietKeDuLieu.docx` / `.pdf` (19 trang) | Xong |
| 6 | Đối chiếu tên trường SV2/SV3 với từ điển, nhật ký thay đổi | `doi_chieu/doi_chieu_ten_truong.py`, `doi_chieu/BangDoiChieuTenTruong.md`, `doi_chieu/NhatKyThayDoi.md` | Công cụ xong – **chạy lại khi có mã SV2/SV3** |
| SV1-08 | Dự Cổng 2: quan sát gửi → lưu → đọc lại | `cong_phoi_hop/kiem_tra_cong2.py`, `cong_phoi_hop/Cong2_BienBanQuanSat.docx`, `cong_phoi_hop/ket_qua/` | Chạy thử 10/10 với máy chủ giả lập – **chạy lại trên máy chủ SV3 ngày 4/11** |
| SV1-09 | Mô hình ước lượng 2 → 4 điểm quét (có công thức) | `07_UocLuong_MoRong.xlsx`, `uoc_luong/tao_bang_uoc_luong.ps1` | Xong – 0 ô lỗi công thức |
| SV1-10 | Giao mô hình ước lượng cho SV4 | `uoc_luong/BanGiao_SV4.md` | Xong – **chờ SV4 ký nhận** |
| SV1-11 | Nâng cao: script tải 2 rồi 4 tiến trình | `tai_thu/tai_thu.py`, `tai_thu/tham_so_tai.json`, `tai_thu/ket_qua/`, `du_lieu/seed_mo_rong_4_diem.sql` | Xong – chạy thử với máy chủ giả lập |
| SV1-12 | Khung hồ sơ chung | `ho_so_chung/HoSoChung_DeTai22_Khung.docx` (mục lục, thuật ngữ, danh mục minh chứng, theo dõi thu bài, phiếu đóng góp) | Xong – **chờ thu bài SV2–SV4** |
| SV1-13 | Hoàn thiện hồ sơ chung | `ho_so_chung/ra_soat_ho_so.py`, `ho_so_chung/RaSoat_HoanThien.md`, `ho_so_chung/RaSoat_BanKhung_*.md` | Công cụ + checklist xong – **chốt cùng SV4 ngày 13/11** |

Phần việc gốc CV01 (phiếu SV1): `01_SoDoHaTang.png`, `02_MoHinhDuLieu.png`, `03_ThietKeDuLieu.docx/.pdf` và các file cấu hình ở trên.

## 2. Bằng chứng kỹ thuật đã chạy

| Bằng chứng | Kết quả | File |
|---|---|---|
| Kiểm chứng mô hình dữ liệu và quy tắc R1–R10 | **11/11 tình huống đạt** (trùng, tồn âm, sai mã hàng, sai số lượng, tài khoản chỉ xem, sửa/xóa lịch sử, 2 điểm quét ghi song song, đối chiếu) | `du_lieu/ketqua_kiemtra.txt` |
| Đo dung lượng | **301 byte/giao dịch** (100.000 giao dịch) | `du_lieu/ketqua_do_dung_luong.txt` |
| Từ điển khớp schema | 38/38 trường | chạy `du_lieu/xuat_tu_dien.py` |
| Cổng 2 (máy chủ giả lập) | 10/10 bước đạt | `cong_phoi_hop/ket_qua/THU_GIA_LAP_*.md` |
| Thử tải nhịp 3 s (máy chủ giả lập) | 2 điểm 0,6 GD/s · 4 điểm 1,27 GD/s · p95 ≤ 40 ms · 0 lỗi lạ · đối chiếu khớp | `tai_thu/ket_qua/*_THU_GIA_LAP_nhip3s/` |
| Thử tải gắng sức (máy chủ giả lập) | 2 điểm 76,7 GD/s · 4 điểm 99,8 GD/s · gửi trùng 100% nhận 409 · đối chiếu khớp | `tai_thu/ket_qua/*_THU_GIA_LAP_gangsuc/` |
| Bảng ước lượng | 4 điểm: 1,33 GD/s (2,7% năng lực), 21,8 kbit/s, 3,47 GB/năm, sao lưu 38,1 GB (3,8% NAS); cảnh báo txn_id 96% | `07_UocLuong_MoRong.xlsx` |

Kết quả “THU_GIA_LAP” chỉ chứng minh script hoạt động, **không** phải số đo hệ thống thật. Số đo thật do SV4 chạy trên máy chủ SV3.

## 3. Phiên bản phần mềm đã dùng

| Phần mềm | Phiên bản | Dùng cho |
|---|---|---|
| Python | 3.13.2 (chạy được từ 3.8; chỉ thư viện chuẩn) | Mọi script `.py` |
| SQLite | 3.45.3 (đi kèm Python) | CSDL |
| Cisco Packet Tracer | 8.2 trở lên | Mô hình mạng |
| Microsoft Edge | bản cài sẵn trên Windows 11 | Xuất sơ đồ PNG |
| Microsoft Word / Excel | 2016 trở lên (Office 16) | Mở `.docx`, tạo lại `.xlsx` |
| Node.js + thư viện `docx` | 22.17.1 · docx 9.5.1 | Tạo lại các file `.docx` |

## 4. Cách dựng lại và chạy kiểm tra

Chạy từ thư mục `SV1_ThietKeMang_DuLieu`:

```bash
# Kiểm chứng mô hình dữ liệu (tạo kho_kiemtra.db tạm, ghi ketqua_kiemtra.txt)
python du_lieu/kiem_tra_thiet_ke.py
# Đo byte/giao dịch
python du_lieu/do_dung_luong.py 100000
# Kiểm tra từ điển khớp schema và xuất 06_TuDienDuLieu.md
python du_lieu/xuat_tu_dien.py

# Máy chủ giả lập theo giao ước API (khi chưa có máy chủ SV3)
python cong_cu_thu/may_chu_gia_lap.py --moi --port 8080
# Cổng 2: gửi -> lưu -> đọc lại (đổi --url sang máy chủ SV3 khi kiểm tra thật)
python cong_phoi_hop/kiem_tra_cong2.py --url http://127.0.0.1:8080
# Thử tải 2 rồi 4 điểm quét (CSDL phải sạch: khởi động lại máy chủ với --moi)
python tai_thu/tai_thu.py --url http://127.0.0.1:8080 --thoi-gian 60
python tai_thu/tai_thu.py --url http://127.0.0.1:8080 --thoi-gian 20 --gang-suc

# Đối chiếu tên trường khi có mã SV2/SV3
python doi_chieu/doi_chieu_ten_truong.py --sv2 <thư mục SV2> --sv3 <thư mục SV3> --db <kho.db của SV3>
# Rà soát hồ sơ chung trước khi chốt
python ho_so_chung/ra_soat_ho_so.py <hồ sơ>.docx --thu-muc <thư mục nộp>
```

```powershell
# Xuất lại sơ đồ PNG từ mã nguồn SVG/HTML
powershell -ExecutionPolicy Bypass -File nguon_so_do/render.ps1
# Tạo lại bảng ước lượng Excel
powershell -ExecutionPolicy Bypass -File uoc_luong/tao_bang_uoc_luong.ps1
# Tạo lại các file Word (cần: npm install docx@9.5.1 trong thư mục nguon_tai_lieu)
node nguon_tai_lieu/build_03.js
```

Nếu cổng 8080 đã bị chương trình khác dùng, đổi sang cổng khác bằng `--port` / `--url` (khi chạy thử trên máy SV1 đã dùng 18080).

Dựng mô hình Packet Tracer: làm theo `cau_hinh/HuongDan_PacketTracer.md` (đặt thiết bị, nối dây, dán cấu hình, 13 phép kiểm tra N1–N13).

## 5. Việc SV1 còn phải tự làm

- [ ] Dựng `KhoHang_DeTai22.pkt` trong Packet Tracer, chụp ảnh N1–N13 có đồng hồ hệ thống
- [ ] Điền họ tên, MSSV, lớp, nhóm vào README này, `03_ThietKeDuLieu.docx`, các biên bản và khung hồ sơ
- [ ] Chủ trì họp Cổng 1, lấy chữ ký (`Cong1_BienBanBanGiao.docx`)
- [ ] Ngày 4/11: chạy `kiem_tra_cong2.py` trên máy chủ SV3, điền `Cong2_BienBanQuanSat.docx`
- [ ] Khi có mã SV2/SV3: chạy `doi_chieu_ten_truong.py`, sửa lệch, ghi `NhatKyThayDoi.md`
- [ ] Ngày 7/11: giao SV4 theo `uoc_luong/BanGiao_SV4.md`, lấy xác nhận
- [ ] Ngày 11–13/11: thu bài, ghép hồ sơ, chạy `ra_soat_ho_so.py` đến 0 vấn đề, chốt cùng SV4
- [ ] Bổ sung mục “Sử dụng AI” (03 mục 13.3, khung hồ sơ): phần nào tự chỉnh sửa, lỗi nào tự phát hiện

## 6. Cấu trúc thư mục

```
SV1_ThietKeMang_DuLieu/
├── README_SV1.md
├── 01_SoDoHaTang.png            02_MoHinhDuLieu.png         04_SoDoLuongDuLieu.png
├── 03_ThietKeDuLieu.docx/.pdf   05_GiaoUocAPI.md            06_TuDienDuLieu.md
├── 07_UocLuong_MoRong.xlsx
├── cau_hinh/        router, switch, Wi-Fi, bảng IP, quy tắc truy cập, hướng dẫn Packet Tracer
├── du_lieu/         schema, dữ liệu mẫu (2 và 4 điểm), từ điển CSV, script kiểm chứng + kết quả
├── cong_phoi_hop/   biên bản Cổng 1, Cổng 2, script kiểm tra Cổng 2, kết quả
├── doi_chieu/       script đối chiếu tên trường, bảng đối chiếu, nhật ký thay đổi
├── uoc_luong/       script tạo bảng Excel, phiếu bàn giao SV4
├── tai_thu/         script tải, tham số, kết quả đo gốc (raw.csv)
├── cong_cu_thu/     máy chủ giả lập theo giao ước API (công cụ thử, không thay SV3)
├── ho_so_chung/     khung hồ sơ chung, script rà soát, checklist hoàn thiện
├── nguon_so_do/     mã nguồn SVG/HTML các sơ đồ + render.ps1
└── nguon_tai_lieu/  script Node.js tạo các file Word
```

## 7. Nguồn tham khảo và sử dụng AI

Cấu hình Cisco IOS theo tài liệu Cisco Networking Academy; lược đồ theo tài liệu SQLite; mã chỉ dùng thư viện chuẩn Python. Tài liệu, cấu hình mẫu, script và sơ đồ được soạn với sự hỗ trợ của trợ lý AI Claude (Anthropic); SV1 đã chạy lại toàn bộ script (kết quả ở mục 2) và chịu trách nhiệm giải thích, chỉnh sửa phần đã nộp.
