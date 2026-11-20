"""
SV4 - Đối chiếu nhật ký điểm quét với CSDL máy chủ theo txn_id / seq_no (Đề tài 22, CV03).

Chỉ ĐỌC dữ liệu (queue_SP0x.jsonl của điểm quét và bảng MySQL), không ghi gì vào CSDL hay file của người khác.
Dùng tài khoản MySQL wh_store (chỉ có quyền SELECT) lấy từ config.json của máy chủ API.

Chạy tại thư mục CNNT (cmd):
  python SV4_KiemThu\\doi_chieu_sv4.py
Kết quả: thư mục SV4_KiemThu\\ket_qua_doi_chieu\\<ngày giờ>\\ gồm doi_chieu.md, client.csv, chi_co_tren_may_chu.csv, ton_kho.csv
Cần: pip install pymysql   (máy chủ API đã dùng sẵn)
"""
import argparse, csv, json, os, re, sys
from collections import defaultdict
from datetime import datetime

MAU_ID = re.compile(r"^(SP\d\d)-(\d{8})-(\d{4})$")


def doc_queue(thu_muc):
    kq = []
    for ten in sorted(os.listdir(thu_muc)):
        if not (ten.startswith("queue_") and ten.endswith(".jsonl")):
            continue
        with open(os.path.join(thu_muc, ten), encoding="utf-8") as f:
            for n, dong in enumerate(f, 1):
                dong = dong.strip()
                if not dong:
                    continue
                try:
                    o = json.loads(dong)
                except ValueError:
                    kq.append({"file": ten, "dong": n, "loi": "dòng không đọc được"}); continue
                p = o.get("payload", {})
                kq.append({"file": ten, "dong": n, "txn_id": p.get("txn_id"), "scan_point_id": p.get("scan_point_id"),
                           "product": p.get("product_code"), "loai": p.get("txn_type"), "sl": p.get("quantity"),
                           "trang_thai": o.get("status"), "retries": o.get("retries"), "ghi_chu": o.get("note"),
                           "tao_luc": o.get("created_at")})
    return kq


def doc_seed(duong_dan):
    try:
        s = open(duong_dan, encoding="utf-8").read()
        i = s.index("INSERT INTO Inventory")
        return {m: int(q) for m, q in re.findall(r"\('(SP\d+)',\s*(\d+)\)", s[i:i + 6000])}
    except Exception:
        return {}


def lay_du_lieu_mysql(cfg_path):
    import pymysql
    d = json.load(open(cfg_path, encoding="utf-8"))["database"]
    c = pymysql.connect(host=d["host"], port=d["port"], user=d["user"], password=d["password"],
                        database=d["database"], cursorclass=pymysql.cursors.DictCursor, charset="utf8mb4")
    with c.cursor() as cur:
        cur.execute("SELECT transaction_id, product_id, transaction_type, quantity, transaction_time, user_id, scan_point_id FROM warehouse_transactions")
        gd = cur.fetchall()
        cur.execute("SELECT product_id, quantity FROM Inventory")
        ton = {r["product_id"]: r["quantity"] for r in cur.fetchall()}
    c.close()
    return gd, ton


def phan_loai_client(c, trong_db):
    tt, co = c["trang_thai"], c["txn_id"] in trong_db
    if tt == "DA_XAC_NHAN":
        return "KHỚP" if co else "THIẾU TRÊN MÁY CHỦ"
    if tt == "TU_CHOI":
        return "XUNG ĐỘT (bị từ chối nhưng máy chủ có bản ghi)" if co else "KHỚP (từ chối đúng, không lưu)"
    if tt == "CHO_XAC_NHAN":
        return "ĐÃ LƯU Ở MÁY CHỦ, điểm quét chưa cập nhật" if co else "CÒN CHỜ GỬI"
    return "TRẠNG THÁI LẠ: " + str(tt)


def chay(a, gd=None, ton=None):
    queue = doc_queue(a.queue_dir)
    if gd is None:
        gd, ton = lay_du_lieu_mysql(a.config)
    seed = doc_seed(a.seed)
    db = {r["transaction_id"]: r for r in gd}
    gốc = datetime.now().strftime("%Y%m%d_%H%M%S")
    ra = os.path.join(a.ra, gốc); os.makedirs(ra, exist_ok=True)

    # A. client -> máy chủ
    for c in queue:
        if "loi" in c:
            c["ket_luan"] = c["loi"]; continue
        c["ket_luan"] = phan_loai_client(c, db)
        m = MAU_ID.match(c["txn_id"] or "")
        c["ngay_txn"] = m.group(2) if m else ""
        c["so_tt"] = int(m.group(3)) if m else ""
    hop = [c for c in queue if "loi" not in c]
    with open(os.path.join(ra, "client.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["file", "dong", "txn_id", "diem_quet", "ngay_txn", "so_tt", "mat_hang", "loai", "sl", "trang_thai_client", "so_lan_gui_lai", "ghi_chu", "ket_luan"])
        for c in hop:
            w.writerow([c["file"], c["dong"], c["txn_id"], c["scan_point_id"], c["ngay_txn"], c["so_tt"], c["product"], c["loai"], c["sl"], c["trang_thai"], c["retries"], c["ghi_chu"], c["ket_luan"]])

    # B. chỉ có trên máy chủ
    diem_client = {c["scan_point_id"] for c in hop}
    id_client = {c["txn_id"] for c in hop}
    chi_mc = []
    for tid, r in db.items():
        if r["scan_point_id"] in diem_client and tid not in id_client:
            m = MAU_ID.match(tid)
            if m and int(m.group(3)) >= 1000 and m.group(2) == a.ngay_tai:
                nhom = f"thử tải (tai_thu_sv4: ngày {a.ngay_tai}, số thứ tự từ 1001)"
            else:
                nhom = "khác (cần xem từng dòng)"
            chi_mc.append((tid, r["scan_point_id"], r["product_id"], r["transaction_type"], r["quantity"], r["user_id"], str(r["transaction_time"]), nhom))
    chi_mc.sort(key=lambda x: x[6])
    with open(os.path.join(ra, "chi_co_tren_may_chu.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["txn_id", "diem_quet", "mat_hang", "loai", "sl", "user_id", "thoi_gian", "nhom"]); w.writerows(chi_mc)

    # C. tồn kho = tồn gốc + nhập - xuất
    net = defaultdict(int)
    for r in db.values():
        net[r["product_id"]] += r["quantity"] if r["transaction_type"] == "IMPORT" else -r["quantity"]
    lech = []
    with open(os.path.join(ra, "ton_kho.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(["mat_hang", "ton_goc_seed", "tong_nhap_tru_xuat", "ton_ky_vong", "ton_thuc_te", "chenh_lech"])
        for p in sorted(ton):
            if p not in seed:
                continue
            kv = seed[p] + net.get(p, 0)
            w.writerow([p, seed[p], net.get(p, 0), kv, ton[p], ton[p] - kv])
            if ton[p] != kv:
                lech.append((p, kv, ton[p]))

    # D. khoảng trống seq: seq_no là bộ đếm liên tục của từng điểm quét, KHÔNG reset theo ngày
    #    (số trong txn_id: SPxx-<ngày>-<seq_no>), nên gộp mọi ngày của cùng một điểm quét.
    nhom_seq = defaultdict(dict)
    for c in hop:
        if c["so_tt"] != "":
            nhom_seq[c["scan_point_id"]][c["so_tt"]] = c["ngay_txn"]
    khoang, tom_tat_seq = [], []
    for sp, ds in sorted(nhom_seq.items()):
        thieu = sorted(set(range(1, max(ds) + 1)) - set(ds))
        ngay = sorted(set(ds.values()))
        tom_tat_seq.append(f"- {sp}: có {len(ds)} số, từ {min(ds)} đến {max(ds)} (các ngày trong txn_id: {', '.join(ngay)})")
        if thieu:
            khoang.append((sp, thieu))

    # Tổng hợp
    dem = defaultdict(int)
    for c in hop:
        dem[(c["scan_point_id"], c["ket_luan"])] += 1
    md = [f"# Đối chiếu điểm quét với máy chủ – {datetime.now():%d/%m/%Y %H:%M:%S}", "",
          f"- Nhật ký điểm quét: {a.queue_dir} ({len(hop)} giao dịch)",
          f"- CSDL: bảng warehouse_transactions có {len(db)} bản ghi (mọi nguồn)", "",
          "## A. Từng giao dịch của điểm quét so với máy chủ", "", "| Điểm quét | Kết luận | Số giao dịch |", "|---|---|---|"]
    for (sp, kl), n in sorted(dem.items()):
        md.append(f"| {sp} | {kl} | {n} |")
    thieu_list = [c for c in hop if c["ket_luan"].startswith(("THIẾU", "XUNG", "CÒN CHỜ", "ĐÃ LƯU", "TRẠNG"))]
    md += ["", "### Các dòng cần xem (không phải KHỚP)", ""]
    if thieu_list:
        md += ["| Điểm quét | txn_id | Ngày trong txn_id | Trạng thái điểm quét | Kết luận |", "|---|---|---|---|---|"]
        md += [f"| {c['scan_point_id']} | {c['txn_id']} | {c['ngay_txn']} | {c['trang_thai']} | {c['ket_luan']} |" for c in thieu_list]
    else:
        md.append("Không có.")
    md += ["", "## B. Giao dịch chỉ có trên máy chủ (điểm quét không có trong nhật ký)", ""]
    g = defaultdict(int)
    for x in chi_mc:
        g[(x[1], x[7])] += 1
    if g:
        md += ["| Điểm quét | Nhóm | Số giao dịch |", "|---|---|---|"] + [f"| {k[0]} | {k[1]} | {n} |" for k, n in sorted(g.items())]
    else:
        md.append("Không có.")
    khac = [x for x in chi_mc if x[7].startswith("khác")]
    if khac:
        md += ["", "### Chi tiết nhóm \"khác\"", "", "| txn_id | Mặt hàng | Loại | SL | Tài khoản | Thời gian |", "|---|---|---|---|---|---|"]
        md += [f"| {x[0]} | {x[2]} | {x[3]} | {x[4]} | {x[5]} | {x[6]} |" for x in khac[:40]]
    md += ["", "Chi tiết toàn bộ: chi_co_tren_may_chu.csv", "", "## C. Tồn kho: tồn gốc + nhập − xuất so với tồn thực tế", ""]
    if not seed:
        md.append("Không đọc được tồn gốc từ file seed, bỏ qua phần này.")
    elif lech:
        md += [f"**Có {len(lech)} mặt hàng lệch**:", "", "| Mặt hàng | Tồn kỳ vọng | Tồn thực tế |", "|---|---|---|"] + [f"| {p} | {k} | {t} |" for p, k, t in lech]
    else:
        md.append(f"Khớp ở cả {len([p for p in ton if p in seed])} mặt hàng: tồn thực tế = tồn gốc (file seed 02) + tổng nhập − tổng xuất của mọi giao dịch trong bảng.")
    md += ["", "## D. Khoảng trống số thứ tự (seq_no) trong nhật ký điểm quét", "",
           "seq_no tăng liên tục theo từng điểm quét, không đặt lại mỗi ngày; nên gộp mọi ngày của một điểm quét.", ""]
    md += tom_tat_seq
    md += ([f"- **{sp}: thiếu số {t}**" for sp, t in khoang] if khoang else ["", "Không có khoảng trống."])
    md += ["", "Lưu ý: nhật ký chỉ chứa giao dịch còn trong file queue; khoảng trống có thể do file bị xóa hoặc chạy trên máy khác."]
    txt = "\n".join(md) + "\n"
    open(os.path.join(ra, "doi_chieu.md"), "w", encoding="utf-8").write(txt)
    print(txt); print("Đã ghi vào", ra)
    return ra


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--queue-dir", default=os.path.join("SV2_DiemQuet_HangDoi", "queue"))
    ap.add_argument("--config", default=os.path.join("SV3_MayChu_CSDL_API", "04_DICH_VU_API", "config.json"))
    ap.add_argument("--seed", default=os.path.join("SV3_MayChu_CSDL_API", "01_CSDL_SQL", "02_insert_sample_data.sql"))
    ap.add_argument("--ngay-tai", default="20261115", help="ngày (yyyymmdd) đã chạy thử tải tai_thu_sv4")
    ap.add_argument("--ra", default=os.path.join("SV4_KiemThu", "ket_qua_doi_chieu"))
    chay(ap.parse_args())
