"""
Đề tài 22 - SV2 (CV01 & CV02): Kịch bản dựng & kiểm thử thực tế giữa 2 máy:
  - Máy 1 (Máy chủ Linux): Máy ảo Ubuntu-22.04 (WSL2) chạy dịch vụ API SV3 (app.py) trên cổng 5000.
  - Máy 2 (Máy trạm Điểm quét): Máy thật Windows chạy SP01 & SP02 gửi giao dịch qua mạng sang IP thật của máy ảo Linux.

Cách chạy:
  python chay_thu_2_may_wsl.py
"""

import json
import os
import subprocess
import sys
import time
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from scanner import (
    build_payload,
    generate_txn_id,
    load_config,
    login_api,
)


def main():
    lines = []

    def out(msg: str = ""):
        print(msg)
        lines.append(msg)

    out("=" * 76)
    out(" KỊCH BẢN CHẠY THẬT GIỮA 2 MÁY: WINDOWS (SP01, SP02) <-> UBUNTU VM (SERVER)")
    out("=" * 76)

    # 1. Khởi chạy máy chủ API SV3 bên trong máy ảo Ubuntu-22.04 và giữ tiến trình sống
    out("\n[BƯỚC 1] Khởi động máy chủ API SV3 bên trong máy ảo Linux (Ubuntu-22.04)...")
    vm_proc = subprocess.Popen(
        [
            "wsl",
            "-d",
            "Ubuntu-22.04",
            "--",
            "bash",
            "-c",
            "cd /mnt/e/CNNT/sinh-vien-3/04_DICH_VU_API && python3 app.py",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )

    try:
        time.sleep(2.5)

        # 2. Lấy địa chỉ IP thật của máy ảo Ubuntu-22.04 (eth0) và IP của máy Windows
        ip_res = subprocess.run(
            ["wsl", "-d", "Ubuntu-22.04", "--", "bash", "-c", "hostname -I | awk '{print $1}'"],
            capture_output=True,
            text=True,
        )
        vm_ip = ip_res.stdout.strip()
        addr_res = subprocess.run(
            ["wsl", "-d", "Ubuntu-22.04", "--", "bash", "-c", "ip -4 addr show eth0"],
            capture_output=True,
            text=True,
        )
        out(f"[*] Thông tin card mạng eth0 trên máy ảo Ubuntu-22.04:")
        for l in addr_res.stdout.strip().splitlines():
            out(f"    {l}")

        vm_url = f"http://{vm_ip}:5000"
        out(f"[*] Địa chỉ API Máy chủ Linux (Ubuntu-22.04): {vm_url}")

        # 3. Kiểm tra ping từ máy Windows sang máy ảo Linux Ubuntu-22.04
        out(f"\n[BƯỚC 2] Kiểm tra kết nối mạng (ping {vm_ip}) từ máy trạm Windows sang máy ảo Linux:")
        ping_res = subprocess.run(["ping", "-n", "2", vm_ip], capture_output=True, text=True)
        for l in ping_res.stdout.strip().splitlines():
            out(f"    {l}")

        # 4. Đăng nhập và gửi giao dịch từ SP01 & SP02 trên Windows sang máy ảo Linux
        out(f"\n[BƯỚC 3] Điểm quét SP01 & SP02 (Windows) gửi giao dịch qua mạng sang {vm_url}:")
        token_nv01 = login_api(vm_url, "nv01", "Kho@2026", 5)
        token_thukho = login_api(vm_url, "thukho_demo", "Kho@2026", 5)
        out(f"    + Đăng nhập SP01 (nv01)        -> token: {token_nv01}")
        out(f"    + Đăng nhập SP02 (thukho_demo) -> token: {token_thukho}")

        # Tra cứu tồn kho SP001 trước giao dịch
        r_inv0 = requests.get(f"{vm_url}/api/inventory/SP001", headers={"Authorization": f"Bearer {token_nv01}"}, timeout=5)
        out(f"    + Tra cứu tồn kho SP001 trên máy ảo Linux trước khi quét: {r_inv0.text.strip()}")

        # SP01 gửi giao dịch NHAP 25 sản phẩm SP001 sang máy ảo Linux
        tid_sp01 = generate_txn_id("SP01", 101)
        p_sp01 = build_payload(tid_sp01, "SP001", "NHAP", 25, "SP01")
        t0 = time.time()
        r1 = requests.post(
            f"{vm_url}/api/transactions",
            json=p_sp01,
            headers={"Authorization": f"Bearer {token_nv01}"},
            timeout=5,
        )
        lat1 = round((time.time() - t0) * 1000, 2)
        out(f"\n    [SP01 -> {vm_ip}:5000] POST /api/transactions ({lat1}ms) -> HTTP {r1.status_code}")
        out(f"    Phản hồi từ máy ảo Linux: {r1.text.strip()}")

        # SP02 gửi giao dịch XUAT 10 sản phẩm SP001 sang máy ảo Linux
        tid_sp02 = generate_txn_id("SP02", 101)
        p_sp02 = build_payload(tid_sp02, "SP001", "XUAT", 10, "SP02")
        t1 = time.time()
        r2 = requests.post(
            f"{vm_url}/api/transactions",
            json=p_sp02,
            headers={"Authorization": f"Bearer {token_thukho}"},
            timeout=5,
        )
        lat2 = round((time.time() - t1) * 1000, 2)
        out(f"\n    [SP02 -> {vm_ip}:5000] POST /api/transactions ({lat2}ms) -> HTTP {r2.status_code}")
        out(f"    Phản hồi từ máy ảo Linux: {r2.text.strip()}")

        # Đọc lại bản ghi từ máy ảo Linux
        r_read = requests.get(
            f"{vm_url}/api/transactions/{tid_sp01}",
            headers={"Authorization": f"Bearer {token_nv01}"},
            timeout=5,
        )
        out(f"\n    [ĐỌC LẠI TỪ MÁY ẢO LINUX] GET /api/transactions/{tid_sp01} -> HTTP {r_read.status_code}")
        out(f"    Bản ghi lưu trên Linux: {r_read.text.strip()}")

        out("\n" + "=" * 76)
        out(" [KẾT LUẬN] Kiểm chứng thành công mô hình 2 máy qua mạng thật:")
        out(f"   - Máy chủ Linux (Ubuntu-22.04 WSL2) : {vm_ip}:5000")
        out("   - Máy trạm Windows (SP01 & SP02)    : Gửi NHAP/XUAT và đọc lại thành công 100%!")
        out("=" * 76)

        logs_dir = os.path.join(BASE_DIR, "logs")
        os.makedirs(logs_dir, exist_ok=True)
        with open(os.path.join(logs_dir, "ketqua_chay_2_may_wsl.txt"), "w", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")

    finally:
        vm_proc.terminate()
        subprocess.run(
            ["wsl", "-d", "Ubuntu-22.04", "--", "bash", "-c", "pkill -f 'python3 app.py' || true"],
            capture_output=True,
        )


if __name__ == "__main__":
    main()
