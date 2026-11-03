"""
Đề tài 22 - SV1: Đo dung lượng lưu trữ thực tế của một giao dịch.

Tạo CSDL từ schema.sql + seed_data.sql, chèn N giao dịch giả (kèm 1 dòng AuditLog
mỗi giao dịch, giống máy chủ thật), rồi đo kích thước file để suy ra byte/giao dịch.
Số liệu dùng cho mục "Ước lượng tài nguyên khi tăng gấp đôi điểm quét".

Chạy: python do_dung_luong.py [N]   (mặc định N = 100000)
"""

import os
import sqlite3
import sys
from datetime import datetime, timedelta

THU_MUC = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(THU_MUC, "kho_do_dung_luong.db")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100_000
    if os.path.exists(DB):
        os.remove(DB)
    conn = sqlite3.connect(DB)
    for ten in ("schema.sql", "seed_data.sql"):
        with open(os.path.join(THU_MUC, ten), encoding="utf-8") as f:
            conn.executescript(f.read())
    conn.commit()
    co_so = os.path.getsize(DB)

    t0 = datetime(2026, 10, 26, 8, 0, 0)
    ma_hang = ["SP001", "SP002", "SP003", "SP004", "SP005"]
    gd, nk = [], []
    for i in range(n):
        diem, user = ("SP01", "nv01") if i % 2 == 0 else ("SP02", "nv02")
        tg = (t0 + timedelta(seconds=3 * i)).strftime("%Y-%m-%dT%H:%M:%S")
        txn_id = f"{diem}-{tg[:10].replace('-', '')}-{i // 2 % 10000:04d}-{i}"
        gd.append((txn_id, ma_hang[i % 5], "NHAP", 1 + i % 50, user, diem, tg, tg, 100 + i % 900))
        nk.append((tg, user, diem, txn_id, "WRITE_TXN", "OK"))
    conn.executemany("INSERT INTO Transactions (txn_id, product_code, txn_type, quantity, username, "
                     "scan_point_id, client_time, server_time, stock_after) VALUES (?,?,?,?,?,?,?,?,?)", gd)
    conn.executemany("INSERT INTO AuditLog (log_time, username, scan_point_id, txn_id, action, result) "
                     "VALUES (?,?,?,?,?,?)", nk)
    conn.commit()
    conn.execute("VACUUM")
    conn.close()

    tong = os.path.getsize(DB)
    bpg = (tong - co_so) / n
    print(f"Thời điểm đo         : {datetime.now():%Y-%m-%d %H:%M:%S}")
    print(f"Số giao dịch chèn    : {n:,}")
    print(f"Kích thước CSDL      : {co_so:,} B (rỗng) -> {tong:,} B")
    print(f"Byte / giao dịch     : {bpg:.0f} B (gồm Transactions + 2 chỉ mục + 1 dòng AuditLog)")
    os.remove(DB)


if __name__ == "__main__":
    main()
