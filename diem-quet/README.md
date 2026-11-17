# HƯỚNG DẪN SỬ DỤNG PHÂN HỆ ĐIỂM QUÉT – SINH VIÊN 2 (`diem-quet/`)
**Đề tài 22:** Xây dựng cơ sở hạ tầng cho hệ thống quản lý kho hàng thông minh  
**Phụ trách:** Sinh viên 2 – Thiết lập và lập trình 2 điểm quét (`SP01`, `SP02`), xử lý mất mạng, hàng đợi cục bộ và chuẩn bị kịch bản demo.

---

## 1. Cấu trúc thư mục `diem-quet/`

```text
diem-quet/
├── scanner.py                      # Chương trình máy khách điểm quét chính (menu tương tác 6 chức năng)
├── config_sp01.json                # Cấu hình Điểm quét 1 - Cửa Nhập (SP01, IP: 192.168.20.11, user: nv01)
├── config_sp02.json                # Cấu hình Điểm quét 2 - Cửa Xuất (SP02, IP: 192.168.20.12, user: nv02/thukho_demo)
├── config_scan01.json              # Cấu hình tương thích mã SCAN01 (nhanvien_demo)
├── config_scan02.json              # Cấu hình tương thích mã SCAN02 (thukho_demo)
├── thu_mat_mang_va_doi_chieu.py    # Script tự động chạy trọn bộ CV02 + CV03 và xuất báo cáo số đo
├── thu_dong_thoi_xuat.py           # Script nâng cao (+2đ): 2 điểm quét đồng thời xuất cùng 1 mặt hàng
├── chay_thu_2_may_wsl.py           # Script dựng IP thật (192.168.20.11/12 -> 192.168.10.10) trên máy ảo Ubuntu WSL2
├── BaoCao_SoDo_MatMang_SV2.md      # Báo cáo số đo độ trễ, retry và bảng đối chiếu seq_no với máy chủ (CV03)
├── KichBan_Demo_SV2.md             # Kịch bản trình diễn bảo vệ (5-7 phút) & trả lời 5 câu hỏi vấn đáp SV2
├── requirements.txt                # Thư viện cần thiết (requests)
├── logs/                           # Thư mục lưu nhật ký hoạt động của các điểm quét
│   ├── log_SP01.log
│   ├── log_SP02.log
│   ├── ketqua_thu_dong_thoi.txt
│   └── ketqua_chay_2_may_wsl.txt
├── queue/                          # Thư mục lưu hàng đợi trên đĩa và bộ đếm seq_no (fsync chống tắt đột ngột)
│   ├── queue_SP01.jsonl
│   ├── queue_SP02.jsonl
│   ├── seq_SP01.txt
│   └── seq_SP02.txt
└── evidence/                       # Trọn bộ 7 ảnh chụp màn hình minh chứng (MC_SV2_01 -> MC_SV2_07)
```

---

## 2. Cài đặt môi trường

Yêu cầu **Python 3.10+** đã cài đặt thư viện `requests` (và `Flask`, `pymysql`, `python-dotenv` nếu chạy kèm máy chủ API của SV3 trên cùng máy):

```powershell
pip install -r diem-quet/requirements.txt
pip install -r sinh-vien-3/04_DICH_VU_API/requirements.txt
```

---

## 3. Cách 1: Chạy tương tác từng điểm quét bằng Menu (`scanner.py`)

### Bước 1: Bật máy chủ API của SV3 (Cổng `5000`)
Mở **Terminal 1** tại thư mục gốc `E:\CNNT`:
```powershell
python sinh-vien-3/04_DICH_VU_API/app.py
```
*(Lưu ý: `app.py` đã tích hợp cơ chế tự động chuyển sang bộ nhớ đệm in-memory nếu máy chưa bật MySQL Server ở cổng `3306`, nên có thể chạy ngay trên mọi máy tính).*

### Bước 2: Bật Điểm quét 1 (`SP01` – Cửa Nhập) và Điểm quét 2 (`SP02` – Cửa Xuất)
- Mở **Terminal 2** (chạy `SP01`):
  ```powershell
  cd diem-quet
  python scanner.py config_sp01.json
  ```
- Mở **Terminal 3** (chạy `SP02`):
  ```powershell
  cd diem-quet
  python scanner.py config_sp02.json
  ```

### Bước 3: Sử dụng 6 chức năng trên Menu điểm quét
Khi khởi động, nhấn `Enter` để dùng tài khoản mặc định (mật khẩu mặc định: `Kho@2026`), sau đó chọn các phím `0–6`:
- **Phím `1` – Quét và gửi giao dịch mới (`NHAP` / `XUAT`):**
  - Nhập mã hàng (`SP001` .. `SP100`), loại giao dịch (`NHAP` hoặc `XUAT`), số lượng (`1 - 10000`).
  - Tự động chặn đầu vào sai tại client (`INVALID_INPUT`), cấp phát `seq_no` tăng dần, sinh mã `txn_id = SPxx-yyyymmdd-nnnn`, lưu vào `queue/queue_SPxx.jsonl` trước khi gửi mạng, và tự động gọi `GET /api/transactions/<txn_id>` đọc lại bản ghi sau khi máy chủ trả `201 Created`.
- **Phím `2` – Đồng bộ lại hàng đợi chưa xác nhận (`CV03`):**
  - Đẩy toàn bộ các giao dịch đang ở trạng thái `CHO_XAC_NHAN` trong `queue/queue_SPxx.jsonl` lên máy chủ sau khi có mạng lại (giữ nguyên `txn_id` gốc).
- **Phím `3` – Gửi lặp lại một `txn_id` cũ (Test ca `KT2` – Chống trùng):**
  - Nhập lại một `txn_id` đã lưu trước đó để kiểm chứng máy chủ trả về `409 DUPLICATE_TXN` và không cộng/trừ tồn kho hai lần.
- **Phím `4` – Kiểm tra kết nối máy chủ & Tra cứu tồn kho (`CV01`):**
  - Kiểm tra độ trễ kết nối tới máy chủ và xem số lượng tồn hiện tại của mặt hàng (mặc định `SP001`).
- **Phím `5` – Xem bảng số đo độ trễ, tỉ lệ thành công & Đối chiếu `seq_no` (`CV03`):**
  - In bảng thống kê tổng số giao dịch, số lần gửi lại (Retry), độ trễ `Min / Avg / Max (ms)` và đối chiếu từng `seq_no` với CSDL máy chủ.
- **Phím `6` – Đổi tài khoản đăng nhập (Test phân quyền RBAC):**
  - Chuyển nhanh giữa các tài khoản:
    - `nv01` / `nhanvien_demo` (**Nhân viên**): Chỉ được `NHAP`, bị chặn `403` khi `XUAT`.
    - `thukho_demo` / `thukho01` (**Thủ kho**): Được cả `NHAP` và `XUAT`.
    - `viewer_demo` / `xem01` (**Chỉ xem**): Bị chặn `403 FORBIDDEN` khi gửi bất kỳ giao dịch nào.

---

## 4. Cách 2: Chạy các kịch bản tự động 1 lệnh (Không cần gõ tay)

Bạn không cần bật sẵn máy chủ trước khi chạy 3 lệnh dưới đây (các script sẽ tự động khởi chạy máy chủ nếu cổng `5000` chưa bật):

### 4.1. Kịch bản tự động kiểm thử toàn diện `CV02` & `CV03`
```powershell
python diem-quet/thu_mat_mang_va_doi_chieu.py
```
- **Thực hiện:** Tự động chạy 5 bước (Chặn đầu vào sai -> Gửi hợp lệ `SP01` & `SP02` + đọc lại -> Kiểm thử `409`, `403`, `404`, `INSUFFICIENT_STOCK` -> Giả lập đứt mạng & tắt đột ngột -> Khôi phục mạng, đồng bộ hàng đợi & đối chiếu `seq_no`).
- **Kết quả sinh ra:** Cập nhật `logs/log_SP01.log`, `logs/log_SP02.log`, `queue/queue_SP01.jsonl`, `queue/queue_SP02.jsonl` và xuất báo cáo [`BaoCao_SoDo_MatMang_SV2.md`](file:///E:/CNNT/diem-quet/BaoCao_SoDo_MatMang_SV2.md).

### 4.2. Kịch bản xuất đồng thời từ 2 điểm quét (Tầng nâng cao +2 điểm)
```powershell
python diem-quet/thu_dong_thoi_xuat.py
```
- **Thực hiện:** Kích hoạt 2 luồng `SP01` và `SP02` cùng lúc yêu cầu xuất `70` sản phẩm `SP001` khi tồn kho ban đầu là `100`.
- **Kết quả sinh ra:** 1 điểm quét thành công (`HTTP 201`, tồn còn `30`), 1 điểm quét bị từ chối (`HTTP 400 INSUFFICIENT_STOCK`), ghi biên bản vào [`logs/ketqua_thu_dong_thoi.txt`](file:///E:/CNNT/diem-quet/logs/ketqua_thu_dong_thoi.txt).

### 4.3. Kịch bản dựng IP thật (`192.168.20.11`, `192.168.20.12` -> `192.168.10.10`) trên máy ảo Linux WSL2
```powershell
python diem-quet/chay_thu_2_may_wsl.py
```
- **Thực hiện:** Tự động gắn 3 IP tĩnh (`192.168.10.10/24`, `192.168.20.11/24`, `192.168.20.12/24`) lên card `eth0` của máy ảo `Ubuntu-22.04`, kiểm tra `ping`, gắn cứng IP nguồn (`SourceIPAdapter`) cho `SP01` & `SP02` bắn giao dịch về `http://192.168.10.10:5000` và trích xuất log máy chủ.
- **Kết quả sinh ra:** Ghi biên bản vào [`logs/ketqua_chay_2_may_wsl.txt`](file:///E:/CNNT/diem-quet/logs/ketqua_chay_2_may_wsl.txt).

---

## 5. Cách 3: Kết nối Điểm quét sang máy chủ ở máy khác (Laptop SV3 hoặc Máy ảo)

Khi ghép bài trực tiếp với máy của SV3 qua mạng LAN / Wi-Fi / Radmin VPN (giả sử máy SV3 có IP `192.168.1.50`), bạn chỉ cần truyền thêm cờ `--url` khi chạy `scanner.py` mà không cần sửa file JSON:

```powershell
python diem-quet/scanner.py diem-quet/config_sp01.json --url http://192.168.1.50:5000
python diem-quet/scanner.py diem-quet/config_sp02.json --url http://192.168.1.50:5000
```
Hoặc với script xuất đồng thời:
```powershell
python diem-quet/thu_dong_thoi_xuat.py --base-url http://192.168.1.50:5000
```

---

## 6. Danh mục ảnh minh chứng trong `diem-quet/evidence/`

| STT | Tệp ảnh | Nội dung |
| :---: | :--- | :--- |
| 1 | `MC_SV2_01_HaiDiemQuetSongSong.png` | **CV01:** Hai điểm quét `SP01` và `SP02` chạy song song và kiểm tra kết nối máy chủ (`200 OK`). |
| 2 | `MC_SV2_02_KiemTraDauVao.png` | **CV02:** Chặn các trường hợp nhập liệu sai tại điểm quét (`INVALID_INPUT`). |
| 3 | `MC_SV2_03_GiaoDichHopLe_DocLai.png` | **CV02:** Giao dịch hợp lệ (`201`) + đọc lại bản ghi từ máy chủ + xử lý `409`, `403`, `404`, `INSUFFICIENT_STOCK`. |
| 4 | `MC_SV2_04_MatMang_HangDoi_Retry.png` | **CV03:** Mất kết nối mạng, lưu `queue_SP01.jsonl`, chờ tăng dần (`5s -> 10s`) và đồng bộ khi có mạng lại. |
| 5 | `MC_SV2_05_BangSoDo_DoiChieuSeqNo.png` | **CV03:** Bảng số đo độ trễ `Min/Avg/Max`, số lần retry và đối chiếu khớp 100% các `seq_no`. |
| 6 | `MC_SV2_06_DongThoiXuat_2DiemQuet.png` | **Nâng cao (+2đ):** Thử nghiệm 2 điểm quét xuất đồng thời 1 mặt hàng, chống âm tồn kho. |
| 7 | `MC_SV2_07_ChayThu2May_Windows_UbuntuVM.png` | **Hạ tầng IP thật:** Cấu hình `ip addr`, `ping` và gửi giao dịch từ `192.168.20.11`, `192.168.20.12` tới `192.168.10.10:5000` trên máy ảo Linux. |
