"""
Đề tài 22 - SV2: Mô phỏng nhiều địa chỉ IP trên một máy ảo Linux (WSL2):
  - Cấu hình các địa chỉ mô phỏng trên cùng một card mạng eth0:
      + Máy chủ SRV-KHO : 192.168.10.10/24 (cổng 8080)
      + Điểm quét SP01  : 192.168.20.11/24 (Cửa Nhập)
      + Điểm quét SP02  : 192.168.20.12/24 (Cửa Xuất)
  - Kiểm tra ping giữa các địa chỉ cục bộ cùng giao diện; đây không phải kiểm thử hai máy, định tuyến VLAN hay firewall.
  - Gắn IP nguồn mô phỏng khi gọi API trên cùng WSL.

Cách chạy:
  python chay_thu_2_may_wsl.py
"""

import os
import subprocess
import sys
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

WSL_SCRIPT = r"""
set -e
ip addr add 192.168.10.10/24 dev eth0 2>/dev/null || true
ip addr add 192.168.20.11/24 dev eth0 2>/dev/null || true
ip addr add 192.168.20.12/24 dev eth0 2>/dev/null || true

echo "=== MÔ PHỎNG NHIỀU IP TRÊN CÙNG MỘT GIAO DIỆN WSL ==="
ip -4 addr show dev eth0

echo ""
echo "=== [2] PING GIỮA CÁC ĐỊA CHỈ CÙNG MÁY (KHÔNG PHẢI HAI MÁY ĐỘC LẬP) ==="
ping -I 192.168.20.11 -c 2 192.168.10.10
echo ""
ping -I 192.168.20.12 -c 2 192.168.10.10

cd /mnt/e/CNNT/MayChu_CSDL_API_PhamCongManh/04_DICH_VU_API
python3 app.py > /tmp/srv_kho_access.log 2>&1 &
SRV_PID=$!
sleep 2

echo ""
echo "=== [3] ĐIỂM QUÉT SP01 (192.168.20.11) & SP02 (192.168.20.12) GỬI GIAO DỊCH TỚI http://192.168.10.10:8080 ==="
python3 - << 'PYEOF'
import sys, time, getpass
sys.path.insert(0, "/mnt/e/CNNT/DiemQuet_HangDoi_TranLeMinhDuc")
from scanner import get_http_session, build_payload, generate_txn_id, login_api

srv_url = "http://192.168.10.10:8080"
s_sp01 = get_http_session("192.168.20.11")
s_sp02 = get_http_session("192.168.20.12")

password_nv01 = getpass.getpass("Mật khẩu của nv01: ")
password_thukho = getpass.getpass("Mật khẩu của thukho_demo: ")
tok_nv01 = login_api(srv_url, "nv01", password_nv01, 5, "192.168.20.11")
tok_thukho = login_api(srv_url, "thukho_demo", password_thukho, 5, "192.168.20.12")

r_inv = s_sp01.get(f"{srv_url}/api/inventory/SP001", headers={"Authorization": f"Bearer {tok_nv01}"}, timeout=5)
print(f"[*] Tồn kho ban đầu trên SRV-KHO (192.168.10.10): {r_inv.text.strip()}")

tid1 = generate_txn_id("SP01", 101)
p1 = build_payload(tid1, "SP001", "NHAP", 25, "SP01")
t0 = time.time()
r1 = s_sp01.post(f"{srv_url}/api/transactions", json=p1, headers={"Authorization": f"Bearer {tok_nv01}"}, timeout=5)
lat1 = round((time.time() - t0) * 1000, 2)
print(f"\n[SP01: 192.168.20.11 -> SRV-KHO: 192.168.10.10:8080] ({lat1}ms) -> HTTP {r1.status_code}")
print(f"    Phản hồi: {r1.text.strip()}")

tid2 = generate_txn_id("SP02", 101)
p2 = build_payload(tid2, "SP001", "XUAT", 10, "SP02")
t1 = time.time()
r2 = s_sp02.post(f"{srv_url}/api/transactions", json=p2, headers={"Authorization": f"Bearer {tok_thukho}"}, timeout=5)
lat2 = round((time.time() - t1) * 1000, 2)
print(f"\n[SP02: 192.168.20.12 -> SRV-KHO: 192.168.10.10:8080] ({lat2}ms) -> HTTP {r2.status_code}")
print(f"    Phản hồi: {r2.text.strip()}")

r_check = s_sp01.get(f"{srv_url}/api/transactions/{tid1}", headers={"Authorization": f"Bearer {tok_nv01}"}, timeout=5)
print(f"\n[ĐỌC LẠI TỪ 192.168.10.10:8080] GET /api/transactions/{tid1} -> HTTP {r_check.status_code}")
print(f"    Bản ghi: {r_check.text.strip()}")
PYEOF

sleep 0.5
echo ""
echo "=== [4] NHẬT KÝ MÁY CHỦ SRV-KHO (192.168.10.10) GHI NHẬN ĐÚNG IP NGUỒN 192.168.20.11 & 192.168.20.12 ==="
grep -E "192\.168\.20\." /tmp/srv_kho_access.log || cat /tmp/srv_kho_access.log
kill $SRV_PID 2>/dev/null || true
"""


def main():
    print("=" * 84)
    print(" MÔ PHỎNG NHIỀU ĐỊA CHỈ IP TRÊN CÙNG WSL (KHÔNG PHẢI HAI MÁY THẬT)")
    print("=" * 84)

    res = subprocess.run(
        ["wsl", "-d", "Ubuntu-22.04", "--", "bash", "-c", WSL_SCRIPT],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    output_text = (
        "=" * 84 + "\n"
        + " MÔ PHỎNG NHIỀU ĐỊA CHỈ IP TRÊN CÙNG WSL (KHÔNG PHẢI HAI MÁY THẬT)\n"
        + "=" * 84 + "\n\n"
        + f"Mã thoát của kịch bản: {res.returncode}\n"
        + res.stdout.strip() + "\n"
        + ("\nSTDERR:\n" + res.stderr.strip() + "\n" if res.stderr.strip() else "")
    )
    print(res.stdout)
    if res.stderr.strip():
        print(res.stderr)

    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    with open(os.path.join(logs_dir, f"ketqua_mophong_ip_wsl_{time.strftime('%Y%m%d_%H%M%S')}.txt"), "w", encoding="utf-8") as f:
        f.write(output_text)
    if res.returncode != 0:
        raise SystemExit(f"Kịch bản WSL thất bại (mã {res.returncode}); xem log: {logs_dir}")


if __name__ == "__main__":
    main()
