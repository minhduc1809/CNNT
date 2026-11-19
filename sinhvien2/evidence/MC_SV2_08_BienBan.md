# Biên bản kiểm thử tích hợp SV2 qua WSL

**Ngày chạy:** 19/11/2026, khoảng 12:12 (giờ máy WSL)  
**Mã minh chứng:** MC_SV2_08  
**Phạm vi:** kiểm tra hai client SV2 có IP nguồn khác nhau gọi API, ghi giao dịch và đọc lại kết quả.

## Môi trường và cách chạy

Ubuntu 22.04 chạy trong WSL2. Trong cùng phiên WSL đã tạo ba network namespace và nối chúng qua bridge riêng:

| Thành phần | Namespace | Địa chỉ |
|---|---|---|
| Điểm quét SP01 | `cnnt_sp01_20261119` | `192.168.20.11/24` |
| Điểm quét SP02 | `cnnt_sp02_20261119` | `192.168.20.12/24` |
| API | `cnnt_srv_20261119` | `192.168.20.10/24`, cổng 5000 |

Hai client chạy các hàm `login_api`, `build_payload`, `enqueue_transaction` và `send_with_retry` trong `sinhvien2/scanner.py`. Máy chủ dùng API trong `sinh-vien-3/04_DICH_VU_API/app.py`. Nhật ký truy cập Flask cho thấy hai địa chỉ nguồn riêng biệt gọi đăng nhập, gửi giao dịch và đọc lại.

## Điều kiện kiểm thử

- Tồn khởi tạo mẫu của `SP001`: 100 đơn vị.
- SP01 đăng nhập tài khoản vai trò `employee`, nhập 5 đơn vị.
- SP02 đăng nhập tài khoản vai trò `warehouse`, xuất 3 đơn vị.
- Mật khẩu thử chỉ được gán vào bản ghi người dùng trong bộ nhớ lúc chạy để kiểm tra luồng đăng nhập; không ghi vào mã nguồn hoặc tệp cấu hình.
- API được buộc dùng fallback in-memory. WSL không có dịch vụ MySQL đang chạy, vì vậy lần chạy này không kiểm tra MySQL, Stored Procedure, ACID hoặc tính bền vững sau khi khởi động lại máy chủ.

## Kết quả

| Điểm quét | Nguồn | Giao dịch | HTTP ghi | Đọc lại | Tồn sau |
|---|---|---|---:|---:|---:|
| SP01 | `192.168.20.11` | `SP01-20261119-9001`, NHAP 5 | 201 | GET 200 | 105 |
| SP02 | `192.168.20.12` | `SP02-20261119-9001`, XUAT 3 | 201 | GET 200 | 102 |

Tồn kho mẫu đi theo chuỗi `100 → 105 → 102`. Cả hai bản ghi được đọc lại bằng endpoint chi tiết giao dịch và scanner đánh dấu `DA_XAC_NHAN`. Nhật ký máy chủ ghi nhận `/api/login` trả 200, `/api/transactions` trả 201 và GET theo mã giao dịch trả 200 từ đúng hai IP client.

## Kết luận và giới hạn

Đạt kiểm tra luồng client–server, gắn IP nguồn riêng cho từng client, xác thực, nhập/xuất, cập nhật hàng đợi cục bộ và đọc lại giao dịch trong môi trường WSL có network namespace. Đây là ba endpoint mạng cô lập trong cùng một WSL/nhân Linux; kết quả chưa chứng minh triển khai trên hai máy vật lý hoặc hai VM độc lập, chưa kiểm tra VLAN/firewall thực tế và chưa phải bằng chứng ghi dữ liệu vào MySQL. Khi nghiệm thu cuối, cần chạy lại cùng kịch bản với API nối MySQL và lưu truy vấn kiểm tra độc lập.

## Tệp đính kèm

- `MC_SV2_08_API_server.log`: log máy chủ, gồm địa chỉ client, endpoint và mã HTTP.
- `MC_SV2_08_SP01_client.log`, `MC_SV2_08_SP02_client.log`: log phía client, phản hồi API và nội dung đọc lại.
- `MC_SV2_08_SP01_queue.jsonl`, `MC_SV2_08_SP02_queue.jsonl`: nhật ký sự kiện hàng đợi tại hai điểm quét.
- `MC_SV2_08_SP01_result.log`, `MC_SV2_08_SP02_result.log`: dòng tổng kết xác nhận từng lượt chạy.

**Ảnh chụp màn hình thật:** hiện chưa có. Cần chụp trực tiếp các cửa sổ đang hiển thị log máy chủ và kết quả hai client rồi lưu PNG cạnh các tệp trên. Không dùng hình minh họa/tổng hợp thay cho ảnh chụp.


## Ghi chú cấu hình hiện hành

Biên bản và log MC_SV2_08 ghi đúng lần chạy WSL ngày 19/11/2026 trên cổng 5000. Sau lần chạy này, nhóm đưa cấu hình hiện hành về cổng 8080 theo giao ước SV1 v1.0. Log cũ được giữ nguyên làm bằng chứng lịch sử; chưa có lần chạy MC_SV2_08 mới trên cổng 8080.
