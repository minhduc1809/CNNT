# Phân hệ điểm quét SV2

**Đề tài 22 – Hệ thống quản lý kho hàng thông minh**  
**Phụ trách:** chương trình điểm quét SP01/SP02, kiểm tra đầu vào, hàng đợi cục bộ, gửi lại khi gián đoạn và kịch bản demo.

## 1. Thành phần

- `scanner.py`: menu tương tác, đăng nhập API, tạo giao dịch, lưu hàng đợi, gửi lại và đọc lại kết quả.
- `config_sp01.json`, `config_sp02.json`: cấu hình điểm quét, IP nguồn, máy chủ API và đường dẫn lưu trữ cục bộ.
- `thu_mat_mang_va_doi_chieu.py`: kịch bản kiểm tra CV02/CV03 bằng API đang chạy.
- `thu_dong_thoi_xuat.py`: thử nghiệm nâng cao hai yêu cầu xuất đồng thời.
- `chay_thu_2_may_wsl.py`: mô phỏng địa chỉ nguồn trên một giao diện WSL; kịch bản này không tương đương hai máy độc lập.
- `queue/`: nhật ký giao dịch JSONL và bộ đếm `seq_no`.
- `logs/`, `evidence/`: nhật ký và ảnh minh chứng đã thu thập.

Lần chạy tích hợp WSL gần nhất có log là MC_SV2_08: hai client `.20.11`/`.20.12` gọi API `.20.10:5000` bằng fallback in-memory trong cùng WSL. Đó là kết quả lịch sử, không phải hai máy vật lý/VM độc lập. Cấu hình hiện hành của API/client đã chuyển về cổng 8080 theo giao ước SV1; MC_SV2_08 chưa được chạy lại sau khi đổi cổng.

## 2. Cài đặt

Cần Python 3.10 trở lên và các thư viện trong `requirements.txt`:

```powershell
cd E:\CNNT
python -m pip install -r SV2_DiemQuet_HangDoi\requirements.txt
```

Phân hệ SV2 cần API SV3 chạy và đăng nhập được. CSDL MySQL phải được xác nhận đang hoạt động trước khi nghiệm thu; nếu API SV3 đang dùng chế độ in-memory thì kết quả không được coi là kết quả MySQL.

## 3. Chạy điểm quét

Cấu hình mặc định trỏ tới máy chủ theo bảng IP nhóm `192.168.10.10:8080`. Chạy mỗi điểm quét trên máy/VM đã có IP nguồn tương ứng và nhập tài khoản, mật khẩu do SV3 cấp:

```powershell
python SV2_DiemQuet_HangDoi\scanner.py SV2_DiemQuet_HangDoi\config_sp01.json
python SV2_DiemQuet_HangDoi\scanner.py SV2_DiemQuet_HangDoi\config_sp02.json
```

Nếu cần chỉ định máy chủ khác, dùng `--url` hoặc biến môi trường `API_BASE_URL`:

```powershell
python SV2_DiemQuet_HangDoi\scanner.py SV2_DiemQuet_HangDoi\config_sp01.json --url http://<IP_MAY_CHU>:8080
```

Để chạy thử trên cùng máy, có thể dùng loopback; khi URL là loopback, scanner không gắn IP nguồn `.20.11`/`.20.12`. Ca này chỉ kiểm tra chức năng phần mềm, không chứng minh kết nối giữa các máy hoặc chính sách firewall.

Đăng nhập thất bại hoặc API không trả token hợp lệ thì scanner dừng trước khi gửi giao dịch. Mật khẩu được nhập ẩn, không có mật khẩu mặc định trong mã SV2.

### Menu

- `1`: nhập giao dịch mới; kiểm tra dữ liệu, cấp `seq_no`, tạo `txn_id`, ghi hàng đợi trước rồi gửi.
- `2`: gửi lại các bản ghi đang chờ, giữ nguyên `txn_id`.
- `3`: gửi lại một mã giao dịch để kiểm tra chống trùng.
- `4`: đọc tồn kho từ API.
- `5`: xem thống kê cục bộ và đối chiếu các giao dịch đã xác nhận.
- `6`: đăng nhập tài khoản khác; yêu cầu nhập lại mật khẩu.
- `0`: thoát.

## 4. Hàng đợi và độ bền dữ liệu

Hàng đợi là nhật ký JSON Lines chỉ ghi nối thêm. Mỗi dòng là sự kiện `enqueue` hoặc cập nhật `status`; cập nhật không viết lại toàn bộ tệp. Mỗi dòng được đồng bộ xuống đĩa bằng `fsync`. `seq_no` được cập nhật qua tệp tạm và thay thế nguyên tử.

Khi đọc hàng đợi, JSON lỗi không bị bỏ qua âm thầm: chương trình dừng và chỉ ra dòng lỗi để tránh tiếp tục khi có thể đã mất dấu giao dịch. Các hàng đợi dạng bản ghi JSONL cũ vẫn được đọc để giữ dữ liệu đã có.

## 5. Gửi lại và trạng thái giao dịch

Mặc định cấu hình có bốn khoảng chờ `[5, 10, 20, 60]` giây, tương ứng tối đa năm lần gửi tổng cộng: một lần ban đầu và bốn lần gửi lại. Đây không phải năm lần retry. Giao dịch được xác nhận sau HTTP 200/201 hoặc phản hồi trùng `409 DUPLICATE_TXN`; lỗi nghiệp vụ rõ ràng được ghi trạng thái từ chối; lỗi mạng hết số lần thử được giữ `CHO_XAC_NHAN`.

## 6. Chạy các kịch bản

Các script kiểm thử được thiết kế để gọi API đang chạy và có thể tạo dữ liệu giao dịch mới. Hãy dùng CSDL thử nghiệm, kiểm tra địa chỉ API và giữ lại log trước khi chạy. Không chạy trên dữ liệu cần bảo toàn nếu chưa có bản sao lưu.

```powershell
$env:API_BASE_URL = 'http://<IP_MAY_CHU>:8080'
python SV2_DiemQuet_HangDoi\thu_mat_mang_va_doi_chieu.py
python SV2_DiemQuet_HangDoi\thu_dong_thoi_xuat.py --base-url http://<IP_MAY_CHU>:8080
```

Kịch bản CV02/CV03 hỏi riêng mật khẩu của từng tài khoản và tạo thư mục chạy riêng trong `SV2_DiemQuet_HangDoi/logs/runs/`; nó không xóa hàng đợi/log có sẵn.

Kịch bản mất kết nối chuyển tạm URL tới cổng đóng; đây là mô phỏng lỗi kết nối. Dòng log “mô phỏng dừng tiến trình” không phải thao tác kill tiến trình thật. Muốn kết luận về tắt đột ngột, cần chạy một ca riêng: ghi giao dịch vào hàng đợi, kết thúc tiến trình thật trước khi gửi, khởi động lại và đối chiếu bản ghi với API/CSDL.

### Mô phỏng IP trên WSL

```powershell
python SV2_DiemQuet_HangDoi\chay_thu_2_may_wsl.py
```

Script gắn các IP nguồn giả lập lên cùng giao diện `eth0` trong một WSL. Ping các IP trên cùng máy không chứng minh hai máy độc lập, định tuyến giữa VLAN hay firewall thật. Không mô tả kết quả này là kiểm thử hai máy thật. Để chứng minh tiêu chí mạng, chạy SP01/SP02 trên hai máy hoặc VM riêng, chụp IP nguồn/đích, ping và gọi API qua IP máy chủ.

## 7. Minh chứng hiện có

| Tệp | Nội dung dự kiến |
|---|---|
| `evidence/MC_SV2_01_HaiDiemQuetSongSong.png` | Hai điểm quét chạy song song |
| `evidence/MC_SV2_02_KiemTraDauVao.png` | Chặn dữ liệu đầu vào sai |
| `evidence/MC_SV2_03_GiaoDichHopLe_DocLai.png` | Giao dịch hợp lệ và đọc lại |
| `evidence/MC_SV2_04_MatMang_HangDoi_Retry.png` | Mất kết nối, chờ tăng dần, hàng đợi |
| `evidence/MC_SV2_05_BangSoDo_DoiChieuSeqNo.png` | Số đo và đối chiếu |
| `evidence/MC_SV2_06_DongThoiXuat_2DiemQuet.png` | Xuất đồng thời |
| `evidence/MC_SV2_07_ChayThu2May_Windows_UbuntuVM.png` | Ảnh kịch bản Windows/WSL; cần mô tả đúng giới hạn nếu các IP nằm trên cùng máy |

Ảnh cũ cần được chụp lại nếu số lần gửi, mã phản hồi hoặc dữ liệu hiển thị không khớp mã hiện tại. Không dùng ảnh chưa được kiểm tra để khẳng định một phép thử đã hoàn thành.

## 8. Giới hạn đã biết

- Mô phỏng WSL nhiều địa chỉ trên một giao diện không phải thử nghiệm nhiều máy.
- Mất kết nối tới cổng đóng chứng minh ứng dụng xử lý lỗi kết nối; không chứng minh mất điện hoặc kill tiến trình giữa lúc ghi.
- MySQL thật phải được xác nhận riêng; phản hồi API đơn lẻ không đủ loại trừ chế độ dữ liệu in-memory của phía SV3.
- Các số liệu độ trễ, số lần gửi lại và kết quả đối chiếu phải lấy từ lần chạy cuối, không chép từ ảnh/log cũ.
