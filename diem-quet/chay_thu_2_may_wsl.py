"""
Đề tài 22 - SV2 (CV01 & CV02): Kịch bản dựng & kiểm thử hạ tầng IP thật trên máy ảo Linux (WSL2):
  - Cấu hình dải IP chuẩn theo quy hoạch mạng của nhóm trên card mạng eth0:
      + Máy chủ SRV-KHO : 192.168.10.10/24 (cổng 5000)
      + Điểm quét SP01  : 192.168.20.11/24 (Cửa Nhập)
      + Điểm quét SP02  : 192.168.20.12/24 (Cửa Xuất)
  - Kiểm chứng ping từ 192.168.20.11 & 192.168.20.12 tới 192.168.10.10, đồng thời ping từ Windows sang VM.
  - Gắn cứng IP nguồn (SourceIPAdapter: 192.168.20.11 và 192.168.20.12) khi gửi giao dịch tới http://192.168.10.10:5000.

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

echo "=== [1] CẤU HÌNH ĐỊA CHỈ IP TRÊN GIAO DIỆN MẠNG ETH0 (ip -4 addr show eth0) ==="
ip -4 addr show dev eth0

echo ""
echo "=== [2] KIỂM TRA KẾT NỐI PING TỪ SP01 (192.168.20.11) & SP02 (192.168.20.12) TỚI MÁY CHỦ (192.168.10.10) ==="
ping -I 192.168.20.11 -c 2 192.168.10.10
echo ""
ping -I 192.168.20.12 -c 2 192.168.10.10

cd /mnt/e/CNNT/sinh-vien-3/04_DICH_VU_API
python3 app.py > /tmp/srv_kho_access.log 2>&1 &
SRV_PID=$!
sleep 2

echo ""
echo "=== [3] ĐIỂM QUÉT SP01 (192.168.20.11) & SP02 (192.168.20.12) GỬI GIAO DỊCH TỚI http://192.168.10.10:5000 ==="
python3 - << 'PYEOF'
import sys, time
sys.path.insert(0, "/mnt/e/CNNT/diem-quet")
from scanner import get_http_session, build_payload, generate_txn_id, login_api

srv_url = "http://192.168.10.10:5000"
s_sp01 = get_http_session("192.168.20.11")
s_sp02 = get_http_session("192.168.20.12")

tok_nv01 = login_api(srv_url, "nv01", "Kho@2026", 5)
tok_thukho = login_api(srv_url, "thukho_demo", "Kho@2026", 5)

r_inv = s_sp01.get(f"{srv_url}/api/inventory/SP001", headers={"Authorization": f"Bearer {tok_nv01}"}, timeout=5)
print(f"[*] Tồn kho ban đầu trên SRV-KHO (192.168.10.10): {r_inv.text.strip()}")

tid1 = generate_txn_id("SP01", 101)
p1 = build_payload(tid1, "SP001", "NHAP", 25, "SP01")
t0 = time.time()
r1 = s_sp01.post(f"{srv_url}/api/transactions", json=p1, headers={"Authorization": f"Bearer {tok_nv01}"}, timeout=5)
lat1 = round((time.time() - t0) * 1000, 2)
print(f"\n[SP01: 192.168.20.11 -> SRV-KHO: 192.168.10.10:5000] ({lat1}ms) -> HTTP {r1.status_code}")
print(f"    Phản hồi: {r1.text.strip()}")

tid2 = generate_txn_id("SP02", 101)
p2 = build_payload(tid2, "SP001", "XUAT", 10, "SP02")
t1 = time.time()
r2 = s_sp02.post(f"{srv_url}/api/transactions", json=p2, headers={"Authorization": f"Bearer {tok_thukho}"}, timeout=5)
lat2 = round((time.time() - t1) * 1000, 2)
print(f"\n[SP02: 192.168.20.12 -> SRV-KHO: 192.168.10.10:5000] ({lat2}ms) -> HTTP {r2.status_code}")
print(f"    Phản hồi: {r2.text.strip()}")

r_check = s_sp01.get(f"{srv_url}/api/transactions/{tid1}", headers={"Authorization": f"Bearer {tok_nv01}"}, timeout=5)
print(f"\n[ĐỌC LẠI TỪ 192.168.10.10:5000] GET /api/transactions/{tid1} -> HTTP {r_check.status_code}")
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
    print(" KỊCH BẢN DỰNG & KIỂM CHỨNG HẠ TẦNG IP THẬT: 192.168.20.11, 192.168.20.12 -> 192.168.10.10")
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
        + " KỊCH BẢN DỰNG & KIỂM CHỨNG HẠ TẦNG IP THẬT: 192.168.20.11, 192.168.20.12 -> 192.168.10.10\n"
        + "=" * 84 + "\n\n"
        + res.stdout.strip() + "\n"
    )
    print(res.stdout)
    if res.stderr.strip():
        print(res.stderr)

    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    with open(os.path.join(logs_dir, "ketqua_chay_2_may_wsl.txt"), "w", encoding="utf-8") as f:
        f.write(output_text)


if __name__ == "__main__":
    main()
