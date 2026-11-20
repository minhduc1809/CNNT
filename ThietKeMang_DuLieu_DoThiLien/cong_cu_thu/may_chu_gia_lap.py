"""
Đề tài 22 - SV1: MÁY CHỦ GIẢ LẬP theo giao ước API v1.0 (05_GiaoUocAPI.md).

MỤC ĐÍCH: công cụ để SV1 thử script Cổng 2 (kiem_tra_cong2.py) và script tải
(tai_thu.py) trước khi có máy chủ thật; SV2 cũng có thể dùng tạm để phát triển client.
KHÔNG phải sản phẩm của SV3 và không nộp thay phần việc của SV3.

Dùng lại hàm ghi_giao_dich() tham chiếu trong du_lieu/kiem_tra_thiet_ke.py (đã kiểm chứng 11/11).
Chỉ dùng thư viện chuẩn Python 3.8+.

Chạy:  python may_chu_gia_lap.py [--port 8080] [--moi]
       --moi : tạo lại CSDL từ schema.sql + seed_data.sql + seed_mo_rong_4_diem.sql
"""

import argparse
import hashlib
import json
import os
import re
import secrets
import sqlite3
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

THU_MUC = os.path.dirname(os.path.abspath(__file__))
DU_LIEU = os.path.join(os.path.dirname(THU_MUC), "du_lieu")
sys.path.insert(0, DU_LIEU)
from kiem_tra_thiet_ke import ghi_giao_dich  # noqa: E402

DB = os.path.join(THU_MUC, "kho_gia_lap.db")
RE_TXN = re.compile(r"^SP\d{2}-\d{8}-\d{4}$")
BAT_BUOC = ["txn_id", "product_code", "txn_type", "quantity", "scan_point_id", "client_time"]
HTTP_CUA = {"OK": 201, "DUPLICATE_TXN": 409, "FORBIDDEN": 403, "UNAUTHORIZED": 401, "PRODUCT_NOT_FOUND": 404,
            "INSUFFICIENT_STOCK": 422, "INVALID_TYPE": 400, "INVALID_QUANTITY": 400, "INVALID_SCAN_POINT": 400,
            "INVALID_TXN_ID": 400, "INVALID_JSON": 400, "DB_CONSTRAINT": 400}
TOKENS = {}
KHOA_TOKEN = threading.Lock()
HAN_TOKEN = 8 * 3600


def ket_noi():
    conn = sqlite3.connect(DB, timeout=10, isolation_level=None)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


def tao_csdl(moi):
    if moi and os.path.exists(DB):
        for duoi in ("", "-wal", "-shm"):
            if os.path.exists(DB + duoi):
                os.remove(DB + duoi)
    if os.path.exists(DB):
        return
    conn = ket_noi()
    conn.execute("PRAGMA journal_mode = WAL")
    for ten in ("schema.sql", "seed_data.sql", "seed_mo_rong_4_diem.sql"):
        with open(os.path.join(DU_LIEU, ten), encoding="utf-8") as f:
            conn.executescript(f.read())
    conn.close()


def dung_mat_khau(luu, mk):
    try:
        _, salt, hx = luu.split("$")
    except ValueError:
        return False
    return hashlib.sha256(f"{salt}:{mk}".encode()).hexdigest() == hx


def dong(cur, row):
    return {d[0]: v for d, v in zip(cur.description, row)}


class XuLy(BaseHTTPRequestHandler):
    server_version = "KhoGiaLap/1.0"

    def log_message(self, *a):
        pass

    def tra(self, ma, obj):
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(ma)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def loi(self, ma_loi, thong_diep, http=None, **them):
        self.tra(http or HTTP_CUA.get(ma_loi, 400),
                 {"status": "REJECTED", "error_code": ma_loi, "message": thong_diep, **them})

    def doc_json(self):
        n = int(self.headers.get("Content-Length") or 0)
        try:
            return json.loads(self.rfile.read(n).decode("utf-8")) if n else None
        except (ValueError, UnicodeDecodeError):
            return None

    def nguoi_goi(self):
        h = self.headers.get("Authorization", "")
        if not h.startswith("Bearer "):
            return None
        with KHOA_TOKEN:
            t = TOKENS.get(h[7:])
        return t if t and t[2] > time.time() else None

    # ---------------- POST ----------------
    def do_POST(self):
        u = urlparse(self.path).path
        if u == "/api/login":
            return self.dang_nhap()
        if u == "/api/transactions":
            return self.ghi()
        self.loi("NOT_FOUND", "Không có API này", 404)

    def dang_nhap(self):
        b = self.doc_json() or {}
        conn = ket_noi()
        r = conn.execute("SELECT password_hash, role, is_active FROM Users WHERE username=?",
                         (b.get("username"),)).fetchone()
        conn.close()
        if not r or not r[2] or not dung_mat_khau(r[0], str(b.get("password", ""))):
            return self.loi("LOGIN_FAILED", "Sai tài khoản/mật khẩu hoặc tài khoản bị khóa", 401)
        tk = secrets.token_hex(16)
        with KHOA_TOKEN:
            TOKENS[tk] = (b["username"], r[1], time.time() + HAN_TOKEN)
        self.tra(200, {"status": "OK", "token": tk, "username": b["username"], "role": r[1], "expires_in": HAN_TOKEN})

    def ghi(self):
        ng = self.nguoi_goi()
        if not ng:
            return self.loi("UNAUTHORIZED", "Thiếu token, token sai hoặc hết hạn")
        b = self.doc_json()
        if not isinstance(b, dict) or any(k not in b for k in BAT_BUOC):
            return self.loi("INVALID_JSON", "Thân yêu cầu không phải JSON hoặc thiếu trường bắt buộc")
        if not RE_TXN.match(str(b["txn_id"])) or not str(b["txn_id"]).startswith(str(b["scan_point_id"]) + "-"):
            return self.loi("INVALID_TXN_ID", "txn_id sai định dạng SPxx-yyyymmdd-nnnn hoặc khác scan_point_id")
        gd = {k: b[k] for k in BAT_BUOC}
        gd["username"] = ng[0]            # người thực hiện lấy từ token, không tin thân yêu cầu
        conn = ket_noi()
        try:
            kq = ghi_giao_dich(conn, gd)
            if kq["status"] == "OK":
                row = conn.execute("SELECT product_code, stock_after, server_time FROM Transactions WHERE txn_id=?",
                                   (gd["txn_id"],)).fetchone()
                return self.tra(201, {"status": "OK", "txn_id": gd["txn_id"], "product_code": row[0],
                                      "stock_after": row[1], "server_time": row[2]})
            them = {}
            if kq["error_code"] == "DUPLICATE_TXN":
                row = conn.execute("SELECT stock_after, server_time FROM Transactions WHERE txn_id=?",
                                   (gd["txn_id"],)).fetchone()
                if row:
                    them["original"] = {"stock_after": row[0], "server_time": row[1]}
            return self.loi(kq["error_code"], kq["message"], **them)
        except Exception as e:  # lỗi CSDL bất ngờ: đã ROLLBACK trong ghi_giao_dich
            return self.loi("SERVER_ERROR", str(e), 500)
        finally:
            conn.close()

    # ---------------- GET ----------------
    def do_GET(self):
        p = urlparse(self.path)
        ng = self.nguoi_goi()
        if not ng:
            return self.loi("UNAUTHORIZED", "Thiếu token, token sai hoặc hết hạn")
        user, role, _ = ng
        q = {k: v[0] for k, v in parse_qs(p.query).items()}
        conn = ket_noi()
        try:
            if p.path == "/api/inventory" or p.path.startswith("/api/inventory/"):
                sql = ("SELECT p.product_code, p.product_name, p.unit, i.quantity, i.last_txn_id, i.updated_at "
                       "FROM Products p JOIN Inventory i ON i.product_code = p.product_code")
                if p.path.startswith("/api/inventory/"):
                    cur = conn.execute(sql + " WHERE p.product_code=?", (p.path.rsplit("/", 1)[1],))
                    r = cur.fetchone()
                    return self.tra(200, {"status": "OK", **dong(cur, r)}) if r else \
                        self.loi("PRODUCT_NOT_FOUND", "Mã hàng không có trong danh mục")
                cur = conn.execute(sql + " ORDER BY p.product_code")
                items = [dong(cur, r) for r in cur.fetchall()]
                return self.tra(200, {"status": "OK", "count": len(items), "items": items})

            if p.path.startswith("/api/transactions/"):
                cur = conn.execute("SELECT * FROM Transactions WHERE txn_id=?", (p.path.rsplit("/", 1)[1],))
                r = cur.fetchone()
                if not r or (role == "NHANVIEN" and dong(cur, r)["username"] != user):
                    return self.loi("TXN_NOT_FOUND", "Chưa có giao dịch này", 404)
                return self.tra(200, {"status": "OK", **dong(cur, r)})

            if p.path == "/api/transactions":
                dk, ts = [], []
                for k in ("product_code", "scan_point_id", "username"):
                    if q.get(k):
                        dk.append(f"{k}=?"); ts.append(q[k])
                if role == "NHANVIEN":
                    dk.append("username=?"); ts.append(user)
                if q.get("from"):
                    dk.append("server_time>=?"); ts.append(q["from"])
                if q.get("to"):
                    dk.append("server_time<=?"); ts.append(q["to"] + ("T23:59:59" if len(q["to"]) == 10 else ""))
                lim = min(int(q.get("limit", 100)), 1000)
                cur = conn.execute("SELECT * FROM Transactions" + (" WHERE " + " AND ".join(dk) if dk else "")
                                   + " ORDER BY server_time DESC, txn_id DESC LIMIT ?", (*ts, lim))
                items = [dong(cur, r) for r in cur.fetchall()]
                return self.tra(200, {"status": "OK", "count": len(items), "items": items})

            if p.path == "/api/reconcile":
                if role == "NHANVIEN":
                    return self.loi("FORBIDDEN", "Vai trò NHANVIEN không được đối chiếu")
                cur = conn.execute("SELECT * FROM v_doi_chieu_ton ORDER BY product_code")
                items = [dong(cur, r) for r in cur.fetchall()]
                return self.tra(200, {"status": "OK", "all_match": all(i["chenh_lech"] == 0 for i in items),
                                      "items": items})
            return self.loi("NOT_FOUND", "Không có API này", 404)
        finally:
            conn.close()


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Máy chủ giả lập API kho (công cụ thử của SV1)")
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--moi", action="store_true", help="tạo lại CSDL từ đầu")
    a = ap.parse_args()
    tao_csdl(a.moi)
    srv = ThreadingHTTPServer((a.host, a.port), XuLy)
    print(f"Máy chủ giả lập chạy tại http://{a.host}:{a.port}  (CSDL: {DB})  – Ctrl+C để dừng", flush=True)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
