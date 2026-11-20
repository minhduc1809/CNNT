"""
Đề tài 22 - SV1-13: Rà soát hồ sơ chung trước khi chốt (cùng SV4).

Kiểm tra tự động trên file .docx của hồ sơ và các file .md/.txt/.csv minh chứng:
  1. Ô hướng dẫn chưa xóa: đoạn "[SV1: ...]", "[SV2: ...]", "[Cả nhóm: ...]"...
  2. Thuật ngữ không thống nhất (cột "Không dùng" của bảng thuật ngữ): VLAN 99, txnId, transaction_id...
  3. Số liệu then chốt phải xuất hiện và khớp nhau giữa các tài liệu (301 B, 0,67 / 1,33 GD/s, 192.168.10.10...).
  4. Đủ các chương bắt buộc: yêu cầu, giả định, kiến trúc, triển khai, kiểm thử, đánh giá, tài liệu tham khảo.
  5. Bảng kiểm thử: dòng KT1, KT2, KT3 đã có cột Thực tế / Đạt.
Bảng thuật ngữ (liệt kê chính các từ cấm) và Phụ lục C phiếu đóng góp (kể lại lỗi cũ) được bỏ qua khi tìm từ cấm.

Chạy:  python ra_soat_ho_so.py [đường_dẫn_hồ_sơ.docx] [--thu-muc thư_mục_minh_chứng ...]
Kết quả: in ra màn hình + RaSoat_<thời điểm>.md. Mã thoát 1 nếu còn vấn đề phải sửa.
"""

import argparse
import os
import re
import sys
import zipfile
from datetime import datetime

THU_MUC = os.path.dirname(os.path.abspath(__file__))
GOC_SV1 = os.path.dirname(THU_MUC)

TU_CAM = {  # cách viết không dùng -> cách dùng thống nhất
    r"VLAN\s*99": "3 VLAN: 10 / 20 / 30", r"\b4 VLAN\b": "3 VLAN", r"192\.168\.99\.": "IP quản lý switch 192.168.10.2",
    r"\btxnId\b": "txn_id", r"\btransaction_id\b": "txn_id", r"\bproductCode\b": "product_code",
    r"\bbarcode\b": "product_code / mã hàng", r"\bsku\b": "product_code", r"\bqty\b": "quantity",
    r"\bscanPointId\b": "scan_point_id", r"\btrạm quét\b": "điểm quét", r"\bmáy scan\b": "máy quét",
    r"\bTC1\b|\btest 1\b": "KT1", r"\bsố dư\b": "tồn",
}
SO_LIEU = {  # số liệu then chốt phải có mặt trong hồ sơ
    "301 byte/giao dịch": r"301\s*(B|byte)", "Tải đỉnh 2 điểm 0,67 GD/s": r"0[,.]67", "Tải đỉnh 4 điểm 1,33 GD/s": r"1[,.]33",
    "IP máy chủ 192.168.10.10": r"192\.168\.10\.10", "Cổng API 8080": r"8080", "3 VLAN (10/20/30)": r"VLAN\s*10",
}
CHUONG = ["Yêu cầu", "Giả định", "Kiến trúc", "Triển khai", "Kiểm thử", "Đánh giá", "Tài liệu tham khảo"]
RE_TODO = re.compile(r"\[(SV\d|Cả nhóm|Nhóm|Mỗi thành viên|SV4 \+ SV1)[^\]]*\]")


def doan_van_docx(duong):
    """Danh sách (kiểu, văn bản) từng đoạn trong document.xml - không cần thư viện ngoài."""
    with zipfile.ZipFile(duong) as z:
        xml = z.read("word/document.xml").decode("utf-8")
    kq = []
    for p in re.findall(r"<w:p[ >].*?</w:p>", xml, flags=re.S):
        kieu = re.search(r'<w:pStyle w:val="([^"]+)"', p)
        txt = "".join(re.findall(r"<w:t[^>]*>([^<]*)</w:t>", p))
        txt = txt.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
        if txt.strip():
            kq.append((kieu.group(1) if kieu else "", txt))
    return kq


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("ho_so", nargs="?", default=os.path.join(THU_MUC, "HoSoChung_DeTai22_Khung.docx"))
    ap.add_argument("--thu-muc", nargs="*", default=[GOC_SV1], help="thư mục minh chứng (.md .txt .csv) cần rà thuật ngữ")
    a = ap.parse_args()

    doan = doan_van_docx(a.ho_so)
    # Bỏ bảng thuật ngữ khi tìm từ cấm
    ra_soat, trong_thuat_ngu = [], False
    for kieu, t in doan:
        if kieu == "Heading1":   # bảng thuật ngữ và phiếu đóng góp (kể lại lỗi cũ) được phép nhắc từ cấm
            trong_thuat_ngu = t.strip().startswith(("Thuật ngữ", "Phụ lục C"))
        if not trong_thuat_ngu:
            ra_soat.append((kieu, t))
    toan_van = "\n".join(t for _, t in doan)

    van_de, canh_bao = [], []
    todo = [t for _, t in doan if RE_TODO.search(t)]
    for t in todo:
        van_de.append(("Ô hướng dẫn chưa xóa", t[:110]))
    for _, t in ra_soat:
        for mau, dung in TU_CAM.items():
            if re.search(mau, t, flags=re.I):
                van_de.append(("Thuật ngữ không thống nhất", f"“{re.search(mau, t, flags=re.I).group(0)}” → dùng “{dung}”: {t[:80]}"))
    for ten, mau in SO_LIEU.items():
        if not re.search(mau, toan_van):
            van_de.append(("Thiếu số liệu then chốt", ten))
    tieu_de = [t for k, t in doan if k == "Heading1"]
    for ch in CHUONG:
        if not any(ch.lower() in t.lower() for t in tieu_de):
            van_de.append(("Thiếu chương bắt buộc", ch))
    for kt in ("KT1", "KT2", "KT3"):
        if not re.search(kt + r".*(ĐẠT|Đạt|CHƯA ĐẠT)", toan_van):
            canh_bao.append(("Bảng kiểm thử chưa điền kết quả", kt))

    # Rà thuật ngữ trong file minh chứng dạng văn bản
    bo_qua = ("doi_chieu", "NhatKyThayDoi", "ra_soat_ho_so", "RaSoat_", "ket_qua", "nguon_")
    for goc in a.thu_muc:
        for d, _, files in os.walk(goc):
            for f in files:
                duong = os.path.join(d, f)
                if not f.endswith((".md", ".txt", ".csv")) or any(b in duong for b in bo_qua):
                    continue
                with open(duong, encoding="utf-8-sig", errors="replace") as fh:
                    for so, dong in enumerate(fh, 1):
                        for mau, dung in TU_CAM.items():
                            m = re.search(mau, dong, flags=re.I)
                            if m:
                                van_de.append(("Thuật ngữ trong file minh chứng", f"{os.path.relpath(duong, goc)}:{so} “{m.group(0)}” → “{dung}”"))

    tong_trang = sum(1 for k, _ in doan if k == "Heading1")
    md = [f"# Rà soát hồ sơ chung – {datetime.now():%Y-%m-%d %H:%M:%S}", "",
          f"- Hồ sơ: `{os.path.basename(a.ho_so)}` ({len(doan)} đoạn, {tong_trang} đề mục cấp 1)",
          f"- Vấn đề phải sửa: **{len(van_de)}** · Cảnh báo: **{len(canh_bao)}**", "",
          "| # | Loại | Chi tiết |", "|---|---|---|"]
    md += [f"| {i} | {k} | {v.replace('|', '/')} |" for i, (k, v) in enumerate(van_de + canh_bao, 1)]
    ten = os.path.join(THU_MUC, f"RaSoat_{datetime.now():%Y%m%d_%H%M%S}.md")
    with open(ten, "w", encoding="utf-8") as f:
        f.write("\n".join(md) + "\n")
    tom = {}
    for k, _ in van_de + canh_bao:
        tom[k] = tom.get(k, 0) + 1
    print(f"Hồ sơ: {os.path.basename(a.ho_so)} · {len(van_de)} vấn đề, {len(canh_bao)} cảnh báo")
    for k, v in tom.items():
        print(f"  - {k}: {v}")
    print(f"Chi tiết: {os.path.basename(ten)}")
    return 1 if van_de else 0


if __name__ == "__main__":
    sys.exit(main())
