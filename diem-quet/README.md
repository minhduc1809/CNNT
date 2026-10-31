# Điểm quét giả lập – Đề 22

Chương trình dòng lệnh Python đóng vai điểm quét: nhập thông tin giao dịch nhập/xuất,
sinh mã giao dịch và (ở các bước sau) gửi lên dịch vụ xử lý của SV3.

## Yêu cầu
- Python 3.10 trở lên (`python --version`)

## Cài đặt
```
python -m venv .venv
# Windows:      .venv\Scripts\activate
# Linux/macOS:  source .venv/bin/activate
pip install -r requirements.txt
```

## Chạy hai điểm quét
Mở hai cửa sổ terminal trong thư mục này:
```
python scanner.py config_scan01.json
python scanner.py config_scan02.json
```
Mỗi điểm quét dùng một file cấu hình riêng (mã điểm quét, địa chỉ máy chủ).
`server_url` để trống cho đến khi SV3 giao địa chỉ dịch vụ.

## Cấu trúc thư mục
| Mục | Công dụng |
|---|---|
| `scanner.py` | chương trình điểm quét |
| `config_scan01.json`, `config_scan02.json` | cấu hình từng điểm quét |
| `queue/` | hàng đợi cục bộ cho giao dịch chưa xác nhận (bước E) |
| `logs/` | nhật ký giao dịch và gửi lại |
| `evidence/` | ảnh và nhật ký minh chứng (đặt tên theo mã MC) |

## Tiến độ
| Bước | Nội dung | Trạng thái |
|---|---|---|
| A | Khung điểm quét: nhập, sinh mã, in JSON | đã có khung |
| B | Chạy hai điểm quét cùng lúc | |
| C | Kiểm tra đầu vào | |
| D | Gửi lên máy chủ, trạng thái chờ/đã xác nhận | |
| E | Hàng đợi và gửi lại khi mất mạng | |
