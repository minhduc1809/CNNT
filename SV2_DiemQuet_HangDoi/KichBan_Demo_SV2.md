# Kịch bản trình diễn và vấn đáp SV2

**Đề tài 22:** Hệ thống quản lý kho hàng thông minh  
**Phạm vi trình bày:** điểm quét SP01/SP02, xác thực, hàng đợi cục bộ, gửi lại và đối chiếu.

## Chuẩn bị trước buổi bảo vệ

1. SV3 xác nhận API đang kết nối MySQL thật, nêu địa chỉ IP/cổng và chuẩn bị một bản sao lưu hoặc dữ liệu thử có thể khôi phục.
2. Chạy hai điểm quét từ hai máy hoặc VM riêng nếu cần chứng minh giao tiếp mạng. Nếu buổi demo chỉ chạy loopback hoặc nhiều IP trên cùng WSL, nói rõ đó là mô phỏng trên một máy.
3. Chọn mã hàng và số tồn ban đầu đã kiểm tra trực tiếp trong MySQL. Không dùng số tồn giả định từ README hoặc dữ liệu in-memory.
4. Dùng tài khoản thử do SV3 cấp; không ghi mật khẩu vào ảnh chụp, log hay báo cáo.
5. Dùng bản mã hiện hành và kiểm tra rằng ảnh minh chứng phù hợp với số lần gửi, mã HTTP và cấu hình retry hiện tại.

## Trình diễn 5–7 phút

### Bước 1 – Khởi động và xác thực

Mở API SV3 theo hướng dẫn của SV3, sau đó chạy từng điểm quét:

```powershell
python SV2_DiemQuet_HangDoi\scanner.py SV2_DiemQuet_HangDoi\config_sp01.json
python SV2_DiemQuet_HangDoi\scanner.py SV2_DiemQuet_HangDoi\config_sp02.json
```

Nhập username và mật khẩu. Scanner phải dừng nếu API không đăng nhập được hoặc không trả token. Nêu địa chỉ đích đang dùng. Nếu địa chỉ là loopback, không giới thiệu ca này như kết nối hai máy.

### Bước 2 – Giao dịch hợp lệ và xác nhận lưu

1. Ở SP01 chọn `4`, tra cứu mã hàng đã chuẩn bị và ghi tồn trước.
2. Chọn `1`, nhập một giao dịch NHAP có số lượng nhỏ.
3. Chỉ kết luận thành công khi API trả xác nhận. Scanner gọi `GET /api/transactions/<txn_id>` để đọc lại.
4. Đối chiếu giao dịch và tồn mới trong MySQL Workbench hoặc công cụ SV3 cung cấp.

### Bước 3 – Kiểm tra dữ liệu sai, quyền và giao dịch trùng

1. Nhập số lượng `0`, số âm hoặc loại giao dịch không hợp lệ; scanner phải chặn trước khi gửi.
2. Gửi lại một `txn_id` đã được lưu và quan sát phản hồi trùng từ API.
3. Đăng nhập lại bằng tài khoản chỉ xem rồi thử ghi; đối chiếu mã từ chối với nhật ký API.

Không suy luận rằng tồn kho không đổi chỉ từ thông báo client; đọc lại tồn hoặc bản ghi trong MySQL.

### Bước 4 – API không kết nối được và đồng bộ hàng đợi

1. Dùng CSDL thử nghiệm. Dừng API hoặc tạm cấu hình URL tới cổng đóng.
2. Tạo một giao dịch mới. Quan sát trạng thái `CHO_XAC_NHAN`, các lần gửi lại và thời gian chờ.
3. Khi API sẵn sàng, dùng chức năng `2` hoặc khởi động lại scanner để gửi lại cùng `txn_id`.
4. Đọc giao dịch trong API/MySQL để xác nhận kết quả.

Đây là mô phỏng API không kết nối được. Kịch bản này không tự chứng minh mất điện, cắt mạng giữa hai máy hoặc kill tiến trình giữa lúc ghi. Kịch bản tự động dùng khoảng chờ rút gọn 1 và 2 giây; cấu hình scanner mặc định dùng 5, 10, 20 và 60 giây. Báo cáo phải nêu đúng lịch chờ của lần chạy.

### Bước 5 – Ca xuất đồng thời nâng cao

Chạy trong CSDL thử nghiệm với số lượng xuất mỗi điểm lớn hơn một nửa tồn ban đầu:

```powershell
python SV2_DiemQuet_HangDoi\thu_dong_thoi_xuat.py --base-url http://<IP_MAY_CHU>:8080 --code SP001 --qty 70
```

Nhập mật khẩu thủ kho khi được hỏi. Kết quả chỉ đạt nếu một yêu cầu được nhận, một yêu cầu bị từ chối do thiếu tồn và tồn cuối bằng tồn đầu trừ đúng một lần xuất. Lưu log mới có thời gian, rồi xác nhận kết quả trong MySQL.

## Giới hạn cần nói rõ

- `chay_thu_2_may_wsl.py` gắn nhiều IP lên cùng giao diện WSL. Nó minh họa cấu hình địa chỉ nguồn, nhưng không phải hai máy độc lập, không chứng minh định tuyến VLAN và không kiểm tra firewall thật.
- Kịch bản tự động CV02/CV03 dùng API đang chạy; nó không tự xác nhận API đang ghi vào MySQL thay vì bộ nhớ. SV3 phải xác nhận backend trước khi chạy và SV4 cần đối chiếu CSDL.
- Kịch bản tự động không kill tiến trình. Muốn trình bày dừng đột ngột, phải chạy ca riêng, kết thúc tiến trình thật sau khi hàng đợi đã fsync, khởi động lại và đối chiếu dữ liệu.
- Nếu thiếu ảnh/log của lần chạy hiện tại, ghi “chưa kiểm chứng” thay vì dùng ảnh cũ để minh họa.

## Câu hỏi vấn đáp

### 1. `txn_id` được tạo thế nào?

Mã gồm điểm quét, ngày và số thứ tự, ví dụ `SP01-yyyymmdd-0001`. SP01/SP02 có tiền tố riêng. Bộ đếm được lưu trên đĩa; máy chủ vẫn cần ràng buộc duy nhất để chống gửi trùng.

### 2. Vì sao ghi hàng đợi trước khi gửi?

Nếu API không phản hồi, máy khách vẫn còn bản ghi để thử lại. Mỗi giao dịch có `txn_id` giữ nguyên qua các lần gửi. Nhật ký hiện lưu sự kiện thêm mới và sự kiện cập nhật trạng thái dưới dạng JSONL nối thêm.

### 3. Hàng đợi xử lý thế nào khi dừng đột ngột?

Mỗi dòng hàng đợi được ghi nối thêm và đồng bộ xuống đĩa; bộ đếm được ghi qua tệp tạm rồi thay thế nguyên tử. Đây là thiết kế trong mã, nhưng chỉ được coi là đã kiểm chứng sau khi chạy ca dừng tiến trình thật và xác nhận lại trên máy khởi động lại.

### 4. Vì sao gửi lại với khoảng chờ tăng dần?

Khoảng chờ tăng dần giúp giảm tải khi máy chủ chưa sẵn sàng. Cần phân biệt số lần gửi tổng cộng với số lần retry: lịch `[5, 10, 20, 60]` có tối đa năm lần gửi, gồm một lần đầu và bốn lần gửi lại.

### 5. Làm sao xác nhận không mất hoặc ghi đúp?

Đối chiếu từng `txn_id`/`seq_no` giữa nhật ký máy khách và bảng giao dịch, kiểm tra tồn trước/sau trong MySQL, và ghi nhận các giao dịch bị từ chối. Nếu có khoảng trống `seq_no`, cần giải thích bằng nhật ký; không mặc định rằng khoảng trống đồng nghĩa giao dịch bị mất.
