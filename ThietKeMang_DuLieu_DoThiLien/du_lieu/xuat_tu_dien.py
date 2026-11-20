"""
Đề tài 22 - SV1: Kiểm tra từ điển dữ liệu khớp với schema.sql rồi xuất bản Markdown.

- Nguồn duy nhất của từ điển: TuDienDuLieu.csv
- So từng bảng/trường trong CSV với cấu trúc thật của CSDL (PRAGMA table_info)
  để chắc chắn tài liệu không lệch với schema.
- Xuất ../06_TuDienDuLieu.md

Chạy: python xuat_tu_dien.py
"""

import csv
import os
import sqlite3
import sys
from datetime import datetime

THU_MUC = os.path.dirname(os.path.abspath(__file__))
FILE_CSV = os.path.join(THU_MUC, "TuDienDuLieu.csv")
FILE_MD = os.path.join(os.path.dirname(THU_MUC), "06_TuDienDuLieu.md")
THU_TU = ["Products", "Inventory", "Transactions", "Users", "ScanPoints", "AuditLog"]


def doc_tu_dien():
    with open(FILE_CSV, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def cau_truc_schema():
    conn = sqlite3.connect(":memory:")
    with open(os.path.join(THU_MUC, "schema.sql"), encoding="utf-8") as f:
        conn.executescript(f.read())
    kq = {}
    for bang in THU_TU:
        kq[bang] = {r[1]: (r[2], bool(r[3]), bool(r[5])) for r in conn.execute(f"PRAGMA table_info({bang})")}
    return kq


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    td = doc_tu_dien()
    sc = cau_truc_schema()

    loi = []
    for bang in THU_TU:
        trong_td = [r["Trường"] for r in td if r["Bảng"] == bang]
        for truong in sc[bang]:
            if truong not in trong_td:
                loi.append(f"{bang}.{truong}: có trong schema nhưng thiếu trong từ điển")
        for r in (r for r in td if r["Bảng"] == bang):
            if r["Trường"] not in sc[bang]:
                loi.append(f"{bang}.{r['Trường']}: có trong từ điển nhưng không có trong schema")
            elif sc[bang][r["Trường"]][0] != r["Kiểu SQLite"]:
                loi.append(f"{bang}.{r['Trường']}: kiểu {r['Kiểu SQLite']} ≠ schema {sc[bang][r['Trường']][0]}")
            elif ("PK" in r["Khóa"]) != sc[bang][r["Trường"]][2]:
                loi.append(f"{bang}.{r['Trường']}: cột Khóa không khớp PRIMARY KEY trong schema")

    so_truong = sum(len(v) for v in sc.values())
    print(f"Đã so {len(td)} dòng từ điển với {so_truong} cột trong schema.sql")
    if loi:
        print("LỆCH:")
        for x in loi:
            print("  -", x)
        return 1
    print("KHỚP 100%: tên trường, kiểu dữ liệu và khóa chính")

    dong = [
        "# Từ điển dữ liệu – Đề tài 22 (SV1)",
        "",
        f"Sinh tự động từ `du_lieu/TuDienDuLieu.csv` lúc {datetime.now():%Y-%m-%d %H:%M}. "
        f"Đã kiểm tra khớp với `schema.sql`: {so_truong} cột, 6 bảng.",
        "",
        "Quy ước: **tên trường trong CSDL = tên khóa JSON trong API** (snake_case, tiếng Anh, không dấu). "
        "SV2 và SV3 dùng đúng các tên này; muốn đổi phải ghi vào `doi_chieu/NhatKyThayDoi.md`.",
        "",
    ]
    mo_ta = {
        "Products": "Danh mục hàng hóa",
        "Inventory": "Tồn kho hiện tại – quan hệ 1–1 với Products",
        "Transactions": "Lịch sử nhập/xuất – chỉ thêm, trigger chặn sửa/xóa",
        "Users": "Tài khoản và vai trò",
        "ScanPoints": "Điểm quét mã",
        "AuditLog": "Nhật ký mọi yêu cầu (bảng bổ sung, không bắt buộc theo đề)",
    }
    for i, bang in enumerate(THU_TU, 1):
        dong += [f"## {i}. {bang} – {mo_ta[bang]}", "",
                 "| Trường | Kiểu SQLite | Kiểu JSON | Bắt buộc | Khóa | Ràng buộc / mặc định | Ý nghĩa | Ví dụ |",
                 "|---|---|---|---|---|---|---|---|"]
        for r in (r for r in td if r["Bảng"] == bang):
            dong.append("| `{}` | {} | {} | {} | {} | {} | {} | {} |".format(
                r["Trường"], r["Kiểu SQLite"], r["Kiểu JSON"], r["Bắt buộc"], r["Khóa"],
                r["Ràng buộc / mặc định"].replace("|", "\\|"), r["Ý nghĩa"], r["Ví dụ"]))
        dong.append("")
    dong += [
        "## Quan hệ giữa các bảng",
        "",
        "| Quan hệ | Kiểu | Giải thích |",
        "|---|---|---|",
        "| Products → Inventory | 1 – 1 | Mỗi mã hàng có đúng một dòng tồn hiện tại |",
        "| Products → Transactions | 1 – N | Một mã hàng xuất hiện trong nhiều giao dịch nhập/xuất |",
        "| Users → Transactions | 1 – N | Một người thực hiện nhiều giao dịch; mỗi giao dịch ghi rõ người làm |",
        "| ScanPoints → Transactions | 1 – N | Một điểm quét gửi nhiều giao dịch; biết giao dịch đến từ đâu |",
        "| Transactions ··· AuditLog | logic qua txn_id | Không khóa ngoại vì AuditLog ghi cả yêu cầu bị từ chối/trùng |",
        "",
        "Bất biến đối chiếu: `Inventory.quantity = Σ quantity(NHAP) − Σ quantity(XUAT)` theo từng mã hàng "
        "(view `v_doi_chieu_ton`, cột `chenh_lech` phải bằng 0).",
        "",
    ]
    with open(FILE_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(dong))
    print(f"Đã xuất {os.path.basename(FILE_MD)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
