# Hướng dẫn dựng mô hình Packet Tracer – Đề tài 22 (SV1)

File đích: `KhoHang_DeTai22.pkt` (Cisco Packet Tracer 8.2 trở lên).
File cấu hình dùng kèm: `R1-KHO_router.txt`, `SW1-KHO_switch.txt`, `AP-KHO_wifi.txt`, `BangDiaChiIP.csv`.

> Packet Tracer chỉ chứng minh **cấu hình và kết nối** trong mô hình. Không dùng kết quả này để khẳng định thông lượng, vùng phủ Wi-Fi hay khả năng chịu tải của hệ thống thật.

## 1. Đặt thiết bị

| Tên đặt trong PT | Chọn thiết bị | Ghi chú |
|---|---|---|
| R1-KHO | Network Devices > Routers > **2911** | |
| SW1-KHO | Network Devices > Switches > **2960-24TT** | |
| AP-KHO | Network Devices > Wireless Devices > **AccessPoint-PT** | |
| SRV-KHO | End Devices > **Server-PT** | Máy chủ ứng dụng + CSDL |
| NAS-SAOLUU | End Devices > **Server-PT** | Đổi Display Name thành NAS-SAOLUU |
| PC-THUKHO, PC-QUANTRI, PC-QUANLY | End Devices > **PC-PT** | |
| SCAN-01 | End Devices > **PC-PT** | Điểm quét 1 – có dây |
| SCAN-02 | End Devices > **Laptop-PT** | Điểm quét 2 – Wi-Fi, lắp card **WPC300N** |

## 2. Nối dây (Copper Straight-Through)

| Từ | Cổng | Đến | Cổng |
|---|---|---|---|
| R1-KHO | G0/0 | SW1-KHO | G0/1 |
| SRV-KHO | Fa0 | SW1-KHO | Fa0/1 |
| NAS-SAOLUU | Fa0 | SW1-KHO | Fa0/2 |
| PC-THUKHO | Fa0 | SW1-KHO | Fa0/5 |
| PC-QUANTRI | Fa0 | SW1-KHO | Fa0/6 |
| PC-QUANLY | Fa0 | SW1-KHO | Fa0/7 |
| SCAN-01 | Fa0 | SW1-KHO | Fa0/9 |
| AP-KHO | Port 0 | SW1-KHO | Fa0/11 |
| SCAN-02 | (không dây) | AP-KHO | SSID KHO-QUETMA |

## 3. Nạp cấu hình

1. SW1-KHO → tab **CLI** → `enable` → `configure terminal` → dán `SW1-KHO_switch.txt`.
2. R1-KHO → tab **CLI** → `enable` → `configure terminal` → dán `R1-KHO_router.txt`.
3. AP-KHO và SCAN-02: làm theo `AP-KHO_wifi.txt`.
4. Các PC/Server: **Desktop → IP Configuration → Static**, nhập IP/mask/gateway/DNS theo `BangDiaChiIP.csv`.
5. SRV-KHO → **Services**:
   - **HTTP**: bật; sửa `index.html` thành trang “API kho hàng – SRV-KHO” để làm minh chứng.
   - **DNS**: bật; thêm bản ghi A `kho.local` → `192.168.10.10`.

## 4. Kiểm tra và chụp minh chứng

| # | Thực hiện tại | Lệnh / thao tác | Kết quả mong đợi | Ý nghĩa |
|---|---|---|---|---|
| N1 | SW1-KHO | `show vlan brief` | VLAN 10/20/30 đúng cổng | Chia 3 vùng mạng |
| N2 | SW1-KHO | `show interfaces trunk` | G0/1 trunk, VLAN 10,20,30 | Trunk lên router |
| N3 | R1-KHO | `show ip interface brief` | G0/0.10/.20/.30 up | Gateway từng VLAN |
| N4 | SCAN-01 | `ping 192.168.10.10` | Thành công | Điểm quét 1 tới máy chủ |
| N5 | SCAN-02 | `ping 192.168.10.10` | Thành công | Điểm quét 2 (Wi-Fi) tới máy chủ |
| N6 | SCAN-01 | Web Browser `http://kho.local` | Hiện trang SRV-KHO | DNS + HTTP qua ACL |
| N7 | SCAN-01 | `ping 192.168.10.20` | **Thất bại** (Destination unreachable) | ACL chặn điểm quét vào NAS |
| N8 | SCAN-01 | `ping 192.168.20.11` | **Thất bại** | Điểm quét không vào được văn phòng |
| N9 | PC-THUKHO | `ping 192.168.10.20` | Thành công (ICMP cho phép để chẩn đoán) | |
| N10 | R1-KHO | `show access-lists` | Bộ đếm `matches` tăng ở các dòng deny/permit | Bằng chứng ACL hoạt động |
| N11 | SW1-KHO | Cắm thêm 1 PC lạ vào Fa0/9 (thay SCAN-01) rồi ping | Cổng Fa0/9 chuyển **err-disabled** | Port-security |
| N12 | PC-QUANTRI | `telnet 192.168.10.2` | Hiện dấu nhắc mật khẩu của SW1-KHO | Chỉ quản trị viên vào được switch |
| N13 | PC-THUKHO | `telnet 192.168.10.2` | **Thất bại** | ACL_VANPHONG chặn |

## 5. Phần chạy thật và phần chỉ thể hiện trên sơ đồ

| Thành phần | Chạy thật (có bằng chứng thao tác) | Chỉ thể hiện trên sơ đồ / Packet Tracer |
|---|---|---|
| Điểm quét SP01, SP02 | Tiến trình client của SV2 trên laptop | Vị trí SCAN-01 (có dây), SCAN-02 (Wi-Fi) |
| Máy chủ ứng dụng + CSDL | server của SV3 + file SQLite `kho.db` | SRV-KHO 192.168.10.10 |
| Sao lưu | Thư mục `backup/` + lệnh sao lưu/khôi phục của SV3 | NAS-SAOLUU 192.168.10.20 |
| Vai trò thủ kho / quản trị / quản lý | Tài khoản thukho01, admin, quanly01 | Các máy PC-THUKHO, PC-QUANTRI, PC-QUANLY |
| Switch, router, Wi-Fi, 3 VLAN, ACL, port-security | — | Packet Tracer (chứng minh cấu hình và kết nối) |
| Mạng giữa điểm quét và máy chủ | Loopback 127.0.0.1 hoặc 2 laptop chung Wi-Fi | Đường đi qua SW1 → R1 → SW1 |

Lưu file `.pkt`, chụp ảnh toàn bộ sơ đồ topo và các màn hình N1–N11 (thấy rõ đồng hồ hệ thống để có dấu thời gian).
