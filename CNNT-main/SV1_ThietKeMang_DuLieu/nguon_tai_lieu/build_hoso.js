const path = require("path");
const { d, P, H1, H2, B, N, T, IMG, CAP, BREAK, makeDoc, save, TableOfContents } = require("./lib_docx");
const { Paragraph, TextRun, AlignmentType, ShadingType } = d;

const ROOT = "D:\\Son_Work_Space\\Dự_án_Liên\\SV1_ThietKeMang_DuLieu";
const OUT = path.join(ROOT, "ho_so_chung", "HoSoChung_DeTai22_Khung.docx");
const c = [];
const center = (s, size, bold = true, color) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 100 }, children: [new TextRun({ text: s, bold, size, color })] });
// Ô hướng dẫn điền (nền vàng nhạt, chữ nghiêng) – XÓA khi hoàn thiện
const TODO = (s) => new Paragraph({ children: [new TextRun({ text: "[" + s + "]", italics: true, color: "9A3412", size: 23 })],
  shading: { type: ShadingType.CLEAR, fill: "FEF3C7", color: "auto" }, spacing: { after: 120, line: 280 } });

// ---------------- Bìa ----------------
c.push(center("HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG", 26));
c.push(center("VIỆN KHOA HỌC KỸ THUẬT BƯU ĐIỆN", 26));
c.push(center("Học phần: Nhập môn Công nghệ nền tảng (RIPT1304)", 26, false));
c.push(new Paragraph({ spacing: { after: 600 }, children: [] }));
c.push(center("BÁO CÁO BÀI TẬP NHÓM", 30, true, "1F3864"));
c.push(center("ĐỀ TÀI 22", 30, true, "1F3864"));
c.push(center("THIẾT KẾ HẠ TẦNG CNTT CHO HỆ THỐNG QUẢN LÝ KHO HÀNG THÔNG MINH", 34, true, "1F3864"));
c.push(new Paragraph({ spacing: { after: 400 }, children: [] }));
c.push(...T(["Vai trò", "Họ và tên", "MSSV", "Phần việc chính"], [
  ["SV1", "", "", "Thiết kế mạng và mô hình dữ liệu"],
  ["SV2", "", "", "Dựng hai điểm quét giả lập"],
  ["SV3", "", "", "Triển khai lưu trữ, quyền và sao lưu"],
  ["SV4", "", "", "Kiểm tra nhất quán, lỗi và mở rộng"],
  ["SV5 (nếu có)", "", "", "Theo hướng dẫn chung"],
], [1.2, 3, 1.6, 3.6], { zebra: false }));
c.push(P("Lớp: ....................     Nhóm: ....................     Giảng viên: ........................................     Hạn nộp: ..../..../2026", { align: AlignmentType.CENTER }));
c.push(BREAK());

// ---------------- Hướng dẫn dùng khung ----------------
c.push(H1("Hướng dẫn dùng khung hồ sơ (XÓA trang này khi nộp)"));
c.push(P("Khung do SV1 dựng (thẻ SV1-12). Các ô nền vàng chữ nâu là hướng dẫn – điền xong thì xóa. Phần do SV1 phụ trách đã có nội dung; phần SV2–SV4 để trống có hướng dẫn. Sau khi điền, nhấp chuột phải vào Mục lục → Update Field → Update entire table."));
c.push(...T(["Chương", "Người viết chính", "Số trang dự kiến", "Nguồn lấy nội dung"], [
  ["1. Yêu cầu và phạm vi", "SV1", "1", "Phiếu giao đề 22 (đã điền)"],
  ["2. Giả định và lựa chọn giải pháp", "SV1", "1,5", "03_ThietKeDuLieu mục 2 (đã điền)"],
  ["3. Kiến trúc hệ thống", "SV1", "3", "01, 02, 04, 05, 06 (đã điền phần chính)"],
  ["4. Triển khai", "SV1 (4.1), SV2 (4.2), SV3 (4.3), SV4 (4.4)", "4", "Sản phẩm từng thành viên"],
  ["5. Kiểm thử", "SV4 chủ trì, cả nhóm cùng chạy", "3", "Bảng kiểm thử KT1–KT3 + tình huống lỗi"],
  ["6. Đánh giá, mở rộng và giới hạn", "SV4 + SV1", "2,5", "07_UocLuong_MoRong.xlsx + kết quả tai_thu.py"],
  ["7. Kết luận, câu hỏi chuẩn bị", "Cả nhóm", "1", ""],
  ["Tài liệu tham khảo, sử dụng AI", "Cả nhóm", "0,5", ""],
  ["Tổng phần nội dung chính", "", "12 – 18 trang", "Phụ lục cấu hình không tính vào giới hạn"],
], [3, 3, 1.4, 3]));
c.push(H2("Theo dõi thu bài (SV1 cập nhật)"));
c.push(...T(["Người", "Hạng mục cần nộp cho hồ sơ chung", "Hạn", "Đã nhận", "Ghi chú"], [
  ["SV1", "Thư mục SV1_ThietKeMang_DuLieu + chương 1–3, mục 4.1", "11/11", "☑", "Đã có"],
  ["SV2", "Mã client + README chạy + ảnh 2 điểm quét + mục 4.2 + phiếu đóng góp", "11/11", "☐", ""],
  ["SV3", "Mã server, CSDL, sao lưu/khôi phục + mục 4.3 + phiếu đóng góp", "11/11", "☐", ""],
  ["SV4", "Bảng kiểm thử KT1–KT3 có bằng chứng thời gian + kết quả tải + mục 4.4, 5, 6 + phiếu đóng góp", "11/11", "☐", ""],
  ["Cả nhóm", "Video demo 5–7 phút", "13/11", "☐", ""],
  ["SV1 + SV4", "Rà thuật ngữ, số liệu, chốt hồ sơ (SV1-13)", "13/11", "☐", "Dùng ho_so_chung/RaSoat_HoanThien.md"],
], [1, 4.5, 0.9, 0.9, 2]));
c.push(BREAK());

// ---------------- Mục lục ----------------
c.push(center("MỤC LỤC", 28));
c.push(new TableOfContents("Mục lục", { hyperlink: true, headingStyleRange: "1-2" }));
c.push(BREAK());

// ---------------- Thuật ngữ ----------------
c.push(H1("Thuật ngữ và chữ viết tắt"));
c.push(P("Cả nhóm dùng **đúng** từ ở cột “Dùng thống nhất”; không dùng các cách gọi ở cột “Không dùng” để báo cáo, sơ đồ và mã nhất quán.", { after: 60 }));
c.push(...T(["Thuật ngữ", "Dùng thống nhất", "Nghĩa trong đề tài", "Không dùng"], [
  ["Điểm quét", "điểm quét SP01, SP02 (scan_point_id)", "Vị trí đặt máy khách + máy quét mã", "trạm quét, máy scan, node"],
  ["Giao dịch", "giao dịch NHAP / XUAT", "Một lần nhập hoặc xuất một mã hàng", "phiếu, order, bản ghi quét"],
  ["Mã giao dịch", "txn_id (SPxx-yyyymmdd-nnnn)", "Định danh duy nhất do máy khách sinh", "transaction_id, txnId, mã quét"],
  ["Mã hàng", "product_code", "Nội dung mã vạch in trên hàng", "barcode, sku, product_id"],
  ["Tồn kho", "tồn (Inventory.quantity)", "Số lượng hiện có của một mã hàng", "số dư, stock"],
  ["Máy chủ", "máy chủ ứng dụng SRV-KHO", "Nơi xử lý và lưu dữ liệu chung", "server kho, host"],
  ["CSDL", "CSDL kho.db (SQLite)", "Cơ sở dữ liệu", "database, DB (trong văn bản)"],
  ["Gửi trùng", "gửi trùng mã giao dịch → 409 DUPLICATE_TXN", "Gửi lại cùng txn_id", "gửi lặp, double"],
  ["Đối chiếu", "đối chiếu tồn (v_doi_chieu_ton)", "So tồn lưu trữ với Σ NHAP − Σ XUAT", "kiểm kê, so khớp"],
  ["VLAN", "VLAN 10 / 20 / 30", "Mạng LAN ảo: máy chủ / văn phòng / điểm quét", "VLAN 99, 4 VLAN"],
  ["ACL", "ACL (danh sách kiểm soát truy cập)", "Quy tắc lọc trên R1-KHO", "firewall rule"],
  ["API", "API (giao ước v1.0)", "Giao tiếp HTTP/JSON giữa máy khách và máy chủ", ""],
  ["AuditLog", "nhật ký AuditLog", "Ghi mọi yêu cầu, kể cả bị từ chối", "log file"],
  ["PT", "Packet Tracer", "Công cụ mô phỏng mạng của Cisco", ""],
  ["NAS", "NAS-SAOLUU (mô phỏng bằng thư mục backup/)", "Thiết bị lưu bản sao lưu", ""],
  ["WAL", "Write-Ahead Logging", "Chế độ ghi của SQLite cho phép đọc khi đang ghi", ""],
  ["KT1 – KT3", "KT1, KT2, KT3", "Kiểm thử nghiệm thu tối thiểu của phiếu", "TC1, test 1"],
  ["Cổng 1 / Cổng 2", "Cổng 1, Cổng 2", "Mốc phối hợp: chốt chuẩn / xác nhận luồng dữ liệu", ""],
], [1.5, 2.8, 3.2, 2.2], { size: 19 }));

// ---------------- 1 ----------------
c.push(H1("1. Yêu cầu và phạm vi"));
c.push(P("Kho hàng có máy tính, thiết bị quét mã, máy chủ và dữ liệu nhập – xuất – tồn. Nhóm thiết kế hạ tầng CNTT phục vụ quản lý kho gồm máy tính, thiết bị quét mã, mạng nội bộ, máy chủ và lưu trữ dữ liệu; phân tích trao đổi thông tin giữa các thiết bị, tổ chức dữ liệu, quản lý người dùng, phương án sao lưu; xây dựng mô hình minh họa và đánh giá khả năng mở rộng."));
c.push(...T(["#", "Yêu cầu bắt buộc", "Đáp ứng tại"], [
  ["YC1", "Thiết kế mạng, máy chủ, lưu trữ, vai trò thủ kho / nhân viên / quản trị và luồng dữ liệu quét mã", "Chương 3, mục 4.1"],
  ["YC2", "Mô phỏng 2 điểm quét; lưu giao dịch có mã, thời gian và người thực hiện", "Mục 4.2, 4.3"],
  ["YC3", "Ghi/đọc dữ liệu mẫu, phân quyền, sao lưu; phát hiện dữ liệu trùng hoặc thao tác không hợp lệ", "Mục 4.3, 4.4, chương 5"],
  ["YC4", "Ước lượng tài nguyên khi số điểm quét tăng gấp đôi; xử lý mất mạng và đối chiếu sau khôi phục", "Chương 6"],
  ["KT1", "Ghi giao dịch hợp lệ và kiểm tra số liệu tồn mẫu", "Chương 5"],
  ["KT2", "Gửi trùng mã giao dịch, không làm thay đổi tồn hai lần", "Chương 5"],
  ["KT3", "Tài khoản chỉ xem không sửa được dữ liệu; khôi phục bản sao và đối chiếu", "Chương 5"],
], [0.7, 6, 2]));
c.push(P("Phạm vi: chỉ dùng dữ liệu giả và môi trường được phép; không mua thiết bị, không thuê Cloud, không xây ứng dụng nghiệp vụ hoàn chỉnh. Phần mạng chứng minh bằng Packet Tracer; phần ứng dụng chạy thật trên laptop của nhóm."));

// ---------------- 2 ----------------
c.push(H1("2. Giả định và lựa chọn giải pháp"));
c.push(...T(["#", "Giả định", "Ảnh hưởng"], [
  ["G1", "Kho nhỏ – vừa, một mặt bằng; 2 điểm quét (cổng nhập, cổng xuất), 3 máy văn phòng", "1 switch 24 cổng đủ dùng"],
  ["G2", "Cao điểm 1 giao dịch / 3 giây / điểm quét; 1 ca 8 giờ; 300 ngày/năm", "Căn cứ ước lượng chương 6"],
  ["G3", "Chạy nội bộ, không phụ thuộc Internet", "Không cần NAT/VPN"],
  ["G4", "Máy quét mã vạch hoạt động kiểu bàn phím", "Mô phỏng bằng nhập bàn phím là tương đương"],
  ["G5–G6", "Mỗi giao dịch 1 mã hàng; chỉ dữ liệu giả, không có kế toán", "Mô hình nhập – xuất – tồn gọn"],
  ["G7", "Python 3 + SQLite + HTTP/JSON", "Ai cũng dựng lại được, không cài thêm"],
], [0.8, 5, 3]));
c.push(...T(["Thành phần", "Lựa chọn", "Phương án khác đã cân nhắc", "Lý do chọn"], [
  ["Phân vùng mạng", "3 VLAN + router-on-a-stick + ACL", "Một mạng phẳng", "Cô lập điểm quét khỏi NAS và văn phòng"],
  ["Xử lý dữ liệu", "Một máy chủ ứng dụng trung tâm", "Mỗi điểm quét tự ghi CSDL", "Tránh ghi đè, phân quyền ở một chỗ"],
  ["CSDL", "SQLite (WAL)", "PostgreSQL / MySQL", "Không cần cài đặt; đủ cho tải ước lượng"],
  ["Chống ghi trùng", "txn_id do máy khách sinh + khóa chính", "Máy chủ cấp mã", "Gửi lại khi mất mạng vẫn an toàn"],
  ["Sao lưu", "Bản sao file kho.db sang NAS / thư mục backup", "Sao chép CSDL thời gian thực", "Đơn giản, đủ cho KT3"],
], [1.6, 2.6, 2.4, 3]));
c.push(TODO("SV1: nếu nhóm làm phần Mở rộng tự chọn, ghi thêm phương án thay thế đã triển khai ở đây"));

// ---------------- 3 ----------------
c.push(H1("3. Kiến trúc hệ thống"));
c.push(H2("3.1. Sơ đồ hạ tầng"));
c.push(IMG(path.join(ROOT, "01_SoDoHaTang.png"), 605));
c.push(CAP("Hình 3.1. Sơ đồ hạ tầng CNTT kho hàng – 3 VLAN, phần chạy thật / chỉ trên sơ đồ"));
c.push(P("Bốn lớp: thiết bị đầu cuối (2 điểm quét, 3 máy văn phòng) – mạng nội bộ (SW1-KHO 3 VLAN, R1-KHO định tuyến và ACL, AP-KHO Wi-Fi) – máy chủ ứng dụng SRV-KHO 192.168.10.10:8080 – lưu trữ (CSDL kho.db, NAS-SAOLUU). Điểm quét chỉ được gọi API của máy chủ; không chạm CSDL hay NAS. Chi tiết: bảng IP và 13 quy tắc truy cập trong phụ lục A."));
c.push(H2("3.2. Mô hình dữ liệu"));
c.push(IMG(path.join(ROOT, "02_MoHinhDuLieu.png"), 605));
c.push(CAP("Hình 3.2. Mô hình dữ liệu – 5 bảng bắt buộc và AuditLog"));
c.push(P("Products 1–1 Inventory; Products, Users, ScanPoints quan hệ 1–N với Transactions; AuditLog liên kết logic qua txn_id. Bất biến: tồn = Σ NHAP − Σ XUAT. Từ điển 38 trường: 06_TuDienDuLieu.md."));
c.push(H2("3.3. Luồng dữ liệu quét mã"));
c.push(IMG(path.join(ROOT, "04_SoDoLuongDuLieu.png"), 605));
c.push(CAP("Hình 3.3. Quét → gửi → kiểm tra → lưu → cập nhật tồn → phản hồi, có nhánh lỗi, trùng, mất mạng"));
c.push(H2("3.4. Người dùng và quyền"));
c.push(...T(["Vai trò", "Tài khoản mẫu", "Ghi giao dịch", "Đọc tồn / lịch sử", "Danh mục hàng", "Tài khoản, sao lưu, khôi phục"], [
  ["ADMIN (quản trị)", "admin", "✔", "✔ / ✔", "✔", "✔"],
  ["THUKHO (thủ kho)", "thukho01", "✔", "✔ / ✔", "✔", "✘"],
  ["NHANVIEN (nhân viên)", "nv01, nv02", "✔", "✔ / chỉ của mình", "✘", "✘"],
  ["QUANLY (chỉ xem – KT3)", "quanly01", "✘ (403)", "✔ / ✔", "✘", "✘"],
], [2.2, 1.6, 1.3, 1.8, 1.3, 2], { center: [2, 3, 4, 5] }));

// ---------------- 4 ----------------
c.push(H1("4. Triển khai"));
c.push(H2("4.1. Mạng và mô hình Packet Tracer (SV1)"));
c.push(P("Mô hình Packet Tracer gồm R1-KHO (2911), SW1-KHO (2960-24TT), AP-KHO, SRV-KHO, NAS-SAOLUU, 3 PC văn phòng, SCAN-01 (có dây), SCAN-02 (Wi-Fi). Cấu hình nạp từ cau_hinh/*.txt; 13 phép kiểm tra N1–N13 theo HuongDan_PacketTracer.md."));
c.push(TODO("SV1: chèn ảnh topo Packet Tracer và ảnh N4 (ping máy chủ thành công), N7 (ping NAS bị chặn), N10 (show access-lists) có đồng hồ hệ thống"));
c.push(H2("4.2. Hai điểm quét giả lập (SV2)"));
c.push(TODO("SV2: mô tả client (ngôn ngữ, cách chạy), cách sinh txn_id, hàng đợi khi mất mạng, cách hiển thị kết quả 201/409/lỗi; ảnh 2 cửa sổ SP01, SP02 đang chạy; tham chiếu file mã"));
c.push(H2("4.3. Lưu trữ, phân quyền và sao lưu (SV3)"));
c.push(TODO("SV3: mô tả server API theo giao ước v1.0, CSDL tạo từ schema.sql, cách kiểm tra quyền theo token, quy trình sao lưu (tên file, nơi lưu, lịch) và khôi phục; ảnh minh chứng"));
c.push(H2("4.4. Kiểm tra nhất quán và xử lý lỗi (SV4)"));
c.push(TODO("SV4: cách phát hiện trùng, thao tác không hợp lệ; quy trình đối chiếu sau mất mạng và sau khôi phục; kết quả /api/reconcile"));
c.push(H2("4.5. Phần việc SV5 (nếu nhóm 5 người)"));
c.push(TODO("SV5: theo hướng dẫn chung của học phần – xóa mục này nếu nhóm 4 người"));

// ---------------- 5 ----------------
c.push(H1("5. Kiểm thử"));
c.push(P("Mọi thành viên cùng tham gia chạy kiểm thử. Mỗi dòng phải có bằng chứng có dấu thời gian (ảnh màn hình thấy đồng hồ, hoặc file kết quả có thời điểm chạy).", { after: 60 }));
c.push(...T(["Mã", "Đầu vào", "Thao tác", "Kết quả mong đợi", "Thực tế", "Đạt / Chưa", "Bằng chứng (file, thời gian)"], [
  ["KT1", "nv01, SP01, SP001, NHAP 20; tồn trước 100", "Quét/nhập tại client SP01", "201 OK; tồn SP001 = 120; Transactions có txn_id, thời gian, nv01", "", "", ""],
  ["KT2", "Gửi lại đúng txn_id của KT1", "Gửi lại từ client (hoặc ngắt mạng rồi gửi lại)", "409 DUPLICATE_TXN; tồn vẫn 120; số dòng Transactions không đổi", "", "", ""],
  ["KT3a", "quanly01, NHAP 10 SP001", "Đăng nhập quanly01 rồi ghi", "403 FORBIDDEN; tồn không đổi; AuditLog REJECTED", "", "", ""],
  ["KT3b", "Bản sao lưu kho_yyyymmdd_hhmm.db", "ADMIN khôi phục bản sao, gọi /api/reconcile", "Khôi phục thành công; all_match = true; chenh_lech = 0 mọi mã", "", "", ""],
  ["TC-L1", "XUAT 51 SP002 khi tồn 50", "Gửi từ SP02", "422 INSUFFICIENT_STOCK; tồn không đổi", "", "", ""],
  ["TC-L2", "Mã hàng SP999", "Gửi từ SP01", "404 PRODUCT_NOT_FOUND", "", "", ""],
  ["TC-L3", "Số lượng 0 / −5", "Gửi từ SP01", "400 INVALID_QUANTITY", "", "", ""],
  ["TC-M1", "Ngắt mạng SP01, quét 3 giao dịch, nối lại", "Quan sát hàng đợi client", "Tự gửi lại cùng txn_id; tồn đổi đúng 3 lần; đối chiếu khớp", "", "", ""],
  ["TC-T1", "tai_thu.py nhịp 3 s, 2 rồi 4 tiến trình", "SV4 chạy trên máy chủ SV3", "Lỗi khác = 0; 409 = 100% gửi trùng; all_match = true; p95 ≤ 500 ms", "", "", ""],
], [0.7, 1.7, 1.5, 2.3, 1.1, 0.7, 1.4], { size: 18 }));
c.push(TODO("SV4: điền cột Thực tế, Đạt/Chưa, Bằng chứng; thêm dòng nếu nhóm kiểm thử thêm"));

// ---------------- 6 ----------------
c.push(H1("6. Đánh giá, mở rộng và giới hạn"));
c.push(H2("6.1. Ước lượng tài nguyên khi tăng từ 2 lên 4 điểm quét"));
c.push(P("Ước lượng theo giả định G2 và số đo 301 byte/giao dịch (07_UocLuong_MoRong.xlsx). **Đây là ước lượng, chưa đo thực tế**; cột “Đo thực tế” do SV4 điền từ kết quả tai_thu.py trên máy chủ SV3.", { after: 60 }));
c.push(...T(["Chỉ tiêu", "Ước lượng 2 điểm", "Ước lượng 4 điểm", "Giới hạn", "Đo thực tế 4 điểm", "Nhận xét"], [
  ["Tải đỉnh (GD/s)", "0,67", "1,33", "50 (G10)", "", ""],
  ["Băng thông đỉnh (kbit/s)", "10,9", "21,8", "100.000", "", ""],
  ["CSDL tăng/ngày, đỉnh (MB)", "5,78", "11,56", "—", "", ""],
  ["Sao lưu 11 bản, cận trên (GB)", "19,1", "38,1", "1.000", "", ""],
  ["Cổng có dây / máy Wi-Fi", "1 / 1", "2 / 2", "7 / 25", "", ""],
  ["Độ trễ p95 (ms)", "—", "—", "≤ 500", "", ""],
], [2.6, 1.3, 1.3, 1.2, 1.4, 2]));
c.push(TODO("SV4 + SV1: kết luận thành phần nào cần nâng cấp; giải thích sai lệch ước lượng – đo nếu > 30%"));
c.push(H2("6.2. Xử lý mất mạng và đối chiếu dữ liệu sau khôi phục"));
c.push(P("Máy khách giữ hàng đợi, gửi lại sau 5 → 10 → 20 giây với cùng txn_id; máy chủ trả 409 cho giao dịch đã lưu nên tồn không bị cộng lặp. Sau khôi phục bản sao, gọi /api/reconcile (view v_doi_chieu_ton) – mọi mã hàng phải có chênh lệch 0; các giao dịch sau thời điểm sao lưu được gửi lại từ hàng đợi máy khách / AuditLog."));
c.push(TODO("SV4: số liệu thực tế của TC-M1 và KT3b"));
c.push(H2("6.3. Giới hạn"));
c.push(B("Packet Tracer chỉ chứng minh cấu hình và kết nối; không khẳng định thông lượng, vùng phủ Wi-Fi hay khả năng chịu tải thật."));
c.push(B("NAS mô phỏng bằng thư mục trên cùng laptop; máy quét mô phỏng bằng nhập bàn phím."));
c.push(B("Định dạng txn_id 4 chữ số giới hạn 9.999 giao dịch/ngày/điểm quét (96% ở tải đỉnh 1 ca)."));
c.push(H2("6.4. Mở rộng tự chọn (nếu có)"));
c.push(TODO("Nhóm: phương án thay thế cho một thành phần (VD: SQLite → PostgreSQL, hoặc txn_id → UUID), triển khai, kiểm thử và so sánh bằng cùng tiêu chí, cùng số liệu. Xóa mục nếu không làm"));

// ---------------- 7 ----------------
c.push(H1("7. Kết luận và câu hỏi chuẩn bị"));
c.push(TODO("Cả nhóm: kết luận 5–8 dòng: đã đáp ứng YC1–YC4, KT1–KT3 thế nào"));
c.push(P("**Vì sao quét thành công chưa chứng minh máy chủ đã lưu giao dịch?** Tiếng “bíp” chỉ xác nhận máy đọc được mã. Gói tin có thể mất khi gửi hoặc khi phản hồi, máy chủ có thể từ chối (trùng, sai mã hàng, không đủ tồn, không có quyền) hoặc lỗi trước COMMIT. Chỉ phản hồi 201 OK – gửi sau khi COMMIT – hoặc 409 (đã lưu từ trước), hoặc tra GET /api/transactions/{txn_id} mới chứng minh giao dịch đã nằm trong CSDL."));

// ---------------- TLTK ----------------
c.push(H1("Tài liệu tham khảo"));
["Phiếu giao đề 22 và hướng dẫn chung học phần RIPT1304 – Viện Khoa học Kỹ thuật Bưu điện, PTIT.",
 "Cisco Networking Academy – Packet Tracer; cấu hình VLAN, 802.1Q, router-on-a-stick, extended ACL, port-security.",
 "IEEE 802.1Q; RFC 1918 (địa chỉ riêng); RFC 9110 (HTTP Semantics).",
 "SQLite Documentation – CREATE TABLE, FOREIGN KEY, CHECK, TRIGGER, BEGIN IMMEDIATE, WAL.",
 "Python 3 Documentation – sqlite3, http.server, urllib, multiprocessing."].forEach((s, i) => c.push(P(`[${i + 1}] ${s}`, { after: 60 })));
c.push(TODO("Mỗi thành viên bổ sung tài liệu / mã nguồn tham khảo đã dùng"));
c.push(H1("Sử dụng AI"));
c.push(TODO("Mỗi thành viên ghi rõ phần nào dùng AI hỗ trợ, công cụ nào, và đã tự kiểm tra / chỉnh sửa / chạy lại những gì. SV1: tài liệu thiết kế, cấu hình mẫu, script và sơ đồ soạn với hỗ trợ của Claude (Anthropic); SV1 đã chạy lại toàn bộ script và chịu trách nhiệm giải thích"));

// ---------------- Phụ lục ----------------
c.push(BREAK());
c.push(H1("Phụ lục A. Cấu hình và bảng tài nguyên"));
c.push(P("Không tính vào giới hạn trang. Đính kèm nguyên văn: cau_hinh/R1-KHO_router.txt, SW1-KHO_switch.txt, AP-KHO_wifi.txt; BangDiaChiIP.csv; QuyTacTruyCap.csv; du_lieu/schema.sql; 05_GiaoUocAPI.md; 06_TuDienDuLieu.md; cấu hình / mã nguồn của SV2, SV3."));
c.push(H1("Phụ lục B. Danh mục minh chứng"));
c.push(...T(["Người", "File / thư mục", "Nội dung", "Có dấu thời gian", "Đã nộp"], [
  ["SV1", "01_SoDoHaTang.png, cau_hinh/, BangDiaChiIP.csv, QuyTacTruyCap.csv", "Sơ đồ mạng 3 VLAN, IP, ACL", "—", "☑"],
  ["SV1", "02_MoHinhDuLieu.png, 06_TuDienDuLieu.md, schema.sql", "Mô hình và từ điển dữ liệu", "—", "☑"],
  ["SV1", "03_ThietKeDuLieu.docx/.pdf, 04_SoDoLuongDuLieu.png, 05_GiaoUocAPI.md", "Thiết kế, luồng dữ liệu, API, ma trận quyền", "—", "☑"],
  ["SV1", "du_lieu/ketqua_kiemtra.txt, ketqua_do_dung_luong.txt", "Kiểm chứng 11/11; 301 B/giao dịch", "Có", "☑"],
  ["SV1", "cong_phoi_hop/Cong1_*.docx, Cong2_*.docx, ket_qua/", "Biên bản Cổng 1, Cổng 2", "Có", "☐ (chờ ký)"],
  ["SV1", "doi_chieu/BangDoiChieuTenTruong.md, NhatKyThayDoi.md", "Đối chiếu tên trường SV2/SV3", "Có", "☐ (chờ mã SV2/SV3)"],
  ["SV1", "07_UocLuong_MoRong.xlsx, uoc_luong/BanGiao_SV4.md, tai_thu/", "Ước lượng, bàn giao SV4, script tải", "Có", "☑"],
  ["SV1", "KhoHang_DeTai22.pkt + ảnh N1–N13", "Mô hình Packet Tracer", "Có", "☐"],
  ["SV2", "", "", "", "☐"],
  ["SV3", "", "", "", "☐"],
  ["SV4", "", "", "", "☐"],
], [0.8, 3.6, 2.6, 1.2, 1.3], { size: 19 }));

c.push(H1("Phụ lục C. Phiếu đóng góp cá nhân"));
c.push(H2("C.1. SV1 – Thiết kế mạng và mô hình dữ liệu"));
c.push(...T(["Mục", "Nội dung"], [
  ["Họ tên / MSSV", ".................................... / ...................."],
  ["Nhiệm vụ", "CV01: sơ đồ mạng 3 VLAN, bảng IP, quy tắc truy cập; mô hình dữ liệu + từ điển; luồng dữ liệu; giao ước API + ma trận quyền; chủ trì Cổng 1, dự Cổng 2; đối chiếu tên trường; mô hình ước lượng 2 → 4 điểm quét, giao SV4; script tải; khung và hoàn thiện hồ sơ chung"],
  ["File tạo ra", "01, 02, 03, 04, 05, 06, 07; cau_hinh/*; du_lieu/* (schema, seed, 3 script); cong_phoi_hop/*; doi_chieu/*; tai_thu/*; uoc_luong/*; cong_cu_thu/may_chu_gia_lap.py; ho_so_chung/*"],
  ["Bằng chứng", "ketqua_kiemtra.txt (11/11 đạt); ketqua_do_dung_luong.txt (301 B/GD); xuat_tu_dien.py (38/38 trường khớp schema); Cổng 2 chạy thử 10/10; tai_thu 2/4 tiến trình: 0 lỗi lạ, 409 = 100% gửi trùng; bảng Excel 0 ô lỗi công thức"],
  ["Lỗi đã xử lý", "(1) Thiết kế đầu có 4 VLAN → rút về 3 VLAN theo yêu cầu, chuyển IP quản lý switch vào VLAN 10. (2) Script tải dùng lại số thứ tự txn_id giữa 2 kịch bản → chia vùng số thứ tự riêng. (3) Cổng 8080 trên máy bị chương trình khác chiếm → thêm tham số --port/--url. (4) Excel hiển thị sai định dạng số trên máy cài tiếng Việt → gán định dạng theo en-US, thay TEXT() bằng FIXED(). (5) Bảng đối chiếu báo “khớp” khi chưa có mã → sửa thành “Chờ mã SV2/SV3”. (6) File Word lỗi cấu trúc do chèn khối mã sai → sửa script dựng tài liệu."],
  ["Tự đánh giá mức hoàn thành", "......%"],
  ["Xác nhận của nhóm", ""],
], [1.8, 7]));
["SV2 – Dựng hai điểm quét giả lập", "SV3 – Triển khai lưu trữ, quyền và sao lưu", "SV4 – Kiểm tra nhất quán, lỗi và mở rộng"].forEach((t, i) => {
  c.push(H2(`C.${i + 2}. ${t}`));
  c.push(...T(["Mục", "Nội dung"], [["Họ tên / MSSV", ""], ["Nhiệm vụ", ""], ["File tạo ra", ""], ["Bằng chứng", ""], ["Lỗi đã xử lý", ""], ["Tự đánh giá mức hoàn thành", "......%"], ["Xác nhận của nhóm", ""]], [1.8, 7], { zebra: false }));
});

(async () => {
  await save(makeDoc(c, { title: "Hồ sơ chung – Đề tài 22", footer: "Đề tài 22 – Hồ sơ chung · Trang ", toc: true }), OUT);
  console.log("OK");
})();
