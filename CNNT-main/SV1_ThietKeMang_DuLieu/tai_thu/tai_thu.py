"""
Đề tài 22 - SV1-11: Script thử tải - chạy 2 rồi 4 tiến trình khách (mỗi tiến trình = 1 điểm quét).

SV1 viết, SV4 chạy trên máy chủ thật của SV3 để đo và so với bảng ước lượng 07_UocLuong_MoRong.xlsx.

Mỗi tiến trình:
  - đăng nhập bằng nv0i, gửi giao dịch từ SP0i theo nhịp "khoang_cach_giua_2_lan_quet_s"
    (mặc định 3 s = giả định G2), xen kẽ NHAP 1 / XUAT 1 trên từng mã hàng nên tồn không bao giờ âm;
  - với xác suất "ti_le_gui_trung" gửi lại một txn_id đã thành công -> phải nhận 409 (KT2 dưới tải);
  - ghi từng yêu cầu: thời điểm, txn_id, mã HTTP, mã lỗi, độ trễ (ms).
Sau mỗi kịch bản: đọc lại ngẫu nhiên N giao dịch đã 201 và gọi /api/reconcile để kiểm tra nhất quán.

Kết quả: ket_qua/<thời điểm>/<kịch bản>/raw.csv (dữ liệu đo gốc), tong_hop.json, tong_hop.md.

LƯU Ý: chạy trên CSDL sạch (vừa khôi phục từ seed) vì txn_id dùng ngày hôm nay + số thứ tự;
chạy lại trong cùng ngày trên cùng CSDL sẽ bị 409 ở giao dịch "mới" (báo trong mục lỗi khác).

Chạy:
  python tai_thu.py                         # dùng tham_so_tai.json
  python tai_thu.py --url http://192.168.10.10:8080 --thoi-gian 120
  python tai_thu.py --gang-suc --thoi-gian 20   # gửi liên tục, không nghỉ: đo năng lực tối đa
Chỉ dùng thư viện chuẩn Python 3.8+.
"""

import argparse
import csv
import json
import multiprocessing as mp
import os
import random
import statistics
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime

THU_MUC = os.path.dirname(os.path.abspath(__file__))


def goi(url, phuong_thuc, duong, token=None, body=None, timeout=5):
    req = urllib.request.Request(url + duong, method=phuong_thuc,
                                 data=json.dumps(body).encode() if body is not None else None)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read().decode("utf-8"))
        except ValueError:
            return e.code, {}
    except Exception as e:  # mất kết nối / hết thời gian chờ
        return 0, {"error_code": "TIMEOUT_OR_NETWORK", "message": str(e)}


def tien_trinh(args):
    """Một điểm quét. Trả danh sách bản ghi đo."""
    i, ts = args
    diem, user = f"SP{i:02d}", f"nv{i:02d}"
    url, timeout = ts["url"], ts["timeout_s"]
    ma, r = goi(url, "POST", "/api/login", body={"username": user, "password": ts["mat_khau"]}, timeout=timeout)
    if ma != 200:
        return [{"tien_trinh": i, "scan_point_id": diem, "loai": "LOGIN", "http": ma,
                 "error_code": r.get("error_code"), "do_tre_ms": 0, "thoi_diem": datetime.now().isoformat(), "txn_id": ""}]
    token = r["token"]
    ngay = datetime.now().strftime("%Y%m%d")
    stt0 = ts["co_so"]          # mỗi kịch bản một vùng số thứ tự riêng để txn_id không trùng nhau
    rng = random.Random(i * 7919 + int(time.time()))
    lan_sau = {m: "NHAP" for m in ts["ma_hang"]}
    da_ok, ban_ghi = [], []
    while time.time() < ts["bat_dau"]:
        time.sleep(0.01)
    het_gio = ts["bat_dau"] + ts["thoi_gian"]
    stt = 0
    while time.time() < het_gio:
        t_moi = time.time()
        if da_ok and rng.random() < ts["ti_le_gui_trung"]:
            body, loai = rng.choice(da_ok), "GUI_TRUNG"
        else:
            stt += 1
            if stt > ts["vung"] - 1:       # hết vùng số thứ tự của kịch bản (giới hạn 4 chữ số của txn_id)
                break
            m = rng.choice(ts["ma_hang"])
            body = {"txn_id": f"{diem}-{ngay}-{stt0 + stt:04d}", "product_code": m, "txn_type": lan_sau[m],
                    "quantity": 1, "scan_point_id": diem, "client_time": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
            loai = "MOI"
        t0 = time.perf_counter()
        ma, r = goi(url, "POST", "/api/transactions", token, body, timeout)
        tre = (time.perf_counter() - t0) * 1000
        if loai == "MOI" and ma == 201:
            lan_sau[body["product_code"]] = "XUAT" if body["txn_type"] == "NHAP" else "NHAP"
            da_ok.append(body)
        ban_ghi.append({"thoi_diem": datetime.now().isoformat(timespec="milliseconds"), "tien_trinh": i,
                        "scan_point_id": diem, "txn_id": body["txn_id"], "loai": loai, "http": ma,
                        "error_code": r.get("error_code", ""), "do_tre_ms": round(tre, 2)})
        nghi = ts["khoang_cach"] - (time.time() - t_moi)
        if nghi > 0:
            time.sleep(nghi)
    return ban_ghi


def phan_vi(ds, p):
    if not ds:
        return None
    ds = sorted(ds)
    k = (len(ds) - 1) * p / 100
    f = int(k)
    return round(ds[f] + (ds[min(f + 1, len(ds) - 1)] - ds[f]) * (k - f), 2)


def chay_kich_ban(kb, ts, thu_muc_kq, thu_tu, so_kb):
    n = kb["so_tien_trinh"]
    vung = 10000 // so_kb
    ts = dict(ts, bat_dau=time.time() + 2, co_so=thu_tu * vung, vung=vung)
    print(f"\n>>> Kịch bản {kb['ten']}: {n} tiến trình, {ts['thoi_gian']} s, nhịp {ts['khoang_cach']} s/lần/điểm", flush=True)
    with mp.Pool(n) as pool:
        kq = pool.map(tien_trinh, [(i, ts) for i in range(1, n + 1)])
    ghi = [x for k in kq for x in k]
    os.makedirs(thu_muc_kq, exist_ok=True)
    with open(os.path.join(thu_muc_kq, "raw.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=["thoi_diem", "tien_trinh", "scan_point_id", "txn_id", "loai", "http", "error_code", "do_tre_ms"])
        w.writeheader()
        w.writerows(sorted(ghi, key=lambda x: x["thoi_diem"]))

    moi = [x for x in ghi if x["loai"] == "MOI"]
    trung = [x for x in ghi if x["loai"] == "GUI_TRUNG"]
    ok = [x for x in moi if x["http"] == 201]
    loi = {}
    for x in ghi:
        if not (x["loai"] == "MOI" and x["http"] == 201) and not (x["loai"] == "GUI_TRUNG" and x["http"] == 409):
            loi[f"{x['http']} {x['error_code']}"] = loi.get(f"{x['http']} {x['error_code']}", 0) + 1
    tre = [x["do_tre_ms"] for x in ghi if x["http"]]

    # Kiểm tra nhất quán sau tải
    _, r = goi(ts["url"], "POST", "/api/login", body={"username": "thukho01", "password": ts["mat_khau"]})
    tk = r.get("token")
    mau = random.sample(ok, min(ts["so_doc_lai"], len(ok)))
    doc_lai_ok = sum(1 for x in mau if goi(ts["url"], "GET", f"/api/transactions/{x['txn_id']}", tk)[0] == 200)
    ma_dc, dc = goi(ts["url"], "GET", "/api/reconcile", tk)

    th = {
        "kich_ban": kb["ten"], "so_tien_trinh": n, "thoi_gian_s": ts["thoi_gian"], "khoang_cach_s": ts["khoang_cach"],
        "tong_yeu_cau": len(ghi), "giao_dich_moi": len(moi), "moi_thanh_cong_201": len(ok),
        "gui_trung": len(trung), "gui_trung_nhan_409": sum(1 for x in trung if x["http"] == 409),
        "loi_khac": loi, "thong_luong_gd_moi_s": round(len(ok) / ts["thoi_gian"], 3),
        "thong_luong_yeu_cau_s": round(len(ghi) / ts["thoi_gian"], 3),
        "do_tre_ms": {"tb": round(statistics.mean(tre), 2) if tre else None, "p50": phan_vi(tre, 50),
                      "p95": phan_vi(tre, 95), "p99": phan_vi(tre, 99), "max": max(tre) if tre else None},
        "doc_lai_mau": f"{doc_lai_ok}/{len(mau)}", "doi_chieu_all_match": dc.get("all_match") if ma_dc == 200 else f"HTTP {ma_dc}",
    }
    with open(os.path.join(thu_muc_kq, "tong_hop.json"), "w", encoding="utf-8") as f:
        json.dump(th, f, ensure_ascii=False, indent=2)
    print(json.dumps(th, ensure_ascii=False, indent=2), flush=True)
    return th


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description="Thử tải 2 rồi 4 điểm quét")
    ap.add_argument("--tham-so", default=os.path.join(THU_MUC, "tham_so_tai.json"))
    ap.add_argument("--url")
    ap.add_argument("--thoi-gian", type=float, help="giây cho mỗi kịch bản")
    ap.add_argument("--gang-suc", action="store_true", help="gửi liên tục không nghỉ (đo năng lực tối đa)")
    ap.add_argument("--nhan", default="", help="nhãn thêm vào tên thư mục kết quả")
    a = ap.parse_args()
    with open(a.tham_so, encoding="utf-8") as f:
        cfg = json.load(f)
    ts = {"url": (a.url or cfg["url"]).rstrip("/"), "mat_khau": cfg["mat_khau"], "timeout_s": cfg["timeout_s"],
          "thoi_gian": a.thoi_gian or cfg["thoi_gian_moi_kich_ban_s"],
          "khoang_cach": 0.0 if a.gang_suc else cfg["khoang_cach_giua_2_lan_quet_s"],
          "ti_le_gui_trung": cfg["ti_le_gui_trung"], "ma_hang": cfg["ma_hang"],
          "so_doc_lai": cfg["so_giao_dich_doc_lai_kiem_tra"]}
    goc = os.path.join(THU_MUC, "ket_qua", datetime.now().strftime("%Y%m%d_%H%M%S") + (("_" + a.nhan) if a.nhan else ""))
    print(f"Thử tải: {ts['url']} · kết quả: {goc}")
    tong = []
    for k, kb in enumerate(cfg["kich_ban"]):
        if k:
            time.sleep(cfg["nghi_giua_2_kich_ban_s"])
        tong.append(chay_kich_ban(kb, ts, os.path.join(goc, kb["ten"]), k, len(cfg["kich_ban"])))

    md = [f"# Tổng hợp thử tải – {datetime.now():%Y-%m-%d %H:%M:%S}", "",
          f"Máy chủ `{ts['url']}` · mỗi kịch bản {ts['thoi_gian']} s · nhịp {ts['khoang_cach']} s/lần/điểm "
          f"· tỉ lệ gửi trùng {ts['ti_le_gui_trung']:.0%}", "",
          "| Chỉ tiêu | " + " | ".join(t["kich_ban"] for t in tong) + " |", "|---|" + "---|" * len(tong)]
    hang = [("Số tiến trình (điểm quét)", "so_tien_trinh"), ("Tổng yêu cầu", "tong_yeu_cau"),
            ("Giao dịch mới thành công (201)", "moi_thanh_cong_201"), ("Gửi trùng / nhận 409", None),
            ("Thông lượng giao dịch mới (GD/s)", "thong_luong_gd_moi_s"), ("Độ trễ trung bình (ms)", ("do_tre_ms", "tb")),
            ("Độ trễ p95 (ms)", ("do_tre_ms", "p95")), ("Độ trễ lớn nhất (ms)", ("do_tre_ms", "max")),
            ("Lỗi khác (không mong đợi)", "loi_khac"), ("Đọc lại mẫu giao dịch 201", "doc_lai_mau"),
            ("Đối chiếu tồn all_match", "doi_chieu_all_match")]
    for ten, k in hang:
        o = []
        for t in tong:
            if k is None:
                o.append(f"{t['gui_trung']} / {t['gui_trung_nhan_409']}")
            elif isinstance(k, tuple):
                o.append(str(t[k[0]][k[1]]))
            else:
                v = t[k]
                o.append(("không có" if not v else ", ".join(f"{a}: {b}" for a, b in v.items())) if isinstance(v, dict) else str(v))
        md.append(f"| {ten} | " + " | ".join(o) + " |")
    with open(os.path.join(goc, "tong_hop.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    print(f"\nĐã ghi {os.path.join(goc, 'tong_hop.md')}")


if __name__ == "__main__":
    mp.freeze_support()
    main()
