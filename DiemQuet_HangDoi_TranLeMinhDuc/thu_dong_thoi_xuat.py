"""
Đề tài 22 - SV2 (Tầng nâng cao): Thử nghiệm gửi đồng thời từ 2 điểm quét cùng xuất 1 mặt hàng.
Mục tiêu: Chứng minh tính nhất quán dữ liệu, cơ chế transaction và chống âm tồn kho (Ngày 14–16).
Bàn giao cho SV4 để phối hợp nghiệm thu.

Cách chạy:
    python thu_dong_thoi_xuat.py [--base-url http://192.168.10.10:8080] [--code SP001] [--qty 70]
"""

import argparse
import concurrent.futures
from datetime import datetime
import getpass
import json
import os
import sys
import time
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(BASE_DIR)
API_DIR = os.path.join(REPO_ROOT, "MayChu_CSDL_API_PhamCongManh", "04_DICH_VU_API")
if API_DIR not in sys.path:
    sys.path.insert(0, API_DIR)


def login(base_url: str, username: str, password: str) -> str:
    try:
        r = requests.post(f"{base_url}/api/login", json={"username": username, "password": password}, timeout=5)
        if r.status_code != 200:
            raise RuntimeError(f"Đăng nhập thất bại: HTTP {r.status_code}: {r.text.strip()}")
        token = r.json().get("token")
        if not isinstance(token, str) or not token.strip():
            raise RuntimeError("API đăng nhập không trả Bearer token hợp lệ")
        return token.strip()
    except requests.RequestException as e:
        raise RuntimeError(f"Không kết nối được API: {e}") from e
    except ValueError as e:
        raise RuntimeError("API đăng nhập trả JSON không hợp lệ") from e


def get_stock(base_url: str, product_code: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    try:
        r = requests.get(f"{base_url}/api/inventory/{product_code}", headers=headers, timeout=5)
        if r.status_code == 200:
            data = r.json()
            return data.get("quantity", data.get("items", {}).get("quantity"))
    except Exception as e:
        print(f"[LỖI] Không đọc được tồn kho: {e}")
    return None


def send_scan_request(base_url: str, scan_point_id: str, product_code: str, quantity: int, token: str):
    today = datetime.now().strftime("%Y%m%d")
    now_ms = int(time.time() * 1000) % 10000
    txn_id = f"{scan_point_id}-{today}-{now_ms:04d}"

    payload = {
        "txn_id": txn_id,
        "product_code": product_code,
        "txn_type": "XUAT",
        "quantity": quantity,
        "scan_point_id": scan_point_id,
        "client_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    start = time.time()
    try:
        r = requests.post(f"{base_url}/api/transactions", json=payload, headers=headers, timeout=5)
        latency = round((time.time() - start) * 1000, 2)
        return {
            "scan_point_id": scan_point_id,
            "txn_id": txn_id,
            "status_code": r.status_code,
            "response": r.json() if r.headers.get("content-type", "").startswith("application/json") else r.text,
            "latency_ms": latency,
        }
    except Exception as e:
        latency = round((time.time() - start) * 1000, 2)
        return {
            "scan_point_id": scan_point_id,
            "txn_id": txn_id,
            "status_code": 0,
            "response": str(e),
            "latency_ms": latency,
        }


def main():
    parser = argparse.ArgumentParser(description="Script thử nghiệm xuất đồng thời 2 điểm quét (SV2 nâng cao)")
    parser.add_argument("--base-url", default="http://192.168.10.10:8080", help="Địa chỉ API máy chủ")
    parser.add_argument("--code", default="SP001", help="Mã hàng cần thử xuất")
    parser.add_argument("--qty", type=int, default=70, help="Số lượng mỗi điểm quét xuất (đặt > 50% tồn kho)")
    parser.add_argument("--username", default="thukho_demo", help="Tài khoản có quyền xuất kho")
    args = parser.parse_args()

    try:
        token = login(args.base_url, args.username, getpass.getpass(f"Mật khẩu của {args.username}: "))
    except RuntimeError as exc:
        parser.error(str(exc))

    lines = []

    def out(msg: str = ""):
        print(msg)
        lines.append(msg)

    out("=" * 70)
    out(" KỊCH BẢN THỬ NGHIỆM ĐỒNG THỜI XUẤT KHO TỪ SP01 & SP02 (SV2 NÂNG CAO)")
    out(f" Máy chủ : {args.base_url}")
    out(f" Mã hàng : {args.code} | Số lượng mỗi bên yêu cầu xuất: {args.qty}")
    out("=" * 70)

    initial_stock = get_stock(args.base_url, args.code, token)
    out(f"[*] Tồn kho ban đầu của {args.code}: {initial_stock}")

    if initial_stock is not None and (args.qty * 2) <= initial_stock:
        out(f"[LƯU Ý] Tổng xuất ({args.qty * 2}) nhỏ hơn hoặc bằng tồn ({initial_stock}).")
        out("         Để kiểm tra chống âm tồn kho, nên chọn --qty lớn hơn một nửa tồn kho!")

    out("[*] Đang kích hoạt 2 luồng đồng thời...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(send_scan_request, args.base_url, "SP01", args.code, args.qty, token)
        f2 = executor.submit(send_scan_request, args.base_url, "SP02", args.code, args.qty, token)
        res1 = f1.result()
        res2 = f2.result()

    out("\n--- KẾT QUẢ PHẢN HỒI ---")
    for res in (res1, res2):
        out(f" điểm quét: {res['scan_point_id']} | txn_id: {res['txn_id']} | HTTP {res['status_code']} | trễ: {res['latency_ms']}ms")
        out(f"   phản hồi: {json.dumps(res['response'], ensure_ascii=False)}")

    final_stock = get_stock(args.base_url, args.code, token)
    out(f"\n[*] Tồn kho cuối cùng của {args.code}: {final_stock}")

    # Đánh giá kết quả
    success_count = sum(1 for r in (res1, res2) if r["status_code"] in (200, 201))
    rejected_count = sum(1 for r in (res1, res2) if r["status_code"] in (400, 422))

    out("\n--- KẾT LUẬN KIỂM CHỨNG ---")
    if initial_stock is not None and final_stock is not None and (args.qty * 2) > initial_stock:
        expected_final = initial_stock - args.qty
        if success_count == 1 and rejected_count == 1 and final_stock == expected_final:
            out(f"[ĐẠT] Một giao dịch được nhận, một giao dịch bị từ chối; tồn cuối {final_stock} khớp dự kiến {expected_final}.")
        else:
            out(f"[CHƯA ĐẠT] Kết quả chưa khớp: thành công={success_count}, từ chối={rejected_count}, tồn cuối={final_stock}, dự kiến={expected_final}.")
    elif initial_stock is None or final_stock is None:
        out("[CHƯA ĐỦ BẰNG CHỨNG] Không đọc được tồn kho trước hoặc sau giao dịch.")
    else:
        out("[CHƯA ĐỦ BẰNG CHỨNG] Số lượng thử không vượt quá tồn ban đầu hai lần; ca này chưa kiểm tra được tranh chấp thiếu tồn.")

    logs_dir = os.path.join(BASE_DIR, "logs")
    os.makedirs(logs_dir, exist_ok=True)
    report_file = os.path.join(logs_dir, f"ketqua_thu_dong_thoi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")



if __name__ == "__main__":
    main()
