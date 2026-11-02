
# 03 - GIAO ƯỚC API

## 1. Giới thiệu

Thư mục này lưu trữ tài liệu giao ước API giữa bộ phận cơ sở dữ liệu (Sinh viên 3) và bộ phận phát triển ứng dụng (Sinh viên 1).

Mục đích là thống nhất cách thức ứng dụng giao tiếp với hệ thống quản lý kho hàng thông minh, đảm bảo việc trao đổi dữ liệu được thống nhất và chính xác.

## 2. Phạm vi giao tiếp

API phục vụ các chức năng chính:

- Ghi nhận giao dịch nhập kho.
- Ghi nhận giao dịch xuất kho.
- Truy vấn thông tin tồn kho.
- Tra cứu lịch sử giao dịch.
- Xác định người dùng và điểm quét thực hiện giao dịch.

## 3. Nguyên tắc trao đổi dữ liệu

- Sử dụng JSON làm định dạng dữ liệu trao đổi.
- Thống nhất tên trường dữ liệu giữa ứng dụng và cơ sở dữ liệu.
- Mỗi giao dịch cần có mã giao dịch riêng để kiểm soát trùng lặp.
- Kiểm tra tính hợp lệ của dữ liệu trước khi ghi vào cơ sở dữ liệu.
- Giao dịch nhập, xuất kho phải cập nhật tồn kho chính xác.
- Trả về kết quả thành công hoặc thông báo lỗi phù hợp.

## 4. Các nội dung cần thống nhất với Sinh viên 1

- Địa chỉ và phương thức gọi API.
- Danh sách endpoint.
- Các tham số đầu vào.
- Cấu trúc dữ liệu JSON.
- Cấu trúc phản hồi và mã lỗi.
- Cơ chế xác thực và phân quyền.
- Cách xử lý giao dịch trùng lặp và lỗi kết nối.

## 5. Phối hợp triển khai

Sinh viên 3 chịu trách nhiệm cung cấp cấu trúc cơ sở dữ liệu, thủ tục xử lý giao dịch và các quy tắc nghiệp vụ liên quan.

Sinh viên 1 chịu trách nhiệm xây dựng ứng dụng và tích hợp API theo giao ước đã thống nhất.

## 6. Tài liệu

File `api_contract.md` sẽ trình bày chi tiết các endpoint, tham số, ví dụ request/response và quy tắc xử lý lỗi sau khi hai thành viên thống nhất.
