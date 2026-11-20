"""
Đề tài 22 - SV1: Kiểm chứng mô hình dữ liệu và quy tắc giao dịch.

Script này KHÔNG phải máy chủ hoàn chỉnh (phần của SV3). Nó dựng CSDL từ
schema.sql + seed_data.sql, cài một hàm ghi_giao_dich() tham chiếu đúng
quy tắc R1-R10 trong tài liệu thiết kế, rồi chạy các tình huống để chứng
minh thiết kế dữ liệu chặn được: trùng mã giao dịch, tồn âm, mã hàng sai,
số lượng sai, tài khoản chỉ xem ghi dữ liệu, sửa/xóa lịch sử, và hai điểm
quét ghi đồng thời.

Chạy:  python kiem_tra_thiet_ke.py
Kết quả: in ra màn hình và ghi vào ketqua_kiemtra.txt (có dấu thời gian).
Yêu cầu: Python 3.8+ (chỉ dùng thư viện chuẩn).
"""

import os
import sqlite3
import sys
import threading
from datetime import datetime

THU_MUC = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(THU_MUC, "kho_kiemtra.db")
FILE_KET_QUA = os.path.join(THU_MUC, "ketqua_kiemtra.txt")

QUYEN_GHI = {"ADMIN", "THUKHO", "NHANVIEN"}   # QUANLY chỉ được đọc
SL_TOI_DA = 10000

dong_ket_qua = []


def ghi_log(noi_dung=""):
    print(noi_dung)
    dong_ket_qua.append(noi_dung)


def bay_gio():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def ket_noi():
    conn = sqlite3.connect(DB_FILE, timeout=10, isolation_level=None)  # tự quản lý BEGIN/COMMIT
    conn.execute("PRAGMA foreign_keys = ON")
    conn.execute("PRAGMA busy_timeout = 10000")
    return conn


def tao_csdl():
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    conn = ket_noi()
    conn.execute("PRAGMA journal_mode = WAL")   # cho phép đọc trong lúc đang ghi
    for ten in ("schema.sql", "seed_data.sql"):
        with open(os.path.join(THU_MUC, ten), encoding="utf-8") as f:
            conn.executescript(f.read())
    conn.close()


def audit(conn, gd, ket_qua, ma_loi=None, chi_tiet=None):
    conn.execute(
        "INSERT INTO AuditLog (username, scan_point_id, txn_id, action, result, error_code, detail) "
        "VALUES (?,?,?,?,?,?,?)",
        (gd.get("username"), gd.get("scan_point_id"), gd.get("txn_id"),
         "WRITE_TXN", ket_qua, ma_loi, chi_tiet),
    )


def ghi_giao_dich(conn, gd):
    """Hàm tham chiếu cho máy chủ: kiểm tra -> lưu giao dịch -> cập nhật tồn -> trả kết quả.
    Toàn bộ nằm trong MỘT giao dịch CSDL (BEGIN IMMEDIATE ... COMMIT) nên
    hoặc cả Transactions và Inventory cùng đổi, hoặc không đổi gì (R7)."""
    conn.execute("BEGIN IMMEDIATE")   # khóa ghi: hai điểm quét không chen ngang nhau
    try:
        # R5 - tài khoản tồn tại, đang hoạt động, có quyền ghi
        u = conn.execute("SELECT role, is_active FROM Users WHERE username=?",
                         (gd["username"],)).fetchone()
        if not u or not u[1]:
            return _tu_choi(conn, gd, "UNAUTHORIZED", "Tài khoản không tồn tại hoặc bị khóa")
        if u[0] not in QUYEN_GHI:
            return _tu_choi(conn, gd, "FORBIDDEN", f"Vai trò {u[0]} chỉ được xem")

        # R6 - điểm quét hợp lệ
        sp = conn.execute("SELECT is_active FROM ScanPoints WHERE scan_point_id=?",
                          (gd["scan_point_id"],)).fetchone()
        if not sp or not sp[0]:
            return _tu_choi(conn, gd, "INVALID_SCAN_POINT", "Điểm quét không hợp lệ")

        # R3 - loại và số lượng
        if gd["txn_type"] not in ("NHAP", "XUAT"):
            return _tu_choi(conn, gd, "INVALID_TYPE", "Loại giao dịch phải là NHAP/XUAT")
        sl = gd["quantity"]
        if not isinstance(sl, int) or isinstance(sl, bool) or sl <= 0 or sl > SL_TOI_DA:
            return _tu_choi(conn, gd, "INVALID_QUANTITY", f"Số lượng phải là số nguyên 1..{SL_TOI_DA}")

        # R1 - trùng mã giao dịch: không áp dụng lần hai, trả lại kết quả lần đầu
        cu = conn.execute("SELECT stock_after FROM Transactions WHERE txn_id=?",
                          (gd["txn_id"],)).fetchone()
        if cu:
            return _tu_choi(conn, gd, "DUPLICATE_TXN",
                            f"Mã giao dịch đã được ghi trước đó (tồn khi ấy = {cu[0]})")

        # R2 - mã hàng tồn tại và đang kinh doanh
        p = conn.execute("SELECT is_active FROM Products WHERE product_code=?",
                         (gd["product_code"],)).fetchone()
        if not p or not p[0]:
            return _tu_choi(conn, gd, "PRODUCT_NOT_FOUND", "Mã hàng không có trong danh mục")

        # R4 - xuất không vượt tồn
        ton = conn.execute("SELECT quantity FROM Inventory WHERE product_code=?",
                           (gd["product_code"],)).fetchone()[0]
        ton_moi = ton + sl if gd["txn_type"] == "NHAP" else ton - sl
        if ton_moi < 0:
            return _tu_choi(conn, gd, "INSUFFICIENT_STOCK", f"Tồn {ton}, không đủ xuất {sl}")

        # R7 - lưu giao dịch + cập nhật tồn trong cùng một giao dịch CSDL
        conn.execute(
            "INSERT INTO Transactions (txn_id, product_code, txn_type, quantity, username, "
            "scan_point_id, client_time, server_time, stock_after) VALUES (?,?,?,?,?,?,?,?,?)",
            (gd["txn_id"], gd["product_code"], gd["txn_type"], sl, gd["username"],
             gd["scan_point_id"], gd["client_time"], bay_gio(), ton_moi),
        )
        conn.execute("UPDATE Inventory SET quantity=?, last_txn_id=?, updated_at=? WHERE product_code=?",
                     (ton_moi, gd["txn_id"], bay_gio(), gd["product_code"]))
        audit(conn, gd, "OK")
        conn.execute("COMMIT")          # R9 - chỉ báo thành công SAU khi COMMIT
        return {"status": "OK", "txn_id": gd["txn_id"], "stock_after": ton_moi}
    except sqlite3.IntegrityError as e:
        # Lớp chặn cuối của CSDL (PRIMARY KEY, CHECK, FOREIGN KEY)
        conn.execute("ROLLBACK")
        ma = "DUPLICATE_TXN" if "Transactions.txn_id" in str(e) else "DB_CONSTRAINT"
        conn.execute("BEGIN")
        audit(conn, gd, "REJECTED", ma, str(e))
        conn.execute("COMMIT")
        return {"status": "REJECTED", "error_code": ma, "message": str(e)}
    except Exception:
        conn.execute("ROLLBACK")
        raise


def _tu_choi(conn, gd, ma_loi, thong_diep):
    audit(conn, gd, "REJECTED", ma_loi, thong_diep)
    conn.execute("COMMIT")   # chỉ lưu dòng AuditLog, không động tới Transactions/Inventory
    return {"status": "REJECTED", "error_code": ma_loi, "message": thong_diep}


def ton(conn, ma):
    return conn.execute("SELECT quantity FROM Inventory WHERE product_code=?", (ma,)).fetchone()[0]


def so_gd(conn):
    return conn.execute("SELECT COUNT(*) FROM Transactions").fetchone()[0]


def giao_dich(txn_id, ma, loai, sl, user, diem):
    return {"txn_id": txn_id, "product_code": ma, "txn_type": loai, "quantity": sl,
            "username": user, "scan_point_id": diem, "client_time": bay_gio()}


ket_qua_tc = []


def kiem_tra(ma_tc, mo_ta, dieu_kien, chi_tiet):
    dat = "ĐẠT" if dieu_kien else "CHƯA ĐẠT"
    ket_qua_tc.append((ma_tc, dat))
    ghi_log(f"[{bay_gio()}] {ma_tc} | {mo_ta}")
    ghi_log(f"      -> {chi_tiet}")
    ghi_log(f"      => {dat}")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ghi_log("=" * 78)
    ghi_log("ĐỀ TÀI 22 - SV1 - KIỂM CHỨNG MÔ HÌNH DỮ LIỆU VÀ QUY TẮC GIAO DỊCH")
    ghi_log(f"Thời điểm chạy : {bay_gio()}")
    ghi_log(f"Python {sys.version.split()[0]} | SQLite {sqlite3.sqlite_version}")
    ghi_log("=" * 78)

    tao_csdl()
    conn = ket_noi()
    bang = [r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    ghi_log(f"Đã tạo các bảng: {', '.join(bang)}")
    ghi_log("Tồn đầu kỳ: " + ", ".join(f"{m}={q}" for m, q in conn.execute(
        "SELECT product_code, quantity FROM Inventory ORDER BY product_code")))
    ghi_log("-" * 78)

    # TC01 - giao dịch nhập hợp lệ tại SP01
    r = ghi_giao_dich(conn, giao_dich("SP01-20261026-0001", "SP001", "NHAP", 20, "nv01", "SP01"))
    kiem_tra("TC01", "SP01/nv01 NHAP 20 SP001 (tồn 100)",
             r["status"] == "OK" and ton(conn, "SP001") == 120, f"{r} ; tồn SP001 = {ton(conn, 'SP001')}")

    # TC02 - giao dịch xuất hợp lệ tại SP02
    r = ghi_giao_dich(conn, giao_dich("SP02-20261026-0001", "SP001", "XUAT", 30, "nv02", "SP02"))
    kiem_tra("TC02", "SP02/nv02 XUAT 30 SP001 (tồn 120)",
             r["status"] == "OK" and ton(conn, "SP001") == 90, f"{r} ; tồn SP001 = {ton(conn, 'SP001')}")

    # TC03 - gửi lại đúng giao dịch TC02 (mô phỏng máy khách gửi lại sau khi mất phản hồi)
    truoc, n_truoc = ton(conn, "SP001"), so_gd(conn)
    r = ghi_giao_dich(conn, giao_dich("SP02-20261026-0001", "SP001", "XUAT", 30, "nv02", "SP02"))
    kiem_tra("TC03", "Gửi trùng txn_id SP02-20261026-0001",
             r["error_code"] == "DUPLICATE_TXN" and ton(conn, "SP001") == truoc and so_gd(conn) == n_truoc,
             f"{r['error_code']} ; tồn {truoc} -> {ton(conn, 'SP001')} ; số giao dịch {n_truoc} -> {so_gd(conn)}")

    # TC04 - xuất vượt tồn
    r = ghi_giao_dich(conn, giao_dich("SP02-20261026-0002", "SP002", "XUAT", 51, "nv02", "SP02"))
    kiem_tra("TC04", "XUAT 51 SP002 khi tồn 50",
             r["error_code"] == "INSUFFICIENT_STOCK" and ton(conn, "SP002") == 50,
             f"{r['error_code']} ; tồn SP002 = {ton(conn, 'SP002')}")

    # TC05 - mã hàng không tồn tại
    r = ghi_giao_dich(conn, giao_dich("SP01-20261026-0002", "SP999", "NHAP", 5, "nv01", "SP01"))
    kiem_tra("TC05", "NHAP mã hàng SP999 (không có)", r["error_code"] == "PRODUCT_NOT_FOUND", r["error_code"])

    # TC06 - số lượng không hợp lệ
    r1 = ghi_giao_dich(conn, giao_dich("SP01-20261026-0003", "SP003", "NHAP", 0, "nv01", "SP01"))
    r2 = ghi_giao_dich(conn, giao_dich("SP01-20261026-0004", "SP003", "NHAP", -5, "nv01", "SP01"))
    kiem_tra("TC06", "Số lượng 0 và -5",
             r1["error_code"] == r2["error_code"] == "INVALID_QUANTITY" and ton(conn, "SP003") == 200,
             f"{r1['error_code']}, {r2['error_code']} ; tồn SP003 = {ton(conn, 'SP003')}")

    # TC07 - tài khoản chỉ xem cố ghi
    r = ghi_giao_dich(conn, giao_dich("SP01-20261026-0005", "SP001", "NHAP", 10, "quanly01", "SP01"))
    kiem_tra("TC07", "quanly01 (QUANLY) cố NHAP", r["error_code"] == "FORBIDDEN" and ton(conn, "SP001") == 90,
             f"{r['error_code']} ; tồn SP001 = {ton(conn, 'SP001')}")

    # TC08 - sửa/xóa trực tiếp lịch sử giao dịch bị CSDL chặn
    loi = []
    for sql in ("UPDATE Transactions SET quantity=1 WHERE txn_id='SP01-20261026-0001'",
                "DELETE FROM Transactions WHERE txn_id='SP01-20261026-0001'"):
        try:
            conn.execute(sql)
            loi.append("KHÔNG bị chặn")
        except sqlite3.DatabaseError as e:
            loi.append(str(e))
    kiem_tra("TC08", "UPDATE/DELETE trực tiếp bảng Transactions",
             all("chi them" in x for x in loi), " | ".join(loi))

    # TC09 - ghi tồn âm trực tiếp bị CHECK chặn
    try:
        conn.execute("UPDATE Inventory SET quantity=-1 WHERE product_code='SP005'")
        kq = "KHÔNG bị chặn"
    except sqlite3.IntegrityError as e:
        kq = str(e)
    kiem_tra("TC09", "UPDATE Inventory quantity = -1", "CHECK" in kq, kq)

    # TC10 - hai điểm quét ghi đồng thời cùng một mã hàng
    ton_dau = ton(conn, "SP004")
    so_lan = 50

    def diem_quet(diem, user, loai):
        c = ket_noi()
        for i in range(1, so_lan + 1):
            ghi_giao_dich(c, giao_dich(f"{diem}-20261026-{1000 + i:04d}", "SP004", loai, 1, user, diem))
        c.close()

    t1 = threading.Thread(target=diem_quet, args=("SP01", "nv01", "NHAP"))
    t2 = threading.Thread(target=diem_quet, args=("SP02", "nv02", "XUAT"))
    bd = datetime.now()
    t1.start(); t2.start(); t1.join(); t2.join()
    ms = (datetime.now() - bd).total_seconds() * 1000
    kiem_tra("TC10", f"SP01 NHAP {so_lan}x1 và SP02 XUAT {so_lan}x1 SP004 chạy song song",
             ton(conn, "SP004") == ton_dau,
             f"tồn SP004 {ton_dau} -> {ton(conn, 'SP004')} (kỳ vọng {ton_dau}); "
             f"{2 * so_lan} giao dịch trong {ms:.0f} ms ≈ {2 * so_lan / (ms / 1000):.0f} giao dịch/giây")

    # TC11 - đối chiếu tồn lưu trữ với tồn tính lại từ lịch sử
    lech = conn.execute("SELECT product_code, ton_luu_tru, ton_tinh_lai, chenh_lech "
                        "FROM v_doi_chieu_ton ORDER BY product_code").fetchall()
    kiem_tra("TC11", "Đối chiếu Inventory với Σ NHAP - Σ XUAT (view v_doi_chieu_ton)",
             all(r[3] == 0 for r in lech),
             "; ".join(f"{m}: lưu={a}, tính={b}, lệch={c}" for m, a, b, c in lech))

    ghi_log("-" * 78)
    tong = conn.execute("SELECT result, COUNT(*) FROM AuditLog GROUP BY result ORDER BY result").fetchall()
    ghi_log("AuditLog: " + ", ".join(f"{k}={v}" for k, v in tong))
    ghi_log("Mã lỗi đã ghi nhận: " + ", ".join(f"{k}={v}" for k, v in conn.execute(
        "SELECT error_code, COUNT(*) FROM AuditLog WHERE error_code IS NOT NULL "
        "GROUP BY error_code ORDER BY error_code")))
    so_dat = sum(1 for _, d in ket_qua_tc if d == "ĐẠT")
    ghi_log(f"TỔNG KẾT: {so_dat}/{len(ket_qua_tc)} tình huống ĐẠT")
    ghi_log("=" * 78)
    conn.close()

    with open(FILE_KET_QUA, "w", encoding="utf-8") as f:
        f.write("\n".join(dong_ket_qua) + "\n")
    return 0 if so_dat == len(ket_qua_tc) else 1


if __name__ == "__main__":
    sys.exit(main())
