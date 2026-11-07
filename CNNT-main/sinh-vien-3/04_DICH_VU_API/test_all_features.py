import sys
import time
import requests
import json

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

BASE_URL = "http://localhost:5000"

class Colors:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    CYAN = "\033[96m"
    RESET = "\033[0m"
    BOLD = "\033[1m"

def print_header(title):
    print("\n" + "=" * 75)
    print(f"{Colors.BOLD}{Colors.CYAN}{title}{Colors.RESET}")
    print("=" * 75)

total_passed = 0
total_failed = 0

def run_test(tc_id, desc, fn):
    global total_passed, total_failed
    try:
        ok, detail = fn()
        if ok:
            total_passed += 1
            print(f"{Colors.GREEN}[PASS]{Colors.RESET} {Colors.BOLD}{tc_id}:{Colors.RESET} {desc}")
            print(f"       -> {Colors.CYAN}{detail}{Colors.RESET}")
        else:
            total_failed += 1
            print(f"{Colors.RED}[FAIL]{Colors.RESET} {Colors.BOLD}{tc_id}:{Colors.RESET} {desc}")
            print(f"       -> {Colors.RED}{detail}{Colors.RESET}")
    except Exception as e:
        total_failed += 1
        print(f"{Colors.RED}[FAIL]{Colors.RESET} {Colors.BOLD}{tc_id}:{Colors.RESET} {desc}")
        print(f"       -> {Colors.RED}Exception: {e}{Colors.RESET}")

# ----------------------------------------------------------------------
# 1. TEST PHÂN QUYỀN VÀ XÁC THỰC (AUTHENTICATION & RBAC)
# ----------------------------------------------------------------------
def test_authentication_rbac():
    print_header("PHẦN 1: KIỂM THỬ XÁC THỰC VÀ MA TRẬN PHÂN QUYỀN (RBAC)")

    tokens = {}

    def tc01():
        r = requests.post(f"{BASE_URL}/api/login", json={"username": "viewer_demo"})
        d = r.json()
        tokens["viewer"] = d.get("token")
        return r.status_code == 200 and d.get("role") == "viewer", f"HTTP {r.status_code}, Token: {tokens['viewer']}"
    run_test("TC01", "Đăng nhập tài khoản Viewer (viewer_demo)", tc01)

    def tc02():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN01", "txn_id": f"TXN-V-IN-{ts}", "product_code": "SP001", "txn_type": "NHAP", "quantity": 5},
            headers={"Authorization": f"Bearer {tokens['viewer']}"}
        )
        return r.status_code == 403, f"HTTP {r.status_code}, Bị chặn: {r.json().get('message')}"
    run_test("TC02", "Viewer cố tình ghi NHẬP KHO -> Bị từ chối 403 Forbidden", tc02)

    def tc03():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN01", "txn_id": f"TXN-V-OUT-{ts}", "product_code": "SP001", "txn_type": "XUAT", "quantity": 2},
            headers={"Authorization": f"Bearer {tokens['viewer']}"}
        )
        return r.status_code == 403, f"HTTP {r.status_code}, Bị chặn: {r.json().get('message')}"
    run_test("TC03", "Viewer cố tình ghi XUẤT KHO -> Bị từ chối 403 Forbidden", tc03)

    def tc04():
        r = requests.post(f"{BASE_URL}/api/login", json={"username": "nhanvien_demo"})
        d = r.json()
        tokens["employee"] = d.get("token")
        return r.status_code == 200 and d.get("role") == "employee", f"HTTP {r.status_code}, Token: {tokens['employee']}"
    run_test("TC04", "Đăng nhập tài khoản Nhân viên (nhanvien_demo)", tc04)

    def tc05():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN01", "txn_id": f"TXN-E-IN-{ts}", "product_code": "SP001", "txn_type": "NHAP", "quantity": 3},
            headers={"Authorization": f"Bearer {tokens['employee']}"}
        )
        return r.status_code == 201, f"HTTP {r.status_code}, Thành công, Tồn mới: {r.json().get('stock_after')}"
    run_test("TC05", "Nhân viên thực hiện NHẬP KHO -> Thành công 201 Created", tc05)

    def tc06():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN01", "txn_id": f"TXN-E-OUT-{ts}", "product_code": "SP001", "txn_type": "XUAT", "quantity": 1},
            headers={"Authorization": f"Bearer {tokens['employee']}"}
        )
        return r.status_code == 403, f"HTTP {r.status_code}, Bị chặn: {r.json().get('message')}"
    run_test("TC06", "Nhân viên cố tình XUẤT KHO -> Bị từ chối 403 Forbidden", tc06)

    def tc07():
        r = requests.post(f"{BASE_URL}/api/login", json={"username": "thukho_demo"})
        d = r.json()
        tokens["warehouse"] = d.get("token")
        return r.status_code == 200 and d.get("role") == "warehouse", f"HTTP {r.status_code}, Token: {tokens['warehouse']}"
    run_test("TC07", "Đăng nhập tài khoản Thủ kho (thukho_demo)", tc07)

    def tc08():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN02", "txn_id": f"TXN-W-OUT-{ts}", "product_code": "SP001", "txn_type": "XUAT", "quantity": 3},
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        return r.status_code == 201, f"HTTP {r.status_code}, Thành công, Tồn mới: {r.json().get('stock_after')}"
    run_test("TC08", "Thủ kho thực hiện XUẤT KHO -> Thành công 201 Created", tc08)

    def tc09():
        r = requests.get(f"{BASE_URL}/api/users", headers={"Authorization": f"Bearer {tokens['warehouse']}"})
        return r.status_code == 403, f"HTTP {r.status_code}, Bị chặn: {r.json().get('message')}"
    run_test("TC09", "Thủ kho cố tình xem danh sách Users -> Bị từ chối 403 Forbidden", tc09)

    def tc10():
        r = requests.post(f"{BASE_URL}/api/login", json={"username": "admin_demo"})
        d = r.json()
        tokens["admin"] = d.get("token")
        return r.status_code == 200 and d.get("role") == "admin", f"HTTP {r.status_code}, Token: {tokens['admin']}"
    run_test("TC10", "Đăng nhập tài khoản Quản trị viên (admin_demo)", tc10)

    def tc11():
        r = requests.get(f"{BASE_URL}/api/users", headers={"Authorization": f"Bearer {tokens['admin']}"})
        users = r.json()
        return r.status_code == 200 and len(users) >= 5, f"HTTP {r.status_code}, Danh sách {len(users)} người dùng hợp lệ"
    run_test("TC11", "Quản trị viên xem danh sách Users -> Thành công 200 OK", tc11)

    return tokens

# ----------------------------------------------------------------------
# 2. TEST CHỨC NĂNG NHẬP / XUẤT VÀ TÍNH TOÁN TỒN KHO (KT1)
# ----------------------------------------------------------------------
def test_import_export_lifecycle(tokens):
    print_header("PHẦN 2: KIỂM THỬ CHỨC NĂNG NHẬP/XUẤT & ĐỐI CHIẾU TỒN KHO (CA KT1)")

    target_product = "SP002"
    init_stock = requests.get(f"{BASE_URL}/api/inventory/{target_product}").json().get("quantity", 0)
    saved_txn_id = f"SCAN01-KT1-IN-{int(time.time())}"

    def tc12():
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={
                "scan_point_id": "SCAN01",
                "txn_id": saved_txn_id,
                "product_code": target_product,
                "txn_type": "NHAP",
                "quantity": 20
            },
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        d = r.json()
        new_stock = d.get("stock_after", 0)
        return r.status_code == 201 and new_stock == init_stock + 20, f"Tồn trước: {init_stock} -> Nhập: +20 -> Tồn sau: {new_stock}"
    run_test("TC12", f"Nhập kho tại điểm quét SCAN01 (+20 {target_product})", tc12)

    export_txn_id = f"SCAN02-KT1-OUT-{int(time.time())}"
    current_stock = requests.get(f"{BASE_URL}/api/inventory/{target_product}").json().get("quantity", 0)

    def tc13():
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={
                "scan_point_id": "SCAN02",
                "txn_id": export_txn_id,
                "product_code": target_product,
                "txn_type": "XUAT",
                "quantity": 8
            },
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        d = r.json()
        new_stock = d.get("stock_after", 0)
        return r.status_code == 201 and new_stock == current_stock - 8, f"Tồn trước: {current_stock} -> Xuất: -8 -> Tồn sau: {new_stock}"
    run_test("TC13", f"Xuất kho tại điểm quét SCAN02 (-8 {target_product})", tc13)

    def tc14():
        r = requests.get(f"{BASE_URL}/api/transactions/{saved_txn_id}")
        d = r.json()
        return r.status_code == 200 and d.get("transaction_id") == saved_txn_id and d.get("quantity") == 20, f"Đọc lại bản ghi MySQL: {d.get('transaction_id')}, Loại: {d.get('transaction_type')}, SL: {d.get('quantity')}"
    run_test("TC14", "Đọc lại giao dịch bằng GET /api/transactions/{txn_id}", tc14)

    return saved_txn_id

# ----------------------------------------------------------------------
# 3. TEST CHỐNG TRÙNG LẶP GIAO DỊCH (CA KT2)
# ----------------------------------------------------------------------
def test_idempotency(tokens, duplicated_txn_id):
    print_header("PHẦN 3: KIỂM THỬ CHỐNG TRÙNG LẶP MÃ GIAO DỊCH (CA KT2)")

    stock_before = requests.get(f"{BASE_URL}/api/inventory/SP002").json().get("quantity", 0)

    def tc15():
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={
                "scan_point_id": "SCAN01",
                "txn_id": duplicated_txn_id,  # Gửi lại đúng mã vừa tạo
                "product_code": "SP002",
                "txn_type": "NHAP",
                "quantity": 20
            },
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        stock_after = requests.get(f"{BASE_URL}/api/inventory/SP002").json().get("quantity", 0)
        return r.status_code == 409 and stock_after == stock_before, f"HTTP {r.status_code}, Thông báo: {r.json().get('message')} | Tồn kho giữ nguyên: {stock_after}"
    run_test("TC15", f"Gửi lại giao dịch trùng mã '{duplicated_txn_id}' -> 409 DUPLICATE_TXN & Tồn kho không đổi", tc15)

# ----------------------------------------------------------------------
# 4. TEST XỬ LÝ LỖI & RÀNG BUỘC TOÀN VẸN (CA LỖI & CA KT3)
# ----------------------------------------------------------------------
def test_error_and_edge_cases(tokens):
    print_header("PHẦN 4: KIỂM THỬ CÁC CA LỖI, CHỐNG ÂM KHO & VALIDATION")

    def tc16():
        ts = int(time.time() * 1000)
        # SP003 hiện có tồn kho là 25, yêu cầu xuất 100 (> 25 và <= 10000) để Stored Procedure kích hoạt chặn âm kho
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN02", "txn_id": f"TXN-ERR-{ts}", "product_code": "SP003", "txn_type": "XUAT", "quantity": 100},
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        return r.status_code == 400 and r.json().get("error_code") == "INSUFFICIENT_STOCK", f"HTTP {r.status_code}, Bị từ chối: {r.json().get('message')}"
    run_test("TC16", "Xuất hàng vượt quá số lượng tồn kho (Chống âm kho KT3)", tc16)

    def tc17():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN01", "txn_id": f"TXN-ERR-{ts}", "product_code": "SP_KHONG_TON_TAI", "txn_type": "NHAP", "quantity": 5},
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        return r.status_code == 404 and r.json().get("error_code") == "PRODUCT_NOT_FOUND", f"HTTP {r.status_code}, Lỗi: {r.json().get('message')}"
    run_test("TC17", "Giao dịch với mã sản phẩm không tồn tại trong danh mục", tc17)

    def tc18():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN_GIA_MAO", "txn_id": f"TXN-ERR-{ts}", "product_code": "SP001", "txn_type": "NHAP", "quantity": 5},
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        return r.status_code == 404 and r.json().get("error_code") == "SCAN_POINT_NOT_FOUND", f"HTTP {r.status_code}, Lỗi: {r.json().get('message')}"
    run_test("TC18", "Giao dịch với điểm quét không tồn tại trong hệ thống", tc18)

    def tc19():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN01", "txn_id": f"TXN-ERR-{ts}", "product_code": "SP001", "txn_type": "NHAP", "quantity": -10},
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        return r.status_code == 400 and r.json().get("error_code") == "INVALID_QUANTITY", f"HTTP {r.status_code}, Lỗi: {r.json().get('message')}"
    run_test("TC19", "Giao dịch với số lượng âm (quantity < 0)", tc19)

    def tc20():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN01", "txn_id": f"TXN-ERR-{ts}", "product_code": "SP001", "txn_type": "NHAP", "quantity": 0},
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        return r.status_code == 400 and r.json().get("error_code") == "INVALID_QUANTITY", f"HTTP {r.status_code}, Lỗi: {r.json().get('message')}"
    run_test("TC20", "Giao dịch với số lượng bằng 0 (quantity = 0)", tc20)

    def tc21():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN01", "txn_id": f"TXN-ERR-{ts}", "product_code": "SP001", "txn_type": "NHAP", "quantity": 999999},
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        return r.status_code == 400 and r.json().get("error_code") == "INVALID_QUANTITY", f"HTTP {r.status_code}, Lỗi: {r.json().get('message')}"
    run_test("TC21", "Giao dịch vượt giới hạn cho phép (> 10000)", tc21)

    def tc22():
        ts = int(time.time() * 1000)
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN01", "txn_id": f"TXN-ERR-{ts}", "product_code": "SP001", "txn_type": "MUA_HANG", "quantity": 5},
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        return r.status_code == 400 and r.json().get("error_code") == "INVALID_TXN_TYPE", f"HTTP {r.status_code}, Lỗi: {r.json().get('message')}"
    run_test("TC22", "Giao dịch sai loại (chỉ nhận NHAP/XUAT)", tc22)

    def tc23():
        r = requests.post(
            f"{BASE_URL}/api/transactions",
            json={"scan_point_id": "SCAN01", "product_code": "SP001", "txn_type": "NHAP", "quantity": 5},
            headers={"Authorization": f"Bearer {tokens['warehouse']}"}
        )
        return r.status_code == 400 and r.json().get("error_code") == "MISSING_FIELDS", f"HTTP {r.status_code}, Lỗi: {r.json().get('message')}"
    run_test("TC23", "Thiếu trường bắt buộc (bỏ trống txn_id)", tc23)

# ----------------------------------------------------------------------
# 5. TEST TRUY VẤN VÀ ĐỐI CHIẾU DỮ LIỆU
# ----------------------------------------------------------------------
def test_queries_and_reconciliation():
    print_header("PHẦN 5: KIỂM THỬ TRUY VẤN DỮ LIỆU & BÁO CÁO TỒN KHO")

    def tc24():
        r = requests.get(f"{BASE_URL}/api/transactions/recent")
        txns = r.json()
        return r.status_code == 200 and len(txns) > 0, f"HTTP {r.status_code}, Lấy được {len(txns)} giao dịch gần nhất từ CSDL"
    run_test("TC24", "Lấy 10 giao dịch gần nhất (GET /api/transactions/recent)", tc24)

    def tc25():
        r = requests.get(f"{BASE_URL}/api/inventory")
        inv = r.json()
        return r.status_code == 200 and len(inv) == 100, f"HTTP {r.status_code}, Toàn bộ {len(inv)} sản phẩm đồng bộ chính xác"
    run_test("TC25", "Xem toàn bộ tồn kho 100 sản phẩm (GET /api/inventory)", tc25)

if __name__ == "__main__":
    start_time = time.time()
    print(f"\n{Colors.BOLD}{Colors.YELLOW}{'#' * 75}")
    print("  BỘ KIỂM THỬ TOÀN DIỆN HỆ THỐNG QUẢN LÝ KHO HÀNG THÔNG MINH (ĐỀ TÀI 22)")
    print(f"  Target API: {BASE_URL}")
    print(f"{'#' * 75}{Colors.RESET}")

    tokens = test_authentication_rbac()
    duplicated_txn_id = test_import_export_lifecycle(tokens)
    test_idempotency(tokens, duplicated_txn_id)
    test_error_and_edge_cases(tokens)
    test_queries_and_reconciliation()

    elapsed = round(time.time() - start_time, 2)
    print("\n" + "=" * 75)
    print(f"{Colors.BOLD}TỔNG KẾT KIỂM THỬ HỆ THỐNG:")
    print(f"  - Tổng số ca kiểm thử: 25")
    print(f"  - {Colors.GREEN}Thành công (PASS): {total_passed}{Colors.RESET}")
    print(f"  - {Colors.RED}Thất bại   (FAIL): {total_failed}{Colors.RESET}")
    print(f"  - Thời gian thực thi : {elapsed}s")
    if total_failed == 0:
        print(f"\n{Colors.BOLD}{Colors.GREEN}>>> TẤT CẢ CHỨC NĂNG ĐỀU HOẠT ĐỘNG HOÀN HẢO 100%! <<<{Colors.RESET}")
    print("=" * 75 + "\n")
