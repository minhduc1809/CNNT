const { d, P, H1, B, T, makeDoc, save } = require("./lib_docx");
const { Paragraph, TextRun, AlignmentType } = d;

const OUT = "D:\\Son_Work_Space\\Dự_án_Liên\\SV1_ThietKeMang_DuLieu\\cong_phoi_hop\\Cong2_BienBanQuanSat.docx";
const c = [];
const center = (s, size, bold = true) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 80 }, children: [new TextRun({ text: s, bold, size })] });

c.push(center("ĐỀ TÀI 22 – THIẾT KẾ HẠ TẦNG CNTT CHO HỆ THỐNG QUẢN LÝ KHO HÀNG THÔNG MINH", 24));
c.push(center("BIÊN BẢN CỔNG 2 – QUAN SÁT CHUỖI GỬI → LƯU → ĐỌC LẠI", 30));
c.push(center("(Mẫu do SV1 chuẩn bị – hạn Cổng 2: 4/11/2026)", 22, false));
c.push(P(""));
c.push(...T(["Mục", "Nội dung"], [
  ["Thời gian", "....h.... ngày ..../11/2026"],
  ["Người quan sát", "SV1 – ........................................"],
  ["Thành phần", "SV2 (điểm quét) – ....................   SV3 (máy chủ) – ....................   SV4 (kiểm thử) – ...................."],
  ["Môi trường", "Máy chủ SV3: http://................:8080 · CSDL: ............ · Client SV2 phiên bản: ............ · Python: ............"],
  ["Mục tiêu", "Xác nhận dữ liệu đi đúng luồng giữa điểm quét và máy chủ: giao dịch gửi từ SP01/SP02 được máy chủ kiểm tra, lưu vào CSDL, cập nhật tồn, và đọc lại ra đúng nội dung đã gửi; gửi trùng không đổi tồn; tài khoản chỉ xem không ghi được."],
  ["Điều kiện qua cổng", "Phần A đạt 10/10 bước và phần B không có quan sát “Không khớp”."],
], [1.6, 6]));

c.push(H1("1. Chuẩn bị"));
c.push(B("SV3 khởi động máy chủ trên CSDL sạch (schema.sql + seed_data.sql), ghi lại địa chỉ và cổng."));
c.push(B("SV2 mở 2 client SP01 (nv01) và SP02 (nv02) trỏ tới máy chủ SV3."));
c.push(B("SV1 mở cửa sổ dòng lệnh tại `cong_phoi_hop/`, sẵn sàng chạy `python kiem_tra_cong2.py --url http://<máy chủ SV3>:8080`."));
c.push(B("Đồng hồ hệ thống hiện trên màn hình khi chụp ảnh để có dấu thời gian."));

c.push(H1("2. Phần A – Kiểm tra tự động bằng script"));
c.push(P("Chạy `kiem_tra_cong2.py`; script ghi file `ket_qua/ketqua_cong2_<thời điểm>.md`. Chép kết quả từng bước vào bảng:", { after: 60 }));
c.push(...T(["Bước", "Nội dung", "Mong đợi", "Thực tế", "Đạt"], [
  ["C2-01", "nv01 đăng nhập tại SP01", "200, role NHANVIEN", "", "☐"],
  ["C2-02", "Đọc tồn SP001 trước khi gửi", "Có số tồn", "", "☐"],
  ["C2-03", "GỬI: SP01 NHAP 5 SP001", "201, stock_after = tồn trước + 5", "", "☐"],
  ["C2-04", "LƯU + ĐỌC LẠI theo txn_id", "200, mọi trường khớp, username = nv01, có server_time", "", "☐"],
  ["C2-05", "Tồn sau giao dịch", "= tồn trước + 5; last_txn_id đúng", "", "☐"],
  ["C2-06", "Gửi lại cùng txn_id", "409 DUPLICATE_TXN, tồn không đổi", "", "☐"],
  ["C2-07", "GỬI từ SP02: nv02 XUAT 2", "201, stock_after giảm 2", "", "☐"],
  ["C2-08", "thukho01 đọc lịch sử lọc SP02", "Thấy giao dịch của nv02", "", "☐"],
  ["C2-09", "quanly01 cố ghi giao dịch", "403 FORBIDDEN, tồn không đổi", "", "☐"],
  ["C2-10", "Đối chiếu tồn", "all_match = true", "", "☐"],
], [0.8, 2.6, 3, 2, 0.6], { size: 20, center: [4] }));
c.push(P("Đã chạy thử script với máy chủ giả lập ngày 27/10/2026: 10/10 bước đạt (`ket_qua/THU_GIA_LAP_ketqua_cong2_20261027_172531.md`). Kết quả này chỉ chứng minh script hoạt động, **không** thay cho lần quan sát trên máy chủ SV3."));

c.push(H1("3. Phần B – Quan sát trực tiếp trên client và CSDL"));
c.push(...T(["#", "Quan sát", "Cách xem", "Khớp", "Không khớp", "Ảnh minh chứng"], [
  ["B1", "Client SP01 hiện “Đã lưu” và tồn mới CHỈ SAU khi nhận 201 (không hiện ngay khi quét)", "Màn hình client SV2", "☐", "☐", ""],
  ["B2", "Client sinh txn_id đúng dạng SPxx-yyyymmdd-nnnn, lưu vào hàng đợi trước khi gửi", "File/bảng hàng đợi của SV2", "☐", "☐", ""],
  ["B3", "Dòng mới trong bảng Transactions có đủ txn_id, product_code, txn_type, quantity, username, scan_point_id, client_time, server_time, stock_after", "Mở kho.db (DB Browser for SQLite / sqlite3)", "☐", "☐", ""],
  ["B4", "Inventory.quantity và last_txn_id đổi đúng sau mỗi giao dịch", "Bảng Inventory", "☐", "☐", ""],
  ["B5", "AuditLog có 1 dòng cho MỖI yêu cầu, kể cả bị từ chối (409, 403)", "Bảng AuditLog", "☐", "☐", ""],
  ["B6", "Ngắt mạng client (tắt Wi-Fi / dừng server) rồi quét: client giữ hàng đợi, có mạng lại tự gửi lại cùng txn_id, tồn chỉ đổi 1 lần", "Client SV2 + bảng Transactions", "☐", "☐", ""],
  ["B7", "Tên trường trong JSON client gửi và trong CSDL khớp từ điển dữ liệu", "Chạy `doi_chieu/doi_chieu_ten_truong.py --sv2 … --sv3 … --db …`", "☐", "☐", ""],
], [0.5, 3.6, 2.2, 0.6, 0.8, 1.3], { size: 19, center: [3, 4] }));

c.push(H1("4. Vấn đề phát hiện và xử lý"));
c.push(...T(["#", "Vấn đề", "Bên xử lý", "Hạn", "Trạng thái"],
  [["1", "", "", "", ""], ["2", "", "", "", ""], ["3", "", "", "", ""]], [0.4, 4.8, 1.5, 1, 1.1], { zebra: false }));

c.push(H1("5. Kết luận"));
c.push(P("☐ Qua Cổng 2 – luồng gửi → lưu → đọc lại đúng        ☐ Qua có điều kiện – sửa mục 4 trước ngày ..../11/2026        ☐ Chưa qua – kiểm tra lại ngày ..../11/2026"));

c.push(H1("6. Ký xác nhận"));
c.push(...T(["Vai trò", "Họ và tên", "MSSV", "Chữ ký / xác nhận trực tuyến"], [
  ["SV1 – Quan sát", "", "", ""], ["SV2", "", "", ""], ["SV3", "", "", ""], ["SV4", "", "", ""],
], [1.6, 3, 1.5, 3], { zebra: false }));

(async () => {
  await save(makeDoc(c, { title: "Biên bản Cổng 2 – Đề tài 22", footer: "Đề tài 22 – Biên bản Cổng 2 · Trang " }), OUT);
  console.log("OK");
})();
