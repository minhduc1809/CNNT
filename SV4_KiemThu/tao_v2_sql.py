# -*- coding: utf-8 -*-
"""
tao_v2_sql.py (SV4) - Tao BAN SAO cua cac file SQL cua SV3, doi ten CSDL thanh smart_warehouse_v2.

Muc dich: thu ban cap nhat cua SV3 (dang nhap co mat khau) tren CSDL RIENG,
KHONG dung vao CSDL smart_warehouse dang giu minh chung V5.
Chi DOC cac file SQL goc; chi GHI mot file moi trong SV4_KiemThu.

Chay tai thu muc goc cua repo da gop (noi co thu muc SV3_MayChu_CSDL_API):
    python SV4_KiemThu\\tao_v2_sql.py
Ket qua: SV4_KiemThu\\smart_warehouse_v2_all.sql  (mo bang MySQL Workbench roi chay ca file).
"""
import os
import re
import sys

TEN_CU = "smart_warehouse"
TEN_MOI = "smart_warehouse_v2"
THU_TU = [
    "01_create_database.sql",
    "02_insert_sample_data.sql",
    "03_create_procedure.sql",
    "04_create_permissions.sql",
    "06_sync_sv1_sv3_aliases.sql",
]


def main():
    goc = sys.argv[1] if len(sys.argv) > 1 else os.getcwd()
    thu_muc_sql = os.path.join(goc, "SV3_MayChu_CSDL_API", "01_CSDL_SQL")
    if not os.path.isdir(thu_muc_sql):
        print("Khong thay", thu_muc_sql, "- hay chay lenh tai thu muc goc cua repo.")
        return 1

    mau = re.compile(r"(?<![A-Za-z0-9_])" + TEN_CU + r"(?![A-Za-z0-9_])")
    phan = [
        "-- smart_warehouse_v2_all.sql: tao boi tao_v2_sql.py (SV4). CSDL thu rieng, khong phai CSDL chinh.",
        "DROP DATABASE IF EXISTS %s;" % TEN_MOI,
        "",
    ]
    for ten in THU_TU:
        duong_dan = os.path.join(thu_muc_sql, ten)
        if not os.path.isfile(duong_dan):
            print("Thieu file:", duong_dan)
            return 1
        with open(duong_dan, "r", encoding="utf-8-sig") as f:
            noi_dung = f.read()
        moi, so_lan = mau.subn(TEN_MOI, noi_dung)
        print("%-32s doi ten %d cho" % (ten, so_lan))
        phan.append("-- ===== %s =====" % ten)
        phan.append(moi)
        phan.append("")
    ket_qua = "\n".join(phan)

    # Kiem tra an toan: khong con ten CSDL cu nao (ngoai DROP/ten moi)
    con_lai = [d for d in mau.findall(ket_qua)]
    if con_lai:
        print("LOI: van con ten CSDL cu trong file ket qua. Khong ghi file.")
        return 1

    ra_dir = os.path.join(goc, "SV4_KiemThu")
    os.makedirs(ra_dir, exist_ok=True)
    ra = os.path.join(ra_dir, "smart_warehouse_v2_all.sql")
    with open(ra, "w", encoding="utf-8", newline="\n") as f:
        f.write(ket_qua)
    print("\nDa ghi:", ra)
    print("Kiem tra: khong con 'USE %s;' hay '%s.' trong file." % (TEN_CU, TEN_CU))
    return 0


if __name__ == "__main__":
    sys.exit(main())
