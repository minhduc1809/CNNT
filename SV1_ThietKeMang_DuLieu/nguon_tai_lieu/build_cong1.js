const path = require("path");
const { d, P, H1, H2, B, N, T, makeDoc, save } = require("./lib_docx");
const { Paragraph, TextRun, AlignmentType } = d;

const OUT = "D:\\Son_Work_Space\\Dự_án_Liên\\SV1_ThietKeMang_DuLieu\\cong_phoi_hop\\Cong1_BienBanBanGiao.docx";
const c = [];
const center = (s, size, bold = true) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: s, bold, size })] });

c.push(center("ĐỀ TÀI 22 – THIẾT KẾ HẠ TẦNG CNTT CHO HỆ THỐNG QUẢN LÝ KHO HÀNG THÔNG MINH", 24));
c.push(center("BIÊN BẢN CỔNG 1 – BÀN GIAO THIẾT KẾ VÀ CHỐT CHUẨN CHUNG", 30));
c.push(center("(Mẫu do SV1 chuẩn bị – điền trong buổi họp, các thành viên ký xác nhận)", 22, false));
c.push(P(""));

c.push(...T(["Mục", "Nội dung"], [
  ["Thời gian", "....h.... ngày ..../..../2026"],
  ["Hình thức / địa điểm", "Trực tiếp tại ........................ / Trực tuyến qua ........................"],
  ["Chủ trì", "SV1 – ........................................ (MSSV ....................)"],
  ["Thành phần", "SV2 – ........................   SV3 – ........................   SV4 – ........................   SV5 (nếu có) – ........................"],
  ["Thư ký", "........................................"],
  ["Mục tiêu", "Bàn giao bộ thiết kế v1.0 của SV1 và chốt một chuẩn chung (địa chỉ, tên trường, mã giao dịch, mã lỗi, quyền, sao lưu, dữ liệu mẫu) để SV2, SV3, SV4 bắt đầu triển khai mà không phải sửa lại khi ghép."],
  ["Điều kiện qua cổng", "Tất cả hạng mục ở mục 3 được đánh dấu “Đồng ý”, hoặc mọi hạng mục “Cần sửa” đã có người chịu trách nhiệm và hạn sửa."],
], [1.6, 6]));

c.push(H1("1. Chương trình họp (khoảng 45 phút)"));
c.push(...T(["Thời lượng", "Nội dung", "Người trình bày"], [
  ["5 phút", "Mục tiêu Cổng 1, giới thiệu thư mục SV1_ThietKeMang_DuLieu", "SV1"],
  ["10 phút", "Kiến trúc 3 VLAN, phần chạy thật / chỉ trên sơ đồ (01_SoDoHaTang.png)", "SV1"],
  ["10 phút", "Mô hình dữ liệu và từ điển (02_MoHinhDuLieu.png, 06_TuDienDuLieu.md)", "SV1"],
  ["10 phút", "Luồng dữ liệu, giao ước API, mã lỗi, ma trận quyền (04_SoDoLuongDuLieu.png, 05_GiaoUocAPI.md)", "SV1"],
  ["10 phút", "Rà checklist mục 3, ghi ý kiến, chốt phân công và hạn mục 4, ký xác nhận", "Cả nhóm"],
], [1.2, 5.5, 1.5]));

c.push(H1("2. Hồ sơ SV1 bàn giao (phiên bản v1.0)"));
c.push(...T(["#", "File", "Nội dung", "Bên nhận chính", "Đã nhận"], [
  ["1", "01_SoDoHaTang.png", "Sơ đồ hạ tầng, 3 VLAN, phần chạy thật / chỉ sơ đồ", "Cả nhóm", "☐"],
  ["2", "02_MoHinhDuLieu.png", "Sơ đồ các bảng và quan hệ", "SV3, SV4", "☐"],
  ["3", "03_ThietKeDuLieu.docx / .pdf", "Tài liệu thiết kế đầy đủ", "Cả nhóm", "☐"],
  ["4", "04_SoDoLuongDuLieu.png", "Lưu đồ luồng dữ liệu, nhánh lỗi / trùng / mất mạng", "SV2, SV3, SV4", "☐"],
  ["5", "05_GiaoUocAPI.md", "Giao ước API, 14 mã lỗi, ma trận quyền", "SV2, SV3, SV4", "☐"],
  ["6", "06_TuDienDuLieu.md (+ du_lieu/TuDienDuLieu.csv)", "Từ điển dữ liệu 6 bảng, 38 trường", "SV2, SV3", "☐"],
  ["7", "du_lieu/schema.sql, seed_data.sql", "Lược đồ CSDL + dữ liệu mẫu giả", "SV3, SV4", "☐"],
  ["8", "du_lieu/kiem_tra_thiet_ke.py", "Hàm ghi giao dịch tham chiếu + 11 tình huống kiểm chứng", "SV3, SV4", "☐"],
  ["9", "cau_hinh/ (router, switch, Wi-Fi, IP, ACL, hướng dẫn PT)", "Cấu hình mạng và bảng IP", "Cả nhóm", "☐"],
], [0.4, 2.8, 3, 1.3, 0.8], { size: 20, center: [4] }));

c.push(H1("3. Checklist chốt chuẩn chung"));
c.push(P("Đánh dấu ☑ vào cột kết quả. Hạng mục “Cần sửa” ghi rõ nội dung sửa, người sửa và hạn ở cột ghi chú.", { after: 60 }));
const rows = [
  ["Kiến trúc", "4 lớp: điểm quét → LAN → máy chủ ứng dụng → CSDL; điểm quét KHÔNG truy cập CSDL trực tiếp", "Cả nhóm"],
  ["Mạng", "3 VLAN: 10 máy chủ 192.168.10.0/24, 20 văn phòng, 30 điểm quét; SRV-KHO 192.168.10.10; API cổng 8080", "Cả nhóm"],
  ["Chạy thật / sơ đồ", "Chạy thật: 2 client, server, SQLite, thư mục backup/, 5 tài khoản. Chỉ sơ đồ + PT: switch, router, Wi-Fi, VLAN, ACL", "Cả nhóm"],
  ["Công nghệ", "Python 3.10+ (ghi rõ phiên bản trong README), SQLite 3, HTTP/JSON UTF-8; không cài thêm thư viện ngoài nếu không cần", "SV2, SV3"],
  ["Địa chỉ máy chủ", "Mô phỏng http://127.0.0.1:8080; đổi được bằng file cấu hình / tham số dòng lệnh, không viết cứng trong mã", "SV2, SV3"],
  ["Tên bảng, tên trường", "Đúng 6 bảng, 38 trường trong 06_TuDienDuLieu.md; không tự đổi tên", "SV3"],
  ["Tên khóa JSON", "Trùng tên trường CSDL (snake_case): txn_id, product_code, txn_type, quantity, scan_point_id, client_time, stock_after, server_time…", "SV2, SV3"],
  ["Mã giao dịch", "SPxx-yyyymmdd-nnnn, máy khách sinh và lưu vào hàng đợi TRƯỚC khi gửi; gửi lại giữ nguyên mã", "SV2"],
  ["Thời gian", "ISO 8601 giờ địa phương, không múi giờ: 2026-10-26T09:15:02", "SV2, SV3"],
  ["Mã lỗi", "Đúng 14 mã và mã HTTP trong mục 6 của giao ước; 409 DUPLICATE_TXN = coi như đã lưu", "SV2, SV3, SV4"],
  ["Quyền", "4 vai trò ADMIN / THUKHO / NHANVIEN / QUANLY theo ma trận quyền; máy chủ lấy người thực hiện từ token", "SV3, SV4"],
  ["Quy tắc ghi", "Thứ tự kiểm tra R5 → R3 → R6 → R1 → R2 → R4; INSERT + UPDATE trong 1 giao dịch CSDL; chỉ trả 201 sau COMMIT", "SV3"],
  ["Mất mạng", "Chờ phản hồi tối đa 5 s; thử lại 5 → 10 → 20 s (tối đa 60 s) với cùng txn_id; hàng đợi không mất khi tắt client", "SV2"],
  ["Sao lưu", "Thư mục backup/, tên file kho_yyyymmdd_hhmm.db; chỉ ADMIN; sau khôi phục chạy đối chiếu v_doi_chieu_ton (chenh_lech = 0)", "SV3, SV4"],
  ["Dữ liệu mẫu", "Dùng seed_data.sql: 5 mã hàng SP001–SP005, tồn đầu 100 / 50 / 200 / 80 / 0; 5 tài khoản, mật khẩu Kho@2026", "SV3, SV4"],
  ["KT1 mong đợi", "nv01 tại SP01 NHAP 20 SP001 → 201 OK, tồn SP001 = 120, Transactions có đủ mã, thời gian, người thực hiện", "SV4"],
  ["KT2 mong đợi", "Gửi lại đúng txn_id đã ghi → 409 DUPLICATE_TXN, tồn và số dòng Transactions không đổi", "SV4"],
  ["KT3 mong đợi", "quanly01 ghi → 403 FORBIDDEN, tồn không đổi; khôi phục bản sao → /api/reconcile all_match = true", "SV4"],
  ["Quản lý thay đổi", "Sau Cổng 1, mọi thay đổi chuẩn phải tăng phiên bản giao ước và ghi vào doi_chieu/NhatKyThayDoi.md", "Cả nhóm"],
  ["Thư mục nộp", "DeTai22_Nhom__/ gồm README.md, SV1_ThietKeMang_DuLieu/, SV2_DiemQuet/, SV3_LuuTru_Quyen_SaoLuu/, SV4_KiemThu_MoRong/, HoSoChung/", "Cả nhóm"],
];
c.push(...T(["#", "Hạng mục", "Chuẩn chốt", "Người xác nhận", "Đồng ý", "Cần sửa", "Ghi chú"],
  rows.map((r, i) => [String(i + 1), r[0], r[1], r[2], "☐", "☐", ""]), [0.35, 1.3, 4, 1.1, 0.6, 0.6, 1.3], { size: 19, center: [4, 5] }));

c.push(H1("4. Phân công sau Cổng 1"));
c.push(...T(["Người", "Việc bắt đầu ngay", "Sản phẩm cần có trước Cổng 2", "Hạn"], [
  ["SV2", "Client điểm quét SP01/SP02: đăng nhập, nhập mã, sinh txn_id, hàng đợi, gửi lại khi mất mạng", "2 client gửi được giao dịch tới server, hiển thị 201 / 409 / lỗi", "4/11/2026"],
  ["SV3", "Server API theo giao ước, CSDL từ schema.sql, phân quyền, sao lưu/khôi phục", "POST/GET chạy được; 403 cho quanly01; tạo được 1 bản sao lưu", "4/11/2026"],
  ["SV4", "Bảng kiểm thử KT1–KT3 và tình huống lỗi/trùng; chuẩn bị đo tải", "Bảng kiểm thử (đầu vào, thao tác, mong đợi) sẵn sàng chạy", "4/11/2026"],
  ["SV1", "Công cụ đối chiếu tên trường; mô hình ước lượng 2 → 4 điểm quét; script tải", "Đối chiếu tên trường trong mã SV2/SV3 ngay khi có mã", "4/11/2026 (Cổng 2)"],
  ["SV5 (nếu có)", "Theo phần việc SV5 trong hướng dẫn chung", "", ""],
], [0.9, 3.4, 3.4, 1.2], { size: 20 }));

c.push(H1("5. Quyết định và vấn đề còn mở"));
c.push(...T(["#", "Nội dung (quyết định / ý kiến / vấn đề)", "Người phụ trách", "Hạn", "Trạng thái"],
  [["1", "", "", "", ""], ["2", "", "", "", ""], ["3", "", "", "", ""], ["4", "", "", "", ""]], [0.4, 4.8, 1.5, 1, 1.1], { zebra: false }));

c.push(H1("6. Kết luận"));
c.push(P("☐ Qua Cổng 1 – bắt đầu triển khai theo chuẩn v1.0        ☐ Qua có điều kiện – sửa các hạng mục ghi ở mục 5 trước ngày ..../..../2026        ☐ Chưa qua – họp lại ngày ..../..../2026"));
c.push(P("Mốc tiếp theo: **Cổng 2 (hạn 4/11/2026)** – quan sát chuỗi gửi → lưu → đọc lại giữa điểm quét và máy chủ."));

c.push(H1("7. Ký xác nhận"));
c.push(...T(["Vai trò", "Họ và tên", "MSSV", "Chữ ký / xác nhận trực tuyến"], [
  ["SV1 – Chủ trì", "", "", ""], ["SV2", "", "", ""], ["SV3", "", "", ""], ["SV4", "", "", ""], ["SV5 (nếu có)", "", "", ""],
], [1.6, 3, 1.5, 3], { zebra: false }));

(async () => {
  await save(makeDoc(c, { title: "Biên bản Cổng 1 – Đề tài 22", footer: "Đề tài 22 – Biên bản Cổng 1 · Trang " }), OUT);
  console.log("OK");
})();
