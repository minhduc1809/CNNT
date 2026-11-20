"""
SV4 - Đo CPU và RAM trong lúc thử tải (Đề tài 22).

Hai lệnh:
  1) Ghi số đo mỗi 1 giây cho tới khi bấm Ctrl+C:
       python do_cpu_ram.py ghi --ra MinhChung\\MC-MR-05_cpu_ram.csv
  2) Sau khi thử tải xong, tính trung bình và lớn nhất riêng cho từng kịch bản (2 điểm, 4 điểm):
       python do_cpu_ram.py tong-hop --csv MinhChung\\MC-MR-05_cpu_ram.csv --kq KiemThu_DoiChieu_NguyenManhDung\\ket_qua\\<thư mục lần chạy>

Đo: CPU và RAM của cả máy; CPU và RAM của riêng 3 nhóm tiến trình: app.py (máy chủ API),
mysqld (CSDL), tai_thu (chương trình sinh tải). CPU tính theo % của TOÀN BỘ máy (0-100).
Cần: pip install psutil
"""
import argparse, csv, os, sys, time
from datetime import datetime

import psutil

NHOM = {"api": ["app.py"], "mysql": ["mysqld"], "tai": ["tai_thu"]}


def nhom_cua(p):
    try:
        ten = (p.info["name"] or "").lower()
        dong = " ".join(p.info["cmdline"] or []).lower()
    except Exception:
        return None
    if "mysqld" in ten:
        return "mysql"
    if "python" in ten:
        if "tai_thu" in dong or "multiprocessing" in dong:   # tiến trình chính và các tiến trình con (Windows)
            return "tai"
        if "app.py" in dong:
            return "api"
    return None


def ghi(a):
    ncpu = psutil.cpu_count()
    cot = ["thoi_diem", "cpu_may_pct", "ram_may_pct", "ram_may_mb"]
    for n in NHOM:
        cot += [f"cpu_{n}_pct", f"ram_{n}_mb"]
    os.makedirs(os.path.dirname(os.path.abspath(a.ra)), exist_ok=True)
    cache = {}
    print(f"Đang ghi vào {a.ra} (mỗi 1 giây). Bấm Ctrl+C để dừng.")
    psutil.cpu_percent(None)
    with open(a.ra, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f); w.writerow(cot)
        try:
            while True:
                t_dau = time.time()
                cpu_nhom = {n: 0.0 for n in NHOM}; ram_nhom = {n: 0.0 for n in NHOM}
                dem = {n: 0 for n in NHOM}
                for p in psutil.process_iter(["name", "cmdline"]):
                    n = nhom_cua(p)
                    if not n:
                        continue
                    try:
                        q = cache.setdefault(p.pid, p)
                        cpu_nhom[n] += q.cpu_percent(None) / ncpu
                        ram_nhom[n] += q.memory_info().rss / 1e6
                        dem[n] += 1
                    except Exception:
                        pass
                time.sleep(max(0, 1 - (time.time() - t_dau)))
                vm = psutil.virtual_memory()
                row = [datetime.now().isoformat(timespec="milliseconds"), psutil.cpu_percent(None),
                       vm.percent, round(vm.used / 1e6)]
                for n in NHOM:
                    row += [round(cpu_nhom[n], 1), round(ram_nhom[n])]
                w.writerow(row); f.flush()
        except KeyboardInterrupt:
            print("Đã dừng.")


def doc_csv(p):
    with open(p, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def tong_hop(a):
    mau = doc_csv(a.csv)
    cot = [c for c in mau[0].keys() if c != "thoi_diem"]
    out = ["# Tổng hợp CPU/RAM theo kịch bản", "", f"Nguồn: {a.csv}", ""]
    res = {}
    for kb in ("2_diem_quet", "4_diem_quet"):
        raw = os.path.join(a.kq, kb, "raw.csv")
        if not os.path.exists(raw):
            print("Không thấy", raw); continue
        ts = [r["thoi_diem"] for r in doc_csv(raw)]
        t0, t1 = min(ts), max(ts)
        sel = [r for r in mau if t0 <= r["thoi_diem"] <= t1]
        res[kb] = (t0, t1, sel)
    out.append("| Chỉ tiêu | " + " | ".join(res) + " |")
    out.append("|---|" + "---|" * len(res))
    out.append("| Khoảng thời gian | " + " | ".join(f"{v[0][11:19]}–{v[1][11:19]}" for v in res.values()) + " |")
    out.append("| Số mẫu (1 mẫu/giây) | " + " | ".join(str(len(v[2])) for v in res.values()) + " |")
    for c in cot:
        cells = []
        for v in res.values():
            xs = [float(r[c]) for r in v[2]]
            cells.append(f"TB {sum(xs)/len(xs):.1f} / lớn nhất {max(xs):.1f}" if xs else "không có mẫu")
        out.append(f"| {c} | " + " | ".join(cells) + " |")
    txt = "\n".join(out)
    print(txt)
    dst = os.path.splitext(a.csv)[0] + "_tong_hop.md"
    open(dst, "w", encoding="utf-8").write(txt + "\n")
    print("\nĐã ghi", dst)


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(); sp = ap.add_subparsers(dest="lenh", required=True)
    g = sp.add_parser("ghi"); g.add_argument("--ra", required=True); g.set_defaults(f=ghi)
    t = sp.add_parser("tong-hop"); t.add_argument("--csv", required=True); t.add_argument("--kq", required=True); t.set_defaults(f=tong_hop)
    a = ap.parse_args(); a.f(a)
