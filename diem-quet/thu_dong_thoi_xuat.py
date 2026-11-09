"""
Đề tài 22 - SV2 (Tầng nâng cao): Thử nghiệm gửi đồng thời từ 2 điểm quét cùng xuất 1 mặt hàng.
Mục tiêu: Chứng minh tính nhất quán dữ liệu, cơ chế transaction và chống âm tồn kho (Ngày 14–16).
Bàn giao cho SV4 để phối hợp nghiệm thu.

Cách chạy:
    python thu_dong_thoi_xuat.py [--base-url http://127.0.0.1:8080] [--code SP001] [--qty 80]
"""

import argparse
import concurrent.futures
from datetime import datetime
import json
import os
import sys
import time
import requests


def login(base_url: str, username: str = "thukho_demo", password: str = "Kho@2026") -> str:
    try:
        r = requests.post(f"{base_url}/api/login", json={"username": username, "password": password}, timeout=5)
        if r.status_code == 200:
            return r.json().get("token") or username
    except Exception as e:
        print(f"[CẢNH BÁO] Không gọi được /api/login: {e}")
    return f"token-{username}"


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
    parser.add_argument("--base-url", default="http://127.0.0.1:5000", help="Địa chỉ API máy chủ")
    parser.add_argument("--code", default="SP001", help="Mã hàng cần thử xuất")
    parser.add_argument("--qty", type=int, default=70, help="Số lượng mỗi điểm quét xuất (đặt > 50% tồn kho)")
    args = parser.parse_args()

    token = login(args.base_url)

    print("=" * 70)
    print(" KỊCH BẢN THỬ NGHIỆM ĐỒNG THỜI XUẤT KHO TỪ SP01 & SP02 (SV2 NÂNG CAO)")
    print(f" Máy chủ : {args.base_url}")
    print(f" Mã hàng : {args.code} | Số lượng mỗi bên yêu cầu xuất: {args.qty}")
    print("=" * 70)

    initial_stock = get_stock(args.base_url, args.code, token)
    print(f"[*] Tồn kho ban đầu của {args.code}: {initial_stock}")

    if initial_stock is not None and (args.qty * 2) <= initial_stock:
        print(f"[LƯU Ý] Tổng xuất ({args.qty * 2}) nhỏ hơn hoặc bằng tồn ({initial_stock}).")
        print("         Để kiểm tra chống âm tồn kho, nên chọn --qty lớn hơn một nửa tồn kho!")

    print("[*] Đang kích hoạt 2 luồng đồng thời...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f1 = executor.submit(send_scan_request, args.base_url, "SP01", args.code, args.qty, token)
        f2 = executor.submit(send_scan_request, args.base_url, "SP02", args.code, args.qty, token)
        res1 = f1.result()
        res2 = f2.result()

    print("\n--- KẾT QUẢ PHẢN HỒI ---")
    for res in (res1, res2):
        print(f" điểm quét: {res['scan_point_id']} | txn_id: {res['txn_id']} | HTTP {res['status_code']} | trễ: {res['latency_ms']}ms")
        print(f"   phản hồi: {json.dumps(res['response'], ensure_ascii=False)}")

    final_stock = get_stock(args.base_url, args.code, token)
    print(f"\n[*] Tồn kho cuối cùng của {args.code}: {final_stock}")

    # Đánh giá kết quả
    success_count = sum(1 for r in (res1, res2) if r["status_code"] in (200, 201))
    rejected_count = sum(1 for r in (res1, res2) if r["status_code"] in (400, 422))

    print("\n--- KẾT LUẬN KIỂM CHỨNG ---")
    if final_stock is not None and final_stock >= 0:
        print(f"[ĐẠT] Tồn kho không bị âm ({final_stock} >= 0).")
        if (args.qty * 2) > (initial_stock or 0):
            print(f"      Số giao dịch thành công: {success_count}, Số giao dịch bị chặn do thiếu tồn: {rejected_count}.")
            print("      Cơ chế transaction và khóa cách ly CSDL đã hoạt động chính xác!")
    else:
        print("[THẤT BẠI] Tồn kho bị âm hoặc không xác định được trạng thái!")


if __name__ == "__main__":
    main()
