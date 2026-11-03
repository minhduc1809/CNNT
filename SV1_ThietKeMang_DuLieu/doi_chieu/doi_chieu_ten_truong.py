"""
Đề tài 22 - SV1: Đối chiếu tên trường trong mã của SV2 / SV3 với từ điển dữ liệu.

Cách làm:
  1. Đọc 38 trường chuẩn từ ../du_lieu/TuDienDuLieu.csv và các khóa JSON phụ của giao ước API.
  2. Quét mã nguồn (.py .js .ts .java .cs .sql .json .html) của SV2, SV3 để lấy các
     chuỗi trông giống tên trường (trong dấu nháy, hoặc tên cột trong CREATE TABLE).
  3. (Tùy chọn) đọc cấu trúc thật của file CSDL của SV3 bằng PRAGMA table_info.
  4. Phân loại: KHỚP (đúng tên chuẩn) · LỆCH (cùng nghĩa nhưng viết khác: txnId, qty,
     transaction_id...) · THIẾU (không thấy dùng).
  5. Ghi BangDoiChieuTenTruong.md có dấu thời gian.

Chạy:
  python doi_chieu_ten_truong.py --sv2 ../../SV2_DiemQuet --sv3 ../../SV3_LuuTru_Quyen_SaoLuu [--db ../../SV3_LuuTru_Quyen_SaoLuu/kho.db]
Trả mã thoát 1 nếu có LỆCH để dễ gắn vào quy trình kiểm tra.
"""

import argparse
import csv
import os
import re
import sqlite3
import sys
from datetime import datetime

THU_MUC = os.path.dirname(os.path.abspath(__file__))
FILE_TU_DIEN = os.path.join(THU_MUC, "..", "du_lieu", "TuDienDuLieu.csv")
FILE_KQ = os.path.join(THU_MUC, "BangDoiChieuTenTruong.md")
DUOI = (".py", ".js", ".ts", ".java", ".cs", ".sql", ".json", ".html")

# Khóa JSON của giao ước API không phải cột CSDL (05_GiaoUocAPI.md)
KHOA_API = ["status", "error_code", "message", "token", "role", "expires_in", "items", "count",
            "original", "all_match", "ton_luu_tru", "ton_tinh_lai", "chenh_lech", "password"]

# Cách viết sai hay gặp -> tên chuẩn
DONG_NGHIA = {
    "transaction_id": "txn_id", "transactionid": "txn_id", "trans_id": "txn_id", "tx_id": "txn_id", "ma_gd": "txn_id",
    "product_id": "product_code", "productid": "product_code", "item_code": "product_code", "barcode": "product_code",
    "sku": "product_code", "ma_hang": "product_code",
    "type": "txn_type", "transaction_type": "txn_type", "loai": "txn_type",
    "qty": "quantity", "amount": "quantity", "so_luong": "quantity",
    "user": "username", "user_name": "username", "user_id": "username", "nguoi_thuc_hien": "username",
    "scanpoint": "scan_point_id", "scan_point": "scan_point_id", "point_id": "scan_point_id",
    "scanner_id": "scan_point_id", "device_id": "scan_point_id", "diem_quet": "scan_point_id",
    "timestamp": "client_time", "scan_time": "client_time", "created_time": "client_time",
    "saved_time": "server_time", "server_timestamp": "server_time",
    "stock": "stock_after", "balance": "stock_after", "ton_sau": "stock_after",
    "name": None,  # có thật trong ScanPoints - không coi là lệch
}

RE_CHUOI = re.compile(r"""["']([A-Za-z_][A-Za-z0-9_]{1,40})["']""")
RE_COT_SQL = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s+(TEXT|INTEGER|INT|REAL|VARCHAR|CHAR|NUMERIC|DATETIME|BOOLEAN)",
                        re.IGNORECASE | re.MULTILINE)


def chuan_hoa(s):
    """txnId, TxnID, txn-id -> txnid để so cùng nghĩa khác cách viết."""
    return re.sub(r"[^a-z0-9]", "", s.lower())


def doc_chuan():
    with open(FILE_TU_DIEN, encoding="utf-8-sig", newline="") as f:
        td = list(csv.DictReader(f))
    truong = []
    for r in td:
        if r["Trường"] not in truong:
            truong.append(r["Trường"])
    return td, truong


def quet_ma(thu_muc):
    """Trả {tên: [file:dòng, ...]} cho mọi chuỗi/cột tìm thấy."""
    gap = {}
    if not thu_muc or not os.path.isdir(thu_muc):
        return gap
    for goc, _, files in os.walk(thu_muc):
        if any(x in goc for x in (os.sep + ".git", "node_modules", "__pycache__", os.sep + "venv")):
            continue
        for ten in files:
            if not ten.lower().endswith(DUOI):
                continue
            duong = os.path.join(goc, ten)
            try:
                with open(duong, encoding="utf-8", errors="replace") as f:
                    for so, dong in enumerate(f, 1):
                        tim = RE_CHUOI.findall(dong) + [m[0] for m in RE_COT_SQL.findall(dong)]
                        for t in tim:
                            gap.setdefault(t, []).append(f"{os.path.relpath(duong, thu_muc)}:{so}")
            except OSError:
                pass
    return gap


def cot_trong_db(db):
    if not db or not os.path.exists(db):
        return {}
    conn = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    kq = {}
    for (bang,) in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'"):
        for r in conn.execute(f"PRAGMA table_info({bang})"):
            kq.setdefault(r[1], []).append(f"{bang}.{r[1]}")
    conn.close()
    return kq


def phan_loai(chuan, gap):
    """Với mỗi tên chuẩn: tên đúng có dùng không, và các biến thể lệch tìm thấy."""
    khop, lech = {}, {}
    nhom = {chuan_hoa(c): c for c in chuan}
    for ten, noi in gap.items():
        if ten in chuan:
            khop.setdefault(ten, []).extend(noi)
            continue
        dich = None
        if chuan_hoa(ten) in nhom:                      # txnId, TXN_ID...
            dich = nhom[chuan_hoa(ten)]
        elif ten.lower() in DONG_NGHIA and DONG_NGHIA[ten.lower()]:
            dich = DONG_NGHIA[ten.lower()]
        if dich and dich in chuan:
            lech.setdefault(dich, []).append((ten, noi[:3]))
    return khop, lech


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Đối chiếu tên trường SV2/SV3 với từ điển dữ liệu")
    ap.add_argument("--sv2", help="Thư mục mã nguồn của SV2 (máy khách điểm quét)")
    ap.add_argument("--sv3", help="Thư mục mã nguồn của SV3 (máy chủ, CSDL)")
    ap.add_argument("--db", help="File SQLite của SV3 để đọc cấu trúc thật (tùy chọn)")
    ap.add_argument("--out", default=FILE_KQ, help="File kết quả Markdown")
    a = ap.parse_args()

    td, truong_csdl = doc_chuan()
    chuan = truong_csdl + KHOA_API
    # Trường máy khách cần dùng khi gửi giao dịch (SV2 thiếu là lỗi)
    can_sv2 = ["txn_id", "product_code", "txn_type", "quantity", "scan_point_id", "client_time",
               "status", "error_code", "stock_after", "token"]

    nguon = {"SV2": quet_ma(a.sv2), "SV3": quet_ma(a.sv3)}
    if a.db:
        for k, v in cot_trong_db(a.db).items():
            nguon["SV3"].setdefault(k, []).extend(["CSDL:" + x for x in v])
    kq = {k: phan_loai(chuan, v) for k, v in nguon.items()}

    bang_cua = {}
    for r in td:
        bang_cua.setdefault(r["Trường"], []).append(r["Bảng"])

    dong, so_lech = [], 0
    for ten in chuan:
        o = [f"`{ten}`", ", ".join(bang_cua.get(ten, ["(khóa API)"]))]
        trang_thai = []
        for sv in ("SV2", "SV3"):
            khop, lech = kq[sv]
            if not nguon[sv]:
                o.append("—")
                continue
            phan = []
            if ten in khop:
                phan.append("✔ dùng đúng")
            if ten in lech:
                phan.append("✘ " + ", ".join(f"`{t}` ({'; '.join(n)})" for t, n in lech[ten]))
                trang_thai.append("LỆCH")
            if not phan:
                phan.append("không thấy")
                if sv == "SV2" and ten in can_sv2:
                    trang_thai.append("THIẾU")
            o.append(" · ".join(phan))
        if not nguon["SV2"] and not nguon["SV3"]:
            kl = "Chờ mã SV2/SV3"
        else:
            kl = "LỆCH" if "LỆCH" in trang_thai else ("THIẾU" if "THIẾU" in trang_thai else "Khớp")
            so_lech += kl != "Khớp"
        o.append(kl)
        dong.append(o)

    md = [
        "# Bảng đối chiếu tên trường – Đề tài 22",
        "",
        f"- Thời điểm chạy: **{datetime.now():%Y-%m-%d %H:%M:%S}**",
        f"- Chuẩn: `du_lieu/TuDienDuLieu.csv` ({len(truong_csdl)} tên trường khác nhau, {len(td)} trường trong 6 bảng) + {len(KHOA_API)} khóa JSON của giao ước API",
        f"- Mã SV2: `{a.sv2 or '(chưa cung cấp)'}` · Mã SV3: `{a.sv3 or '(chưa cung cấp)'}` · CSDL SV3: `{a.db or '(không đọc)'}`",
        f"- Kết quả: **{len(chuan) - so_lech}/{len(chuan)} khớp**, {so_lech} cần xử lý",
        "",
        "| Tên chuẩn | Bảng | SV2 (điểm quét) | SV3 (máy chủ, CSDL) | Kết luận |",
        "|---|---|---|---|---|",
    ] + ["| " + " | ".join(o) + " |" for o in dong] + [
        "",
        "Cách xử lý khi có LỆCH/THIẾU: (1) bên viết mã sửa về tên chuẩn; hoặc (2) nếu nhóm thống nhất đổi chuẩn thì",
        "SV1 sửa `TuDienDuLieu.csv`, `schema.sql`, `05_GiaoUocAPI.md`, tăng phiên bản và ghi `NhatKyThayDoi.md`.",
        "Chạy lại script này đến khi không còn LỆCH.",
        "",
    ]
    with open(a.out, "w", encoding="utf-8") as f:
        f.write("\n".join(md))
    if not nguon["SV2"] and not nguon["SV3"]:
        md[5] = "- Kết quả: **chưa đối chiếu** – chưa có mã SV2/SV3 (bảng chuẩn sẵn sàng)"
        with open(a.out, "w", encoding="utf-8") as f:
            f.write("\n".join(md))
        print(f"Chưa có mã SV2/SV3 - đã xuất bảng chuẩn {len(chuan)} tên -> {os.path.basename(a.out)}")
        return 0
    print(f"{len(chuan) - so_lech}/{len(chuan)} khớp, {so_lech} cần xử lý -> {os.path.basename(a.out)}")
    return 1 if so_lech else 0


if __name__ == "__main__":
    sys.exit(main())
