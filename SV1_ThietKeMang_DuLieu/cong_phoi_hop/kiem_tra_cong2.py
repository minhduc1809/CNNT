"""
Đề tài 22 - SV1-08: Kiểm tra CỔNG 2 - chuỗi GỬI -> LƯU -> ĐỌC LẠI giữa điểm quét và máy chủ.

Chạy với máy chủ của SV3 (hoặc máy chủ giả lập cong_cu_thu/may_chu_gia_lap.py):
    python kiem_tra_cong2.py [--url http://127.0.0.1:8080] [--mk Kho@2026]

Mỗi bước in dấu thời gian, yêu cầu, phản hồi và ĐẠT/CHƯA ĐẠT; kết quả ghi vào
ket_qua/ketqua_cong2_<thời điểm>.md để dán vào biên bản Cổng 2.
Chỉ dùng thư viện chuẩn Python 3.8+.
"""

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime

THU_MUC = os.path.dirname(os.path.abspath(__file__))
ket_qua = []


def bay_gio():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def goi(url, phuong_thuc, duong, token=None, body=None):
    req = urllib.request.Request(url + duong, method=phuong_thuc,
                                 data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except ValueError:
            return e.code, {}
    except (urllib.error.URLError, TimeoutError) as e:
        return 0, {"error": str(e)}


def buoc(ma, mo_ta, dat, chi_tiet):
    kq = "ĐẠT" if dat else "CHƯA ĐẠT"
    ket_qua.append((ma, bay_gio(), mo_ta, chi_tiet, kq))
    print(f"[{bay_gio()}] {ma} {mo_ta}\n      {chi_tiet}\n      => {kq}")
    return dat


def dang_nhap(url, user, mk):
    ma, r = goi(url, "POST", "/api/login", body={"username": user, "password": mk})
    return ma, r, r.get("token")


def ton(url, token, ma_hang):
    ma, r = goi(url, "GET", f"/api/inventory/{ma_hang}", token)
    return r.get("quantity") if ma == 200 else None, r


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Kiểm tra Cổng 2: gửi -> lưu -> đọc lại")
    ap.add_argument("--url", default="http://127.0.0.1:8080")
    ap.add_argument("--mk", default="Kho@2026", help="mật khẩu tài khoản mẫu")
    a = ap.parse_args()
    url = a.url.rstrip("/")
    ngay = datetime.now().strftime("%Y%m%d")
    stt = (datetime.now().hour * 3600 + datetime.now().minute * 60 + datetime.now().second) % 9000 + 1000
    id1, id2 = f"SP01-{ngay}-{stt:04d}", f"SP02-{ngay}-{stt:04d}"

    print("=" * 78)
    print(f"CỔNG 2 - KIỂM TRA CHUỖI GỬI -> LƯU -> ĐỌC LẠI   máy chủ: {url}   lúc {bay_gio()}")
    print("=" * 78)

    ma, r, tk1 = dang_nhap(url, "nv01", a.mk)
    if not buoc("C2-01", "nv01 đăng nhập tại SP01", ma == 200 and tk1 and r.get("role") == "NHANVIEN",
                f"HTTP {ma}, role={r.get('role')}"):
        return ket_thuc(url, 2)

    q0, _ = ton(url, tk1, "SP001")
    buoc("C2-02", "Đọc tồn SP001 trước khi gửi", q0 is not None, f"tồn = {q0}")

    gui = {"txn_id": id1, "product_code": "SP001", "txn_type": "NHAP", "quantity": 5,
           "scan_point_id": "SP01", "client_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
    ma, r = goi(url, "POST", "/api/transactions", tk1, gui)
    buoc("C2-03", f"GỬI: SP01 NHAP 5 SP001, txn_id {id1}",
         ma == 201 and r.get("status") == "OK" and q0 is not None and r.get("stock_after") == q0 + 5,
         f"HTTP {ma}, stock_after={r.get('stock_after')}, server_time={r.get('server_time')}")

    ma, r = goi(url, "GET", f"/api/transactions/{id1}", tk1)
    lech = [k for k in gui if str(r.get(k)) != str(gui[k])]
    buoc("C2-04", "LƯU + ĐỌC LẠI: GET /api/transactions/{txn_id} khớp dữ liệu đã gửi",
         ma == 200 and not lech and r.get("username") == "nv01" and bool(r.get("server_time")),
         f"HTTP {ma}, trường lệch={lech or 'không'}, username={r.get('username')}, server_time={r.get('server_time')}")

    q1, r = ton(url, tk1, "SP001")
    buoc("C2-05", "Tồn SP001 sau giao dịch = tồn trước + 5, last_txn_id đúng",
         q0 is not None and q1 == q0 + 5 and r.get("last_txn_id") == id1, f"tồn {q0} -> {q1}, last_txn_id={r.get('last_txn_id')}")

    ma, r = goi(url, "POST", "/api/transactions", tk1, gui)
    q2, _ = ton(url, tk1, "SP001")
    buoc("C2-06", "Gửi lại CÙNG txn_id (mô phỏng mất phản hồi)", ma == 409 and r.get("error_code") == "DUPLICATE_TXN" and q2 == q1,
         f"HTTP {ma} {r.get('error_code')}, tồn {q1} -> {q2}")

    ma, r, tk2 = dang_nhap(url, "nv02", a.mk)
    gui2 = {"txn_id": id2, "product_code": "SP001", "txn_type": "XUAT", "quantity": 2,
            "scan_point_id": "SP02", "client_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
    ma, r = goi(url, "POST", "/api/transactions", tk2, gui2)
    buoc("C2-07", f"GỬI từ điểm quét thứ hai: SP02/nv02 XUAT 2 SP001, txn_id {id2}",
         ma == 201 and q2 is not None and r.get("stock_after") == q2 - 2, f"HTTP {ma}, stock_after={r.get('stock_after')}")

    ma, r, tk3 = dang_nhap(url, "thukho01", a.mk)
    ma, r = goi(url, "GET", f"/api/transactions?scan_point_id=SP02&product_code=SP001&limit=5", tk3)
    co = any(i.get("txn_id") == id2 and i.get("username") == "nv02" for i in r.get("items", []))
    buoc("C2-08", "ĐỌC LẠI lịch sử bằng tài khoản khác (thukho01), lọc SP02", ma == 200 and co,
         f"HTTP {ma}, thấy {id2} của nv02: {co}")

    ma, r, tk4 = dang_nhap(url, "quanly01", a.mk)
    gui3 = dict(gui, txn_id=f"SP01-{ngay}-{(stt + 1) % 10000:04d}")
    ma, r = goi(url, "POST", "/api/transactions", tk4, gui3)
    q3, _ = ton(url, tk1, "SP001")
    buoc("C2-09", "quanly01 (chỉ xem) cố ghi giao dịch", ma == 403 and q3 == q2 - 2, f"HTTP {ma} {r.get('error_code')}, tồn = {q3}")

    ma, r = goi(url, "GET", "/api/reconcile", tk3)
    buoc("C2-10", "Đối chiếu tồn lưu trữ với Σ NHAP − Σ XUAT", ma == 200 and r.get("all_match") is True,
         f"HTTP {ma}, all_match={r.get('all_match')}")
    return ket_thuc(url, 0)


def ket_thuc(url, ma_thoat):
    dat = sum(1 for x in ket_qua if x[4] == "ĐẠT")
    print("-" * 78)
    print(f"TỔNG KẾT CỔNG 2: {dat}/{len(ket_qua)} bước ĐẠT")
    os.makedirs(os.path.join(THU_MUC, "ket_qua"), exist_ok=True)
    ten = os.path.join(THU_MUC, "ket_qua", f"ketqua_cong2_{datetime.now():%Y%m%d_%H%M%S}.md")
    md = [f"# Kết quả kiểm tra Cổng 2 – {bay_gio()}", "", f"Máy chủ: `{url}` · Kết quả: **{dat}/{len(ket_qua)} bước ĐẠT**", "",
          "| Bước | Thời điểm | Nội dung | Thực tế | Kết quả |", "|---|---|---|---|---|"]
    md += [f"| {m} | {t} | {mo} | {ct.replace('|', '/')} | {k} |" for m, t, mo, ct, k in ket_qua]
    with open(ten, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"Đã ghi {os.path.relpath(ten, THU_MUC)}")
    return ma_thoat or (0 if dat == len(ket_qua) else 1)


if __name__ == "__main__":
    sys.exit(main())
