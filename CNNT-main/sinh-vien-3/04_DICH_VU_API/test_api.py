"""
KỊCH BẢN KIỂM THỬ TỰ ĐỘNG DỊCH VỤ API (SV3 - MÃ VIỆC CV02)
-----------------------------------------------------------
Kiểm thử toàn diện 10 ca kiểm thử nghiệp vụ:
  TC01: Đăng nhập thành công và cấp Bearer Token
  TC02: Đăng nhập thất bại khi sai mật khẩu (401 LOGIN_FAILED)
  TC03: Kiểm tra ma trận phân quyền: Tài khoản QUANLY/xem01 bị chặn ghi (403 FORBIDDEN)
  TC04: Kiểm tra xác thực đầu vào: Số lượng âm / vượt 10000 (400 INVALID_QUANTITY)
  TC05: Ghi giao dịch hợp lệ NHẬP KHO (201 Created) & Tồn kho tăng
  TC06: Đọc lại giao dịch bằng GET /api/transactions/{txn_id} (200 OK)
  TC07: Ghi giao dịch hợp lệ XUẤT KHO (201 Created) & Tồn kho giảm
  TC08: Chống trùng giao dịch khi gửi lại cùng txn_id (409 Conflict - Ca KT2)
  TC09: Chống âm tồn kho khi xuất vượt tồn (422 INSUFFICIENT_STOCK - Ca KT3)
  TC10: Đối chiếu tồn kho (GET /api/reconcile - Phục vụ SV4)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
import requests

API_BASE_URL = "http://127.0.0.1:8080"


class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"


def log_test(tc_id: str, desc: str, passed: bool, detail: str = ""):
    status = f"{Colors.GREEN}[ĐẠT - PASS]{Colors.RESET}" if passed else f"{Colors.RED}[TRƯỢT - FAIL]{Colors.RESET}"
    print(f"{Colors.BOLD}{tc_id}:{Colors.RESET} {desc} -> {status}")
    if detail:
        print(f"   Chi tiết: {detail}")


def run_tests(base_url: str):
    print("=" * 70)
    print(f"{Colors.CYAN}BẮT ĐẦU KIỂM THỬ TỰ ĐỘNG DỊCH VỤ API SV3 TẠI: {base_url}{Colors.RESET}")
    print("=" * 70)

    results = []

    # -------------------------------------------------------------
    # TC01: Đăng nhập thành công (nv01)
    # -------------------------------------------------------------
    tc_id = "TC01"
    desc = "Đăng nhập thành công tài khoản nhân viên (nv01)"
    nv01_token = ""
    try:
        res = requests.post(f"{base_url}/api/login", json={"username": "nv01", "password": "Kho@2026"}, timeout=5)
        data = res.json()
        passed = (res.status_code == 200 and data.get("status") == "OK" and "token" in data)
        nv01_token = data.get("token", "")
        log_test(tc_id, desc, passed, f"HTTP {res.status_code}, Token: {nv01_token[:20]}...")
        results.append((tc_id, desc, passed, f"HTTP {res.status_code}"))
    except Exception as e:
        log_test(tc_id, desc, False, str(e))
        results.append((tc_id, desc, False, str(e)))

    # -------------------------------------------------------------
    # TC02: Đăng nhập sai mật khẩu (401)
    # -------------------------------------------------------------
    tc_id = "TC02"
    desc = "Đăng nhập thất bại khi sai mật khẩu (401 LOGIN_FAILED)"
    try:
        res = requests.post(f"{base_url}/api/login", json={"username": "nv01", "password": "SaiMatKhau123"}, timeout=5)
        data = res.json()
        passed = (res.status_code == 401 and data.get("error_code") == "LOGIN_FAILED")
        log_test(tc_id, desc, passed, f"HTTP {res.status_code}, error_code: {data.get('error_code')}")
        results.append((tc_id, desc, passed, f"HTTP {res.status_code}"))
    except Exception as e:
        log_test(tc_id, desc, False, str(e))
        results.append((tc_id, desc, False, str(e)))

    # -------------------------------------------------------------
    # TC03: Kiểm tra phân quyền: QUANLY/xem01 bị chặn ghi giao dịch (403)
    # -------------------------------------------------------------
    tc_id = "TC03"
    desc = "Ma trận phân quyền: Tài khoản QUANLY bị chặn ghi giao dịch (403 FORBIDDEN - KT3a)"
    try:
        # Đăng nhập quanly01
        res_login = requests.post(f"{base_url}/api/login", json={"username": "quanly01", "password": "Kho@2026"}, timeout=5)
        ql_token = res_login.json().get("token", "")

        # Thử ghi giao dịch
        headers = {"Authorization": f"Bearer {ql_token}"}
        txn_data = {
            "txn_id": "SP01-20261105-9999",
            "product_code": "SP001",
            "txn_type": "NHAP",
            "quantity": 10,
            "scan_point_id": "SP01"
        }
        res_write = requests.post(f"{base_url}/api/transactions", json=txn_data, headers=headers, timeout=5)
        passed = (res_write.status_code == 403 and res_write.json().get("error_code") == "FORBIDDEN")
        log_test(tc_id, desc, passed, f"HTTP {res_write.status_code}, error_code: {res_write.json().get('error_code')}")
        results.append((tc_id, desc, passed, f"HTTP {res_write.status_code}"))
    except Exception as e:
        log_test(tc_id, desc, False, str(e))
        results.append((tc_id, desc, False, str(e)))

    # Headers chuẩn của nv01 cho các ca tiếp theo
    nv_headers = {"Authorization": f"Bearer {nv01_token}"}

    # -------------------------------------------------------------
    # TC04: Kiểm tra đầu vào: Số lượng âm / không hợp lệ (400)
    # -------------------------------------------------------------
    tc_id = "TC04"
    desc = "Kiểm tra xác thực đầu vào: Số lượng <= 0 (400 INVALID_QUANTITY)"
    try:
        bad_data = {
            "txn_id": "SP01-20261105-0000",
            "product_code": "SP001",
            "txn_type": "NHAP",
            "quantity": -5,
            "scan_point_id": "SP01"
        }
        res = requests.post(f"{base_url}/api/transactions", json=bad_data, headers=nv_headers, timeout=5)
        passed = (res.status_code == 400 and res.json().get("error_code") == "INVALID_QUANTITY")
        log_test(tc_id, desc, passed, f"HTTP {res.status_code}, message: {res.json().get('message')}")
        results.append((tc_id, desc, passed, f"HTTP {res.status_code}"))
    except Exception as e:
        log_test(tc_id, desc, False, str(e))
        results.append((tc_id, desc, False, str(e)))

    # -------------------------------------------------------------
    # TC05: Ghi giao dịch hợp lệ NHẬP KHO (201 Created)
    # -------------------------------------------------------------
    tc_id = "TC05"
    desc = "Ghi giao dịch hợp lệ NHẬP KHO (201 Created & cập nhật tồn kho)"
    test_txn_id = f"SP01-TEST-{int(time.time())}"
    stock_before = 0
    stock_after = 0
    try:
        # Lấy tồn trước khi nhập
        res_inv = requests.get(f"{base_url}/api/inventory/SP001", headers=nv_headers, timeout=5)
        stock_before = res_inv.json().get("quantity", 0)

        # Gửi giao dịch nhập 15
        import_data = {
            "txn_id": test_txn_id,
            "product_code": "SP001",
            "txn_type": "NHAP",
            "quantity": 15,
            "scan_point_id": "SP01",
            "client_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        }
        res_txn = requests.post(f"{base_url}/api/transactions", json=import_data, headers=nv_headers, timeout=5)
        res_data = res_txn.json()
        stock_after = res_data.get("stock_after", 0)

        passed = (res_txn.status_code == 201 and res_data.get("status") == "OK" and stock_after == stock_before + 15)
        log_test(tc_id, desc, passed, f"HTTP {res_txn.status_code}, Tồn trước: {stock_before} -> Sau: {stock_after}")
        results.append((tc_id, desc, passed, f"Tồn: {stock_before}->{stock_after}"))
    except Exception as e:
        log_test(tc_id, desc, False, str(e))
        results.append((tc_id, desc, False, str(e)))

    # -------------------------------------------------------------
    # TC06: Đọc lại giao dịch GET /api/transactions/{txn_id} (200 OK)
    # -------------------------------------------------------------
    tc_id = "TC06"
    desc = "Đọc lại chi tiết giao dịch theo txn_id để xác nhận đã lưu (200 OK - CV02)"
    try:
        res_get = requests.get(f"{base_url}/api/transactions/{test_txn_id}", headers=nv_headers, timeout=5)
        data = res_get.json()
        passed = (res_get.status_code == 200 and data.get("product_code") == "SP001" and data.get("quantity") == 15)
        log_test(tc_id, desc, passed, f"HTTP {res_get.status_code}, txn_id: {data.get('txn_id')}")
        results.append((tc_id, desc, passed, f"HTTP {res_get.status_code}"))
    except Exception as e:
        log_test(tc_id, desc, False, str(e))
        results.append((tc_id, desc, False, str(e)))

    # -------------------------------------------------------------
    # TC07: Ghi giao dịch hợp lệ XUẤT KHO (201 Created)
    # -------------------------------------------------------------
    tc_id = "TC07"
    desc = "Ghi giao dịch hợp lệ XUẤT KHO (201 Created & trừ tồn kho)"
    test_export_id = f"SP02-TEST-EXP-{int(time.time())}"
    try:
        export_data = {
            "txn_id": test_export_id,
            "product_code": "SP001",
            "txn_type": "XUAT",
            "quantity": 5,
            "scan_point_id": "SP02"
        }
        res_exp = requests.post(f"{base_url}/api/transactions", json=export_data, headers=nv_headers, timeout=5)
        data = res_exp.json()
        new_stock = data.get("stock_after", 0)
        passed = (res_exp.status_code == 201 and new_stock == stock_after - 5)
        log_test(tc_id, desc, passed, f"HTTP {res_exp.status_code}, Tồn sau xuất: {new_stock}")
        results.append((tc_id, desc, passed, f"Tồn: {stock_after}->{new_stock}"))
    except Exception as e:
        log_test(tc_id, desc, False, str(e))
        results.append((tc_id, desc, False, str(e)))

    # -------------------------------------------------------------
    # TC08: Chống trùng giao dịch (409 Conflict - Ca KT2)
    # -------------------------------------------------------------
    tc_id = "TC08"
    desc = "Chống trùng giao dịch khi gửi lại cùng txn_id (409 Conflict - Ca KT2)"
    try:
        duplicate_data = {
            "txn_id": test_txn_id,  # Dùng lại test_txn_id đã gửi ở TC05
            "product_code": "SP001",
            "txn_type": "NHAP",
            "quantity": 15,
            "scan_point_id": "SP01"
        }
        res_dup = requests.post(f"{base_url}/api/transactions", json=duplicate_data, headers=nv_headers, timeout=5)
        data = res_dup.json()
        passed = (res_dup.status_code == 409 and data.get("error_code") == "DUPLICATE_TXN")
        log_test(tc_id, desc, passed, f"HTTP {res_dup.status_code}, error_code: {data.get('error_code')}")
        results.append((tc_id, desc, passed, f"HTTP {res_dup.status_code}"))
    except Exception as e:
        log_test(tc_id, desc, False, str(e))
        results.append((tc_id, desc, False, str(e)))

    # -------------------------------------------------------------
    # TC09: Chống âm tồn kho khi xuất vượt quá tồn (422 INSUFFICIENT_STOCK)
    # -------------------------------------------------------------
    tc_id = "TC09"
    desc = "Chống âm tồn kho khi xuất vượt quá số lượng tồn (422 INSUFFICIENT_STOCK - Ca KT3)"
    try:
        insufficient_data = {
            "txn_id": f"SP01-FAIL-{int(time.time())}",
            "product_code": "SP001",
            "txn_type": "XUAT",
            "quantity": 500,
            "scan_point_id": "SP01"
        }
        res_fail = requests.post(f"{base_url}/api/transactions", json=insufficient_data, headers=nv_headers, timeout=5)
        data = res_fail.json()
        passed = (res_fail.status_code == 422 and data.get("error_code") == "INSUFFICIENT_STOCK")
        log_test(tc_id, desc, passed, f"HTTP {res_fail.status_code}, error_code: {data.get('error_code')}")
        results.append((tc_id, desc, passed, f"HTTP {res_fail.status_code}"))
    except Exception as e:
        log_test(tc_id, desc, False, str(e))
        results.append((tc_id, desc, False, str(e)))

    # -------------------------------------------------------------
    # TC10: Đối chiếu tồn kho (GET /api/reconcile)
    # -------------------------------------------------------------
    tc_id = "TC10"
    desc = "Đối chiếu số liệu tồn kho toàn hệ thống (GET /api/reconcile)"
    try:
        # Dùng tài khoản admin hoặc thukho để đối chiếu
        res_adm = requests.post(f"{base_url}/api/login", json={"username": "thukho01", "password": "Kho@2026"}, timeout=5)
        tk_token = res_adm.json().get("token", "")
        tk_headers = {"Authorization": f"Bearer {tk_token}"}

        res_rec = requests.get(f"{base_url}/api/reconcile", headers=tk_headers, timeout=5)
        data = res_rec.json()
        passed = (res_rec.status_code == 200 and data.get("status") == "OK" and "items" in data)
        log_test(tc_id, desc, passed, f"HTTP {res_rec.status_code}, Số mặt hàng đối chiếu: {len(data.get('items', []))}")
        results.append((tc_id, desc, passed, f"HTTP {res_rec.status_code}"))
    except Exception as e:
        log_test(tc_id, desc, False, str(e))
        results.append((tc_id, desc, False, str(e)))

    # =============================================================
    # TỔNG KẾT BẢNG BÁO CÁO
    # =============================================================
    total = len(results)
    pass_cnt = sum(1 for r in results if r[2])
    print("-" * 70)
    print(f"{Colors.BOLD}KẾT QUẢ KIỂM THỬ: {pass_cnt}/{total} CA ĐẠT CHUẨN{Colors.RESET}")
    print("=" * 70)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Script kiểm thử tự động API SV3")
    parser.add_argument("--url", default="http://127.0.0.1:8080", help="URL máy chủ API")
    args = parser.parse_args()

    run_tests(args.url)
