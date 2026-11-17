# KỊCH BẢN TRÌNH DIỄN (DEMO) & CHUẨN BỊ VẤN ĐÁP – SINH VIÊN 2 (ĐIỂM QUÉT)
**Đề tài 22:** Xây dựng cơ sở hạ tầng cho hệ thống quản lý kho hàng thông minh  
**Vai trò chung của SV2 (2 điểm):** Người chuẩn bị kịch bản demo, dữ liệu mẫu, luồng trình diễn lỗi và mất mạng.

---

## 1. Danh mục tệp mã nguồn & minh chứng của SV2 (`diem-quet/`)

| STT | Tệp tin | Vai trò theo đề cương (`CV01`, `CV02`, `CV03`, Nâng cao) |
| :---: | :--- | :--- |
| 1 | `scanner.py` | Chương trình máy khách điểm quét dùng chung cho `SP01` và `SP02`: đăng nhập lấy Bearer Token, sinh `txn_id = SPxx-yyyymmdd-nnnn`, kiểm tra đầu vào, lưu `seq_no` và hàng đợi `queue/queue_SPxx.jsonl` xuống đĩa (`fsync`), gửi lại tăng dần (`5 -> 10 -> 20 -> 60s`), đọc lại bản ghi từ máy chủ và đối chiếu `seq_no`. |
| 2 | `config_sp01.json`, `config_sp02.json` | Cấu hình tách rời cho Điểm quét 1 (`SP01 - 192.168.20.11`, nhân viên `nv01`) và Điểm quét 2 (`SP02 - 192.168.20.12`, thủ kho `thukho_demo`), trỏ tới API máy chủ `http://127.0.0.1:5000`, lưu log vào `logs/` và hàng đợi vào `queue/`. |
| 3 | `config_scan01.json`, `config_scan02.json` | Cấu hình tương thích tài khoản demo của SV3 (`nhanvien_demo`, `thukho_demo`). |
| 4 | `thu_mat_mang_va_doi_chieu.py` | Kịch bản tự động kiểm thử toàn diện `CV02` & `CV03`, tự động sinh file nhật ký (`logs/log_SP01.log`, `logs/log_SP02.log`), hàng đợi (`queue/queue_SP01.jsonl`, `queue/queue_SP02.jsonl`), số thứ tự (`queue/seq_SP01.txt`, `queue/seq_SP02.txt`) và xuất báo cáo `BaoCao_SoDo_MatMang_SV2.md`. |
| 5 | `thu_dong_thoi_xuat.py` | Kịch bản nâng cao (+2 điểm): kích hoạt 2 luồng `SP01` và `SP02` đồng thời xuất cùng 1 mặt hàng (`SP001`, mỗi bên xuất `70` khi tồn `100`) và ghi biên bản `logs/ketqua_thu_dong_thoi.txt`. |
| 6 | `BaoCao_SoDo_MatMang_SV2.md` | Báo cáo số đo độ trễ, tỉ lệ gửi thành công, số lần gửi lại và bảng đối chiếu `seq_no` với máy chủ (`CV03`). |

---

## 2. Dữ liệu mẫu dùng trong buổi bảo vệ

### 2.1. Tài khoản phân quyền (mật khẩu chung: `Kho@2026`)
- `nv01` / `nhanvien_demo` (**Nhân viên nhập kho** – `employee`): Chỉ được phép `NHAP`, bị chặn `403 FORBIDDEN` nếu cố tình `XUAT`.
- `thukho_demo` / `thukho01` (**Thủ kho** – `warehouse`): Được phép cả `NHAP` và `XUAT`.
- `viewer_demo` / `xem01` (**Người chỉ xem** – `viewer`): Chỉ được tra cứu tồn kho, bị chặn `403 FORBIDDEN` khi gửi giao dịch.

### 2.2. Mặt hàng mẫu trên CSDL
- `SP001` – Cảm biến nhiệt độ DHT22 (Tồn khởi tạo: `100`)
- `SP003` – Đầu đọc mã vạch Zebra DS2208 (Tồn khởi tạo: `30`)
- `SP005` – Thùng nhựa đựng linh kiện A4 (Tồn khởi tạo: `15`)
- `SP006` – Cuộn tem nhãn mã vạch 50x30mm (Tồn khởi tạo: `16`)

---

## 3. Kịch bản trình diễn trực tiếp 4 bước (5–7 phút)

### Bước 1: Khởi động máy chủ API (SV3) và 2 điểm quét `SP01`, `SP02` (SV2 – `CV01`)
1. Mở Terminal 1 (Máy chủ SV3):
   ```powershell
   python sinh-vien-3/04_DICH_VU_API/app.py
   ```
2. Mở Terminal 2 (Điểm quét 1 – Cửa Nhập `SP01`):
   ```powershell
   cd diem-quet
   python scanner.py config_sp01.json
   ```
   *(Nhấn Enter để đăng nhập mặc định `nv01`)*
3. Mở Terminal 3 (Điểm quét 2 – Cửa Xuất `SP02`):
   ```powershell
   cd diem-quet
   python scanner.py config_sp02.json
   ```
   *(Nhấn Enter để đăng nhập mặc định `thukho_demo`)*

### Bước 2: Trình diễn giao dịch hợp lệ, đọc lại từ máy chủ & chặn lỗi nghiệp vụ (`CV02`)
1. **Kiểm tra tồn kho ban đầu:** Tại Terminal 2 (`SP01`), chọn phím `4` -> nhập `SP001` -> hiển thị tồn kho hiện tại.
2. **Gửi giao dịch Nhập hợp lệ + Đọc lại:** Chọn phím `1` -> nhập `SP001`, loại `NHAP`, số lượng `20`.
   - Quan sát JSON sinh ra đúng chuẩn SV1 (`txn_id = SP01-yyyymmdd-0001`), máy chủ trả về `201 Created` kèm `stock_after`, và điểm quét tự động gọi `GET /api/transactions/<txn_id>` đọc lại bản ghi vừa lưu.
3. **Chặn đầu vào sai tại điểm quét:** Chọn phím `1` -> nhập số lượng `-5` hoặc `0` -> bị chặn ngay tại máy trạm (`INVALID_INPUT`), không tốn băng thông gửi lên máy chủ.
4. **Chống trùng giao dịch (`KT2`):** Chọn phím `3` -> nhập lại mã `SP01-yyyymmdd-0001` vừa gửi -> máy chủ trả `409 DUPLICATE_TXN`, điểm quét báo chống trùng thành công, tồn kho không bị cộng hai lần.
5. **Chặn sai quyền (`403`) & Xuất quá tồn (`INSUFFICIENT_STOCK`):**
   - Chọn phím `6` đổi sang `viewer_demo`, sau đó chọn phím `1` gửi giao dịch -> bị chặn `403 FORBIDDEN`.
   - Tại `SP02`, chọn phím `1` xuất `SP003` với số lượng `500` -> bị chặn `INSUFFICIENT_STOCK`.

### Bước 3: Trình diễn mất mạng, hàng đợi trên đĩa, tắt đột ngột và phục hồi (`CV03`)
1. **Ngắt máy chủ API:** Tại Terminal 1, nhấn `Ctrl + C` để dừng `app.py` (giả lập đứt mạng tới máy chủ).
2. **Quét hàng khi mất mạng:** Tại `SP01`, chọn phím `1` nhập `SP005`, loại `NHAP`, số lượng `15`.
   - Quan sát điểm quét lưu ngay vào `queue_SP01.jsonl` với trạng thái `CHO_XAC_NHAN`, giữ nguyên `txn_id` và thực hiện chờ tăng dần (`5s -> 10s...`).
3. **Khôi phục mạng & tự động đồng bộ:** Bật lại `app.py` ở Terminal 1 -> tại `SP01` chọn phím `2` (hoặc tắt đi bật lại `scanner.py`) -> hàng đợi tự động đẩy giao dịch tồn đọng lên máy chủ và chuyển trạng thái sang `DA_XAC_NHAN`.
4. **Xem bảng số đo & đối chiếu `seq_no`:** Chọn phím `5` trên `scanner.py` để in bảng độ trễ (Min/Avg/Max), tỉ lệ thành công và đối chiếu `seq_no` khớp 100% với CSDL máy chủ.

### Bước 4: Trình diễn xuất đồng thời 2 điểm quét (Tầng nâng cao +2 điểm)
Chạy lệnh tự động:
```powershell
python diem-quet/thu_dong_thoi_xuat.py
```
- Kịch bản kích hoạt 2 luồng `SP01` và `SP02` cùng lúc yêu cầu xuất `70` sản phẩm `SP001` khi tồn kho chỉ có `100`.
- Kết quả: Đúng 1 bên thành công (`201`, tồn còn `30`), 1 bên bị từ chối (`400 INSUFFICIENT_STOCK`), tồn kho không bao giờ âm.

---

## 4. Trả lời chuẩn 5 câu hỏi vấn đáp của SV2

1. **`txn_id` được tạo như thế nào để hai điểm quét không bao giờ sinh trùng mã?**
   - Mỗi điểm quét được định danh bằng tiền tố `scan_point_id` riêng biệt (`SP01`, `SP02`) kết hợp ngày hiện tại (`yyyymmdd`) và số thứ tự tăng dần cục bộ (`seq_no` lưu trong `seq_SP01.txt`, `seq_SP02.txt`), tạo thành `SPxx-yyyymmdd-nnnn`. Nhờ tiền tố `SP01` khác `SP02`, hai máy trạm hoạt động độc lập hoàn toàn vẫn không bao giờ sinh trùng `txn_id`.

2. **Khi mất mạng, làm sao đảm bảo khi gửi lại không làm cộng/trừ tồn kho hai lần?**
   - Điểm quét cấp phát `txn_id` và lưu vào `queue_SPxx.jsonl` **trước** khi gửi mạng. Trong suốt các lần retry, điểm quét giữ nguyên `txn_id` cũ (cơ chế Idempotency). Nếu gói tin trước thực chất đã được máy chủ xử lý nhưng mất gói phản hồi ACK, lần gửi lại sẽ bị khóa `UNIQUE(txn_id)` trên máy chủ chặn và trả về `409 DUPLICATE_TXN`. Điểm quét nhận `409` sẽ đánh dấu `DA_XAC_NHAN` mà không cộng/trừ tồn kho lần hai.

3. **Nếu đang mất mạng mà chương trình điểm quét bị tắt đột ngột thì sao?**
   - Mọi thao tác tăng `seq_no` (`get_next_seq_no`) và ghi hàng đợi (`save_queue`) đều gọi `f.flush()` và `os.fsync(f.fileno())` để ép hệ điều hành ghi thẳng xuống đĩa cứng ngay lập tức. Khi bật lại `scanner.py`, hàm `flush_pending_queue()` chạy tự động ngay lúc khởi động, đọc lại các bản ghi `CHO_XAC_NHAN` từ `queue_SPxx.jsonl` và gửi tiếp lên máy chủ.

4. **Tại sao phải chờ tăng dần (`5 -> 10 -> 20 -> 60` giây) thay vì gửi lại liên tục?**
   - Cơ chế *Exponential Backoff* tránh hiện tượng bão yêu cầu (*Retry Storm*) làm nghẽn băng thông mạng LAN hoặc làm quá tải máy chủ ngay thời điểm máy chủ vừa khởi động lại sau sự cố.

5. **Làm sao chứng minh không mất giao dịch nào sau đợt mất mạng?**
   - Sử dụng chức năng số `5` trên `scanner.py` hoặc chạy `thu_mat_mang_va_doi_chieu.py` để đối chiếu dãy `seq_no` từ `1..N` tại từng điểm quét với các bản ghi trên máy chủ qua API `GET /api/transactions/<txn_id>`. Mọi `seq_no` đều được giải trình rõ ràng: hoặc đã nằm trong CSDL (`DA_XAC_NHAN`), hoặc bị từ chối hợp lệ do lỗi nghiệp vụ (`TU_CHOI`), không có khoảng trống `seq_no` nào bị thất lạc.
