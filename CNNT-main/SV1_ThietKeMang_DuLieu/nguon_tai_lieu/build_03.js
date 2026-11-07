const fs = require("fs");
const path = require("path");
const { d, P, H1, H2, B, N, CODE, BREAK, CAP, IMG, T, readCsv, makeDoc, save } = require("./lib_docx");
const { Paragraph, TextRun, AlignmentType } = d;

const ROOT = "D:\\Son_Work_Space\\Dự_án_Liên\\SV1_ThietKeMang_DuLieu";
const p = (...a) => path.join(ROOT, ...a);
const IMGW = 605;

// ---- dữ liệu nguồn ----
const ip = readCsv(p("cau_hinh", "BangDiaChiIP.csv"));
const acl = readCsv(p("cau_hinh", "QuyTacTruyCap.csv"));
const dict = readCsv(p("du_lieu", "TuDienDuLieu.csv"));
const kq = fs.readFileSync(p("du_lieu", "ketqua_kiemtra.txt"), "utf8").split(/\r?\n/);
const tcs = [];
for (let i = 0; i < kq.length; i++) {
  const m = kq[i].match(/^\[(.+?)\] (TC\d+) \| (.+)$/);
  if (m) tcs.push([m[2], m[3], kq[i + 1].replace(/^\s*->\s*/, ""), kq[i + 2].replace(/^\s*=>\s*/, ""), m[1].replace("T", " ")]);
}
const runTime = (kq.find((l) => l.startsWith("Thời điểm chạy")) || "").split(": ")[1];
const sqliteVer = (kq.find((l) => l.startsWith("Python")) || "");

const c = [];

// ---- Trang bìa ----
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 60 }, children: [new TextRun({ text: "HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG", bold: true, size: 26 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "Học phần: Nhập môn Công nghệ nền tảng (RIPT1304)", size: 26 })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: "ĐỀ TÀI 22", bold: true, size: 32, color: "1F3864" })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 400 }, children: [new TextRun({ text: "THIẾT KẾ HẠ TẦNG CNTT CHO HỆ THỐNG QUẢN LÝ KHO HÀNG THÔNG MINH", bold: true, size: 34, color: "1F3864" })] }));
c.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 }, children: [new TextRun({ text: "TÀI LIỆU THIẾT KẾ MẠNG VÀ MÔ HÌNH DỮ LIỆU (03_ThietKeDuLieu)", bold: true, size: 28 })] }));
c.push(...T(["Mục", "Nội dung"], [
  ["Phần việc", "SV1 – CV01: Thiết kế mạng và mô hình dữ liệu"],
  ["Người thực hiện", "Họ tên: ................................   MSSV: ....................."],
  ["Lớp / Nhóm", "Lớp: ....................   Nhóm: ...................."],
  ["Phiên bản", "v1.0 – 26/10/2026 (bản bàn giao tại Cổng 1)"],
  ["Tài liệu kèm theo", "01_SoDoHaTang.png · 02_MoHinhDuLieu.png · 04_SoDoLuongDuLieu.png · 05_GiaoUocAPI.md · 06_TuDienDuLieu.md · cau_hinh/ · du_lieu/"],
], [1, 3], { zebra: false }));
c.push(BREAK());

// ---- 1 ----
c.push(H1("1. Mục tiêu và phạm vi phần việc"));
c.push(P("Phần việc SV1 xác định **kiến trúc hạ tầng CNTT** của kho hàng thông minh: thiết bị nào kết nối với nhau ra sao, dữ liệu được xử lý ở đâu, lưu ở đâu và được tổ chức thành những bảng nào. Tài liệu này là **chuẩn chung** để SV2 (dựng hai điểm quét), SV3 (lưu trữ, phân quyền, sao lưu) và SV4 (kiểm tra nhất quán, lỗi, mở rộng) triển khai thống nhất: cùng địa chỉ, cùng tên trường, cùng quy tắc giao dịch và cùng danh sách mã lỗi."));
c.push(...T(["Công việc CV01", "Mục trong tài liệu", "Minh chứng"], [
  ["1. Sơ đồ mạng và kiến trúc hệ thống", "3, 4, 5", "01_SoDoHaTang.png, cau_hinh/*.txt, BangDiaChiIP.csv, QuyTacTruyCap.csv"],
  ["2. Mô hình dữ liệu", "6, 7", "02_MoHinhDuLieu.png, 06_TuDienDuLieu.md, du_lieu/schema.sql"],
  ["3. Quy tắc luồng dữ liệu", "8, 9", "04_SoDoLuongDuLieu.png, 05_GiaoUocAPI.md"],
  ["Kiểm chứng thiết kế", "10", "du_lieu/kiem_tra_thiet_ke.py, ketqua_kiemtra.txt"],
  ["4. Bàn giao thiết kế cho nhóm", "11, 13", "Toàn bộ thư mục SV1_ThietKeMang_DuLieu"],
], [3, 1.4, 4]));

// ---- 2 ----
c.push(H1("2. Giả định thiết kế"));
c.push(P("Đề bài không cho quy mô cụ thể nên nhóm thống nhất các giả định dưới đây. Mọi con số ước lượng trong tài liệu đều suy ra từ các giả định này; nếu giảng viên thay đổi giả định, chỉ cần tính lại theo cùng công thức."));
c.push(...T(["#", "Giả định", "Ảnh hưởng tới thiết kế"], [
  ["G1", "Kho quy mô nhỏ – vừa, một mặt bằng; 2 điểm quét (cổng nhập, cổng xuất) và 3 máy văn phòng", "Một switch 24 cổng đủ dùng, không cần mạng nhiều tầng"],
  ["G2", "Cường độ quét lúc cao điểm: 1 giao dịch / 3 giây / điểm quét; 1 ca 8 giờ; 300 ngày làm việc/năm", "Căn cứ ước lượng băng thông, dung lượng, tải máy chủ"],
  ["G3", "Hệ thống chạy hoàn toàn trong mạng nội bộ, không phụ thuộc Internet", "Không cần NAT/VPN; mất Internet không làm ngừng kho"],
  ["G4", "Máy quét mã vạch USB/Wi-Fi hoạt động kiểu bàn phím (keyboard-wedge): đọc mã rồi “gõ” chuỗi ký tự", "Mô phỏng bằng cách gõ mã hoặc đọc file danh sách mã là tương đương"],
  ["G5", "Mỗi giao dịch là một mã hàng; nhiều đơn vị cùng mã thì nhập số lượng", "Bảng Transactions có cột quantity"],
  ["G6", "Chỉ dùng dữ liệu giả; không có nghiệp vụ kế toán, giá tiền, nhà cung cấp", "Mô hình dữ liệu tập trung vào nhập – xuất – tồn"],
  ["G7", "Nhóm dùng Python 3 + SQLite (có sẵn, không cần cài đặt) để ai cũng dựng lại được trên laptop", "CSDL là một file kho.db; quyền kiểm soát ở tầng ứng dụng"],
  ["G8", "Không mua thiết bị, không thuê Cloud; phần mạng chứng minh bằng Packet Tracer", "Xem mục 5: phần chạy thật và phần chỉ có trên sơ đồ"],
], [0.5, 4.5, 3.5]));

// ---- 3 ----
c.push(H1("3. Kiến trúc hạ tầng"));
c.push(H2("3.1. Sơ đồ kiến trúc"));
c.push(IMG(p("01_SoDoHaTang.png"), IMGW));
c.push(CAP("Hình 1. Sơ đồ hạ tầng CNTT kho hàng – 4 lớp: thiết bị đầu cuối, mạng nội bộ, máy chủ xử lý, lưu trữ (01_SoDoHaTang.png)"));
c.push(P("Hệ thống được chia thành bốn lớp rõ ràng, đúng yêu cầu phân biệt của đề:"));
c.push(B("**Thiết bị đầu cuối**: hai điểm quét (SCAN-01 có dây ở cổng nhập, SCAN-02 dùng Wi-Fi ở cổng xuất) và ba máy văn phòng cho thủ kho, quản trị, người quản lý."));
c.push(B("**Mạng nội bộ**: một switch SW1-KHO chia 3 VLAN, một router/firewall R1-KHO định tuyến giữa các VLAN và lọc truy cập, một điểm phát Wi-Fi AP-KHO cho máy quét cầm tay."));
c.push(B("**Máy chủ xử lý**: SRV-KHO chạy ứng dụng tiếp nhận API, xác thực, kiểm tra quy tắc, ghi giao dịch và trả kết quả."));
c.push(B("**Lưu trữ dữ liệu**: CSDL kho.db nằm trên ổ SSD của SRV-KHO; bản sao lưu đặt trên NAS-SAOLUU tách biệt."));
c.push(H2("3.2. Thành phần và cấu hình đề xuất"));
c.push(...T(["Lớp", "Thành phần", "Vai trò", "Cấu hình đề xuất khi triển khai thật"], [
  ["Đầu cuối", "SCAN-01, SCAN-02", "Đọc mã, sinh mã giao dịch, gửi lên máy chủ, giữ hàng đợi khi mất mạng", "PC mini/laptop + máy quét mã vạch USB; hoặc máy quét cầm tay Android Wi-Fi"],
  ["Đầu cuối", "PC-THUKHO, PC-QUANTRI, PC-QUANLY", "Ghi/xem dữ liệu, quản trị, xem báo cáo", "Máy văn phòng phổ thông, trình duyệt web"],
  ["Mạng", "SW1-KHO", "Chuyển mạch, chia VLAN, port-security", "Switch quản lý được 24 cổng 10/100/1000, hỗ trợ 802.1Q, có PoE cho AP"],
  ["Mạng", "R1-KHO", "Gateway, định tuyến liên VLAN, DHCP, ACL", "Router/firewall SME, ≥ 2 cổng GE"],
  ["Mạng", "AP-KHO", "Wi-Fi riêng cho máy quét (SSID KHO-QUETMA)", "AP Wi-Fi 5/6 gắn trần, WPA2/WPA3; khảo sát sóng thực tế trước khi lắp"],
  ["Xử lý", "SRV-KHO", "Ứng dụng kho (API :8080) + CSDL + DNS kho.local", "CPU 4 nhân, RAM 8 GB, SSD 2 × 256 GB RAID 1, UPS 1 kVA"],
  ["Lưu trữ", "kho.db", "CSDL SQLite (6 bảng + view đối chiếu)", "Trên SSD của SRV-KHO, chế độ WAL"],
  ["Lưu trữ", "NAS-SAOLUU", "Giữ bản sao lưu, tách khỏi máy chủ", "NAS 2 khay, 2 × 1 TB RAID 1"],
], [1, 1.6, 2.6, 3]));
c.push(H2("3.3. Vì sao cần máy chủ – một nơi xử lý dữ liệu chung"));
c.push(P("Hai điểm quét cùng thay đổi một con số tồn kho. Nếu mỗi máy tự giữ dữ liệu, SP01 nhập 20 và SP02 xuất 30 sẽ cho hai con số tồn khác nhau và không ai biết số nào đúng. Đặt **một máy chủ duy nhất** giữ CSDL giúp: (1) mọi giao dịch được kiểm tra theo cùng một bộ quy tắc; (2) hai yêu cầu đến cùng lúc được xếp hàng ghi lần lượt (khóa ghi BEGIN IMMEDIATE), không ghi đè nhau; (3) phân quyền, phát hiện trùng và sao lưu chỉ cần làm ở một chỗ; (4) máy khách mất mạng hay hỏng cũng không mất dữ liệu đã lưu."));
c.push(H2("3.4. Hai điểm quét gửi dữ liệu về hệ thống chung như thế nào"));
c.push(P("Hai điểm quét **không chạm trực tiếp vào CSDL**. Mỗi điểm quét gửi yêu cầu HTTP/JSON `POST /api/transactions` tới SRV-KHO cổng 8080. Gói tin đi SCAN → SW1 → R1 (định tuyến VLAN 30 → VLAN 10 và kiểm tra ACL) → SW1 → SRV-KHO; SCAN-02 đi qua AP-KHO trước khi vào SW1. Máy chủ là tiến trình duy nhất mở file kho.db, nên hai điểm quét dùng chung một CSDL nhưng không bao giờ tranh nhau ghi file. Mỗi giao dịch mang `scan_point_id` và tiền tố `txn_id` riêng (SP01-…, SP02-…) nên luôn biết giao dịch đến từ đâu và không bao giờ trùng mã giữa hai điểm."));

// ---- 4 ----
c.push(H1("4. Quy hoạch mạng"));
c.push(H2("4.1. Ba VLAN"));
c.push(...T(["VLAN", "Tên", "Dải địa chỉ", "Gateway", "Thành phần", "Lý do tách riêng"], [
  ["10", "MAYCHU", "192.168.10.0/24", "192.168.10.1", "SRV-KHO, NAS-SAOLUU, IP quản lý SW1 (.2)", "Vùng chứa dữ liệu – bảo vệ chặt nhất"],
  ["20", "VANPHONG", "192.168.20.0/24", "192.168.20.1", "PC-THUKHO, PC-QUANTRI, PC-QUANLY", "Người dùng văn phòng, có quyền rộng hơn điểm quét"],
  ["30", "QUETMA", "192.168.30.0/24", "192.168.30.1", "SCAN-01, SCAN-02, AP-KHO, máy quét mở rộng", "Thiết bị ở khu kho, dễ bị cắm thiết bị lạ – chỉ cho gọi API"],
], [0.6, 1.2, 1.7, 1.4, 2.6, 2.5]));
c.push(P("Mỗi VLAN dùng mạng /24 (253 địa chỉ dùng được). Dải .1–.99 dành cho địa chỉ tĩnh; R1 cấp DHCP .100–.254 cho thiết bị mới ở VLAN 20 và 30. Router dùng mô hình router-on-a-stick: một cổng G0/0 chia ba cổng con G0/0.10, G0/0.20, G0/0.30 theo 802.1Q; switch nối lên bằng một đường trunk G0/1 chỉ cho phép VLAN 10, 20, 30."));
c.push(H2("4.2. Bảng địa chỉ IP"));
c.push(...T(["Thiết bị", "VLAN", "Địa chỉ IP", "Gateway", "Cổng switch", "Chạy thật / chỉ trên sơ đồ"],
  ip.map((r) => [r["Thiết bị"], r["VLAN"], r["Địa chỉ IP"], r["Gateway"], r["Cổng switch"], r["Chạy thật hay chỉ trên sơ đồ"]]),
  [1.6, 0.8, 2, 1.3, 1.5, 2.8], { size: 19 }));
c.push(P("Bảng đầy đủ (loại thiết bị Packet Tracer, DNS, dịch vụ mở) nằm ở `cau_hinh/BangDiaChiIP.csv`."));
c.push(H2("4.3. Quy tắc truy cập"));
c.push(P("Nguyên tắc: **điểm quét chỉ được làm đúng một việc là gọi API của máy chủ**; chỉ máy quản trị được quản trị máy chủ và thiết bị mạng; NAS sao lưu chỉ nói chuyện với SRV-KHO. Các quy tắc được cài bằng ACL mở rộng trên R1-KHO (chiều vào ở cổng con của VLAN 20 và 30) và port-security trên SW1-KHO."));
c.push(...T(["#", "Nguồn", "Đích", "Dịch vụ", "Hành động", "Lý do"],
  acl.map((r) => [r["STT"], r["Nguồn"], r["Đích"], r["Dịch vụ / cổng"], r["Hành động"], r["Lý do"]]),
  [0.4, 1.8, 1.8, 1.5, 1.1, 2.6], { size: 19 }));
c.push(H2("4.4. Cổng dịch vụ và kiểm tra cấu hình"));
c.push(...T(["Dịch vụ", "Cổng", "Trên máy", "Dùng cho"], [
  ["API kho hàng", "TCP 8080", "SRV-KHO", "Điểm quét, văn phòng gửi/đọc dữ liệu"],
  ["HTTP", "TCP 80", "SRV-KHO", "Trang minh chứng trong Packet Tracer (Server-PT chỉ hỗ trợ cổng 80)"],
  ["DNS", "UDP 53", "SRV-KHO", "Phân giải kho.local → 192.168.10.10"],
  ["SSH", "TCP 22", "SRV-KHO, NAS", "Quản trị từ PC-QUANTRI"],
  ["Telnet", "TCP 23", "SW1-KHO", "Cấu hình switch từ PC-QUANTRI (trong mô hình)"],
  ["SMB / SSH", "TCP 445 / 22", "NAS-SAOLUU", "SRV-KHO chép bản sao lưu"],
  ["DHCP", "UDP 67/68", "R1-KHO", "Cấp địa chỉ cho thiết bị mới"],
], [1.6, 1.3, 1.6, 4]));
c.push(P("Cấu hình đầy đủ: `cau_hinh/R1-KHO_router.txt`, `SW1-KHO_switch.txt`, `AP-KHO_wifi.txt`. Hướng dẫn dựng file .pkt và 13 phép kiểm tra N1–N13 (ping thành công tới máy chủ, ping thất bại tới NAS/văn phòng từ điểm quét, show access-lists, port-security err-disabled…) nằm trong `cau_hinh/HuongDan_PacketTracer.md`."));

// ---- 5 ----
c.push(H1("5. Triển khai thực tế và phần mô phỏng"));
c.push(P("Theo quy tắc của học phần, nhóm không mua thiết bị hay thuê Cloud. Bảng dưới ghi rõ **thành phần nào chạy thật** (có thao tác và bằng chứng chạy được) và **thành phần nào chỉ thể hiện trên sơ đồ / Packet Tracer**."));
c.push(...T(["Thành phần", "Triển khai thật", "Khi mô phỏng", "Trạng thái"], [
  ["Điểm quét SP01, SP02", "PC/máy quét cầm tay ở cổng nhập, cổng xuất", "2 tiến trình client của SV2 (2 cửa sổ dòng lệnh hoặc 2 laptop)", "CHẠY THẬT"],
  ["Máy quét mã vạch", "Thiết bị USB/Wi-Fi", "Gõ mã từ bàn phím hoặc đọc file danh sách mã (tương đương – giả định G4)", "CHẠY THẬT"],
  ["Máy chủ ứng dụng", "SRV-KHO 192.168.10.10", "server của SV3 trên laptop, cổng 8080", "CHẠY THẬT"],
  ["CSDL", "kho.db trên SSD máy chủ", "File SQLite tạo từ schema.sql + seed_data.sql", "CHẠY THẬT"],
  ["Sao lưu", "NAS-SAOLUU", "Thư mục backup/ (hoặc ổ USB)", "CHẠY THẬT (thay thế)"],
  ["Vai trò người dùng", "Người thật ở các máy văn phòng", "Tài khoản admin, thukho01, nv01, nv02, quanly01", "CHẠY THẬT"],
  ["Switch, router, Wi-Fi, VLAN, ACL, port-security", "Thiết bị thật", "Packet Tracer – chứng minh cấu hình và kết nối", "CHỈ SƠ ĐỒ + PT"],
  ["Đường mạng điểm quét ↔ máy chủ", "Cáp/Wi-Fi qua SW1–R1", "Loopback 127.0.0.1 (1 máy) hoặc 2 laptop chung Wi-Fi/hotspot", "CHẠY THẬT (rút gọn)"],
], [1.8, 2, 3.4, 1.4], { size: 20 }));
c.push(P("Ba cách dựng môi trường chạy thật, từ dễ đến khó: **(a)** một laptop chạy server và hai client, địa chỉ `http://127.0.0.1:8080`; **(b)** hai laptop cùng mạng Wi-Fi/hotspot, client đổi địa chỉ sang IP của laptop chạy server; **(c)** máy ảo VirtualBox mạng host-only. Cả ba dùng chung giao ước API nên SV2/SV3 không phải sửa mã, chỉ đổi địa chỉ máy chủ trong file cấu hình."));
c.push(P("**Giới hạn:** Packet Tracer chỉ chứng minh cấu hình và kết nối trong mô hình; kết quả của nó **không** được dùng để khẳng định thông lượng thực tế, vùng phủ Wi-Fi hay khả năng chịu tải của hệ thống thật."));

// ---- 6 ----
c.push(H1("6. Mô hình dữ liệu"));
c.push(H2("6.1. Sơ đồ các bảng và quan hệ"));
c.push(IMG(p("02_MoHinhDuLieu.png"), IMGW));
c.push(CAP("Hình 2. Mô hình dữ liệu – 5 bảng bắt buộc và bảng nhật ký bổ sung AuditLog (02_MoHinhDuLieu.png)"));
c.push(P("Mô hình gồm đủ 5 bảng đề xuất trong phiếu (Products, Inventory, Transactions, Users, ScanPoints) và bổ sung **AuditLog** để ghi lại mọi yêu cầu, kể cả yêu cầu bị từ chối – đây là bằng chứng phát hiện dữ liệu trùng và thao tác không hợp lệ (yêu cầu bắt buộc số 3). Lược đồ cài đặt trong `du_lieu/schema.sql`; dữ liệu mẫu giả trong `du_lieu/seed_data.sql`."));
c.push(H2("6.2. Từ điển dữ liệu"));
c.push(P("Quy ước: **tên trường trong CSDL trùng tên khóa JSON trong API** (snake_case, tiếng Anh, không dấu). Bảng dưới được sinh từ `du_lieu/TuDienDuLieu.csv`; script `xuat_tu_dien.py` đã kiểm tra tự động 38/38 trường khớp với schema.sql về tên, kiểu và khóa chính."));
const order = ["Products", "Inventory", "Transactions", "Users", "ScanPoints", "AuditLog"];
const desc = { Products: "danh mục hàng hóa", Inventory: "tồn hiện tại", Transactions: "lịch sử nhập/xuất, chỉ thêm", Users: "tài khoản và vai trò", ScanPoints: "điểm quét", AuditLog: "nhật ký mọi yêu cầu (bổ sung)" };
order.forEach((tb, i) => {
  c.push(P(`**Bảng ${i + 1}. ${tb}** – ${desc[tb]}`, { keepNext: true, after: 60 }));
  c.push(...T(["Trường", "Kiểu", "Khóa", "Bắt buộc", "Ràng buộc / mặc định", "Ý nghĩa"],
    dict.filter((r) => r["Bảng"] === tb).map((r) => ["`" + r["Trường"] + "`", r["Kiểu SQLite"], r["Khóa"], r["Bắt buộc"], r["Ràng buộc / mặc định"].replace(/; /g, ", "), r["Ý nghĩa"]]),
    [1.8, 1.1, 0.8, 0.8, 2.5, 2.8], { size: 19 }));
});
c.push(H2("6.3. Quan hệ giữa các bảng"));
c.push(...T(["Quan hệ", "Kiểu", "Giải thích"], [
  ["Products – Inventory", "1 – 1", "Mỗi mã hàng có đúng một dòng tồn hiện tại (product_code vừa là khóa chính vừa là khóa ngoại)"],
  ["Products – Transactions", "1 – N", "Một mã hàng xuất hiện trong nhiều giao dịch nhập/xuất; giao dịch với mã hàng không có trong danh mục bị khóa ngoại chặn"],
  ["Users – Transactions", "1 – N", "Một người thực hiện nhiều giao dịch; mỗi giao dịch ghi rõ người thực hiện (yêu cầu bắt buộc 2)"],
  ["ScanPoints – Transactions", "1 – N", "Một điểm quét gửi nhiều giao dịch; biết giao dịch đến từ điểm nào"],
  ["Transactions ··· AuditLog", "Logic qua txn_id", "Không đặt khóa ngoại vì AuditLog phải ghi được cả yêu cầu trùng, sai mã hàng, sai tài khoản"],
], [2, 1.2, 5.3]));
c.push(H2("6.4. Vì sao không chỉ lưu số tồn mà phải lưu lịch sử giao dịch"));
c.push(B("**Truy vết:** biết ai, ở điểm quét nào, lúc nào làm tồn thay đổi – bắt buộc theo yêu cầu 2 (mã, thời gian, người thực hiện)."));
c.push(B("**Phát hiện trùng:** chỉ khi lưu từng giao dịch với mã riêng mới nhận ra một giao dịch bị gửi hai lần (KT2). Nếu chỉ có số tồn, “+20” lần hai trông giống hệt một lần nhập mới."));
c.push(B("**Đối chiếu và khôi phục:** tồn luôn tính lại được bằng Σ NHAP − Σ XUAT. Sau khi khôi phục bản sao hoặc sau sự cố mất mạng, so tồn lưu trữ với tồn tính lại (view `v_doi_chieu_ton`) cho biết dữ liệu có nhất quán không (KT3, yêu cầu 4)."));
c.push(B("**Sửa sai minh bạch:** giao dịch không bị sửa/xóa (trigger chặn); ghi sai thì thêm giao dịch điều chỉnh, lịch sử vẫn còn nguyên."));

// ---- 7 ----
c.push(H1("7. Người dùng, vai trò và ma trận quyền"));
c.push(...T(["Vai trò (role)", "Ứng với đề bài", "Tài khoản mẫu", "Phạm vi"], [
  ["ADMIN", "Quản trị", "admin", "Toàn quyền: tài khoản, điểm quét, sao lưu/khôi phục, xem nhật ký"],
  ["THUKHO", "Thủ kho", "thukho01", "Ghi nhập/xuất, sửa danh mục hàng, xem tồn, lịch sử, đối chiếu"],
  ["NHANVIEN", "Nhân viên", "nv01, nv02", "Ghi nhập/xuất tại điểm quét; xem tồn; chỉ xem giao dịch của mình"],
  ["QUANLY", "Người quản lý / tài khoản chỉ xem (KT3)", "quanly01", "Chỉ đọc tồn kho, lịch sử, đối chiếu, nhật ký; mọi lệnh ghi bị 403"],
], [1.4, 2.2, 1.6, 4.3]));
c.push(P("Ký hiệu: ✔ được phép · ◐ có giới hạn · ✘ bị từ chối (403 FORBIDDEN).", { after: 60 }));
c.push(...T(["Chức năng", "API", "ADMIN", "THUKHO", "NHANVIEN", "QUANLY"], [
  ["Đăng nhập", "POST /api/login", "✔", "✔", "✔", "✔"],
  ["Ghi giao dịch NHAP/XUAT", "POST /api/transactions", "✔", "✔", "✔", "✘"],
  ["Đọc tồn kho", "GET /api/inventory", "✔", "✔", "✔", "✔"],
  ["Đọc lịch sử giao dịch", "GET /api/transactions", "✔", "✔", "◐ của mình", "✔"],
  ["Kiểm tra một giao dịch", "GET /api/transactions/{txn_id}", "✔", "✔", "◐ của mình", "✔"],
  ["Đối chiếu tồn", "GET /api/reconcile", "✔", "✔", "✘", "✔"],
  ["Thêm/sửa danh mục hàng", "POST/PUT /api/products", "✔", "✔", "✘", "✘"],
  ["Quản lý tài khoản", "POST/PUT /api/users", "✔", "✘", "✘", "✘"],
  ["Quản lý điểm quét", "POST/PUT /api/scanpoints", "✔", "✘", "✘", "✘"],
  ["Xem nhật ký AuditLog", "GET /api/audit", "✔", "✘", "✘", "✔"],
  ["Sao lưu CSDL", "POST /api/backup", "✔", "✘", "✘", "✘"],
  ["Khôi phục CSDL", "POST /api/restore", "✔", "✘", "✘", "✘"],
  ["Sửa / xóa giao dịch đã ghi", "(không có API)", "✘", "✘", "✘", "✘"],
], [2.4, 2.7, 0.9, 0.9, 1.2, 0.9], { size: 19, center: [2, 3, 4, 5] }));
c.push(P("Quyền được kiểm tra ở **một chỗ duy nhất** là máy chủ: máy khách không truy cập CSDL trực tiếp và máy chủ lấy người thực hiện từ token đăng nhập, không tin tên người dùng do máy khách tự khai. Mật khẩu chỉ lưu dạng băm SHA-256 có salt."));

// ---- 8 ----
c.push(H1("8. Quy tắc giao dịch"));
c.push(H2("8.1. Mã giao dịch"));
c.push(P("Mã giao dịch có dạng `SPxx-yyyymmdd-nnnn`, ví dụ `SP01-20261026-0001` = điểm quét SP01, ngày 26/10/2026, giao dịch thứ 1 trong ngày. Mã do **máy khách sinh và lưu vào hàng đợi trước khi gửi**; khi gửi lại (mất mạng, hết thời gian chờ) phải dùng đúng mã cũ. Nhờ vậy:"));
c.push(B("Máy chủ nhận ra yêu cầu gửi lại là **cùng một giao dịch** (khóa chính txn_id) và không cộng/trừ tồn lần hai – cơ sở của KT2."));
c.push(B("Hai điểm quét không bao giờ sinh trùng mã vì tiền tố SP01/SP02 khác nhau, không cần hỏi máy chủ trước khi sinh mã."));
c.push(B("Mã cho biết ngay giao dịch đến từ đâu, ngày nào – thuận tiện khi đối chiếu sau sự cố."));
c.push(P("Giới hạn đã biết: 4 chữ số cho 9.999 giao dịch/ngày/điểm quét, đủ cho một ca cao điểm theo giả định G2 (9.600). Nếu chạy 2–3 ca cần tăng lên 5 chữ số; CSDL không ràng buộc định dạng này nên chỉ phải sửa giao ước API và máy khách."));
c.push(H2("8.2. Bộ quy tắc R1 – R10"));
c.push(...T(["Mã", "Quy tắc", "Kiểm tra ở", "Mã lỗi khi vi phạm"], [
  ["R1", "txn_id là duy nhất; gửi trùng không làm đổi tồn, trả kết quả lần đầu", "Máy chủ + PRIMARY KEY", "409 DUPLICATE_TXN"],
  ["R2", "Mã hàng phải có trong Products và đang kinh doanh", "Máy chủ + FOREIGN KEY", "404 PRODUCT_NOT_FOUND"],
  ["R3", "txn_type ∈ {NHAP, XUAT}; quantity nguyên 1…10000; đủ trường bắt buộc", "Máy khách + máy chủ + CHECK", "400 INVALID_TYPE / INVALID_QUANTITY / INVALID_JSON"],
  ["R4", "XUAT không vượt tồn; tồn không bao giờ âm", "Máy chủ + CHECK quantity ≥ 0", "422 INSUFFICIENT_STOCK"],
  ["R5", "Tài khoản tồn tại, đang hoạt động, vai trò có quyền ghi", "Máy chủ", "401 UNAUTHORIZED / 403 FORBIDDEN"],
  ["R6", "Điểm quét tồn tại, đang hoạt động, khớp tiền tố txn_id", "Máy chủ + FOREIGN KEY", "400 INVALID_SCAN_POINT / INVALID_TXN_ID"],
  ["R7", "INSERT Transactions và UPDATE Inventory trong cùng một giao dịch CSDL", "Máy chủ (BEGIN IMMEDIATE … COMMIT)", "500 SERVER_ERROR (đã ROLLBACK)"],
  ["R8", "Lịch sử giao dịch không được sửa/xóa", "Trigger trong CSDL", "Lỗi CSDL – không có API"],
  ["R9", "Chỉ trả 201 OK sau khi COMMIT thành công", "Máy chủ", "—"],
  ["R10", "Inventory.quantity = Σ NHAP − Σ XUAT cho mọi mã hàng", "View v_doi_chieu_ton", "chenh_lech ≠ 0 → báo lệch"],
], [0.6, 4, 2.2, 2.4], { size: 20 }));

// ---- 9 ----
c.push(H1("9. Luồng dữ liệu quét mã"));
c.push(H2("9.1. Lưu đồ"));
c.push(IMG(p("04_SoDoLuongDuLieu.png"), IMGW));
c.push(CAP("Hình 3. Lưu đồ quét → gửi → kiểm tra → lưu → cập nhật tồn → phản hồi, có nhánh lỗi, nhánh trùng và nhánh mất mạng (04_SoDoLuongDuLieu.png)"));
c.push(H2("9.2. Sáu bước của luồng chính"));
c.push(N("**Quét:** nhân viên quét (hoặc nhập) mã hàng, chọn NHAP/XUAT, nhập số lượng. Máy khách sinh `txn_id` và ghi vào hàng đợi cục bộ."));
c.push(N("**Gửi:** máy khách gửi `POST /api/transactions` kèm txn_id, product_code, txn_type, quantity, scan_point_id, client_time; chờ tối đa 5 giây."));
c.push(N("**Kiểm tra:** máy chủ mở khóa ghi (BEGIN IMMEDIATE), ghi AuditLog, rồi kiểm tra theo thứ tự: token và quyền (R5) → dữ liệu (R3) → điểm quét (R6) → trùng mã giao dịch (R1) → mã hàng (R2) → đủ tồn (R4)."));
c.push(N("**Lưu:** INSERT một dòng vào Transactions với đầy đủ mã, thời gian, người thực hiện, điểm quét."));
c.push(N("**Cập nhật tồn:** UPDATE Inventory, ghi stock_after; COMMIT cả bước 4 và 5 cùng lúc – lỗi bất kỳ thì ROLLBACK cả hai."));
c.push(N("**Phản hồi:** máy chủ trả `201 OK` kèm stock_after và server_time; máy khách xóa giao dịch khỏi hàng đợi và hiển thị “Đã lưu”."));
c.push(H2("9.3. Nhánh lỗi, nhánh trùng và nhánh mất mạng"));
c.push(B("**Nhánh lỗi** (dữ liệu/quyền: 400, 401, 403; nghiệp vụ: 404, 422): máy chủ không ghi Transactions, không đổi tồn, chỉ ghi AuditLog với result = REJECTED; máy khách báo lỗi và không gửi lại."));
c.push(B("**Nhánh trùng** (409 DUPLICATE_TXN): txn_id đã có. Máy chủ không INSERT, tồn không đổi lần hai, trả kèm kết quả lần đầu; máy khách coi như đã lưu và xóa khỏi hàng đợi."));
c.push(B("**Nhánh mất mạng / hết giờ chờ:** máy khách không biết máy chủ đã lưu hay chưa nên giữ giao dịch trong hàng đợi, thử lại sau 5 → 10 → 20 giây (tối đa 60 giây) với cùng txn_id. Nếu lần trước máy chủ đã lưu, lần gửi lại nhận 409 – an toàn, tồn không bị cộng hai lần."));
c.push(H2("9.4. Giao ước API (tóm tắt)"));
c.push(P("Chi tiết đầy đủ, ví dụ yêu cầu/phản hồi và 14 mã lỗi nằm trong `05_GiaoUocAPI.md` (v1.0)."));
c.push(...T(["Lệnh", "Mục đích", "Phản hồi thành công"], [
  ["POST /api/login", "Đăng nhập, lấy token", "200 { token, role }"],
  ["POST /api/transactions", "Ghi giao dịch nhập/xuất", "201 { txn_id, stock_after, server_time }"],
  ["GET /api/inventory[/{code}]", "Đọc tồn tất cả / một mã hàng", "200 { items: [...] }"],
  ["GET /api/transactions?…", "Đọc lịch sử, lọc theo mã hàng, điểm quét, người, thời gian", "200 { items: [...] }"],
  ["GET /api/transactions/{txn_id}", "Xác minh một giao dịch đã được lưu", "200 hoặc 404 TXN_NOT_FOUND"],
  ["GET /api/reconcile", "Đối chiếu tồn lưu trữ với tồn tính lại", "200 { all_match, items }"],
  ["POST /api/backup, /api/restore", "Sao lưu / khôi phục (ADMIN)", "200"],
], [2.8, 3.5, 3]));
c.push(...CODE([
  "POST /api/transactions        Authorization: Bearer <token>",
  '{ "txn_id": "SP01-20261026-0001", "product_code": "SP001", "txn_type": "NHAP",',
  '  "quantity": 20, "scan_point_id": "SP01", "client_time": "2026-10-26T09:15:00" }',
  "",
  "201 Created",
  '{ "status": "OK", "txn_id": "SP01-20261026-0001", "product_code": "SP001",',
  '  "stock_after": 120, "server_time": "2026-10-26T09:15:02" }',
]));
c.push(H2("9.5. Đối chiếu dữ liệu sau khi mất mạng hoặc khôi phục"));
c.push(P("Thiết kế dữ liệu hỗ trợ sẵn quy trình đối chiếu (SV4 triển khai và kiểm thử chi tiết):"));
c.push(N("Khi có mạng lại, mỗi máy khách gửi hết hàng đợi theo thứ tự client_time, giữ nguyên txn_id; các giao dịch đã lưu trước đó trả 409 nên không bị cộng lặp.", "num2"));
c.push(N("Với giao dịch nghi ngờ, máy khách gọi `GET /api/transactions/{txn_id}` để xác minh đã lưu hay chưa.", "num2"));
c.push(N("Sau khi khôi phục bản sao (KT3), gọi `GET /api/reconcile`: mọi mã hàng phải có chenh_lech = 0.", "num2"));
c.push(N("Các giao dịch phát sinh sau thời điểm sao lưu nằm trong AuditLog và hàng đợi máy khách; gửi lại chúng (cùng txn_id) để đưa CSDL về trạng thái mới nhất mà không trùng lặp.", "num2"));

// ---- 10 ----
c.push(H1("10. Kiểm chứng thiết kế"));
c.push(P(`Để chứng minh mô hình dữ liệu và bộ quy tắc hoạt động đúng trước khi bàn giao, SV1 viết script \`du_lieu/kiem_tra_thiet_ke.py\` (chỉ dùng thư viện chuẩn của Python). Script dựng CSDL từ schema.sql + seed_data.sql, cài một hàm ghi giao dịch tham chiếu theo R1–R10 rồi chạy 11 tình huống. Lần chạy ghi trong tài liệu: **${runTime}** (${sqliteVer}). Kết quả gốc lưu trong \`du_lieu/ketqua_kiemtra.txt\`.`));
c.push(...T(["Mã", "Tình huống", "Kết quả thực tế", "Đánh giá"], tcs.map((t) => [t[0], t[1], t[2].replace(/\{|\}|'/g, ""), t[3]]), [0.7, 2.6, 4.6, 1], { size: 18 }));
c.push(P("Đo dung lượng thực tế bằng `du_lieu/do_dung_luong.py`: chèn 100.000 giao dịch giả (kèm 1 dòng AuditLog mỗi giao dịch) làm CSDL tăng từ 73.728 B lên 30.187.520 B, tức **khoảng 301 byte/giao dịch** (gồm bảng, 2 chỉ mục và nhật ký). Con số này là đầu vào cho mô hình ước lượng mở rộng."));
c.push(P("**Lưu ý:** đây là kiểm chứng ở mức thiết kế dữ liệu (không qua mạng, không qua HTTP). Bằng chứng nghiệm thu KT1–KT3 chính thức do cả nhóm thực hiện trên hệ thống của SV2/SV3, theo bảng kiểm thử chung."));

// ---- 11 ----
c.push(H1("11. Bàn giao thiết kế cho nhóm"));
c.push(...T(["Người nhận", "Nhận gì", "Dùng để làm gì"], [
  ["SV2 – Điểm quét", "05_GiaoUocAPI.md (mục 1–3, 6), định dạng txn_id, danh sách mã lỗi và cách xử lý, địa chỉ máy chủ, tài khoản nv01/nv02", "Viết client SP01/SP02: sinh txn_id, hàng đợi, gửi lại khi mất mạng, hiển thị kết quả"],
  ["SV3 – Lưu trữ, quyền, sao lưu", "schema.sql, seed_data.sql, 06_TuDienDuLieu.md, R1–R10, ma trận quyền, giao ước API đầy đủ, kiem_tra_thiet_ke.py (hàm tham chiếu)", "Dựng server và CSDL, phân quyền, sao lưu/khôi phục ra thư mục backup/"],
  ["SV4 – Nhất quán, lỗi, mở rộng", "Bộ R1–R10, view v_doi_chieu_ton, AuditLog, 11 tình huống kiểm chứng, số đo 301 B/giao dịch, giả định G2", "Viết kịch bản KT1–KT3, kiểm thử lỗi và trùng, ước lượng – đo tải khi tăng số điểm quét"],
  ["Cả nhóm", "01_SoDoHaTang.png, BangDiaChiIP.csv, QuyTacTruyCap.csv, cấu hình Packet Tracer", "Chương kiến trúc của báo cáo chung, video demo"],
], [1.8, 4, 3.2], { size: 20 }));
c.push(P("Quy tắc thay đổi: sau Cổng 1, mọi thay đổi tên trường, mã lỗi hay định dạng phải tăng phiên bản giao ước và ghi vào nhật ký thay đổi (`doi_chieu/NhatKyThayDoi.md`) để ba bạn còn lại cùng cập nhật."));

// ---- 12 ----
c.push(H1("12. Chuẩn bị bảo vệ"));
const qa = [
  ["Vì sao hệ thống cần máy chủ hoặc một nơi xử lý dữ liệu chung?", "Hai điểm quét cùng sửa một con số tồn. Chỉ khi có một nơi xử lý chung thì giao dịch mới được kiểm tra theo cùng quy tắc, được ghi lần lượt không đè nhau, phân quyền – phát hiện trùng – sao lưu làm ở một chỗ, và máy khách hỏng cũng không mất dữ liệu (mục 3.3)."],
  ["Hai điểm quét dùng chung cơ sở dữ liệu như thế nào?", "Không điểm quét nào mở CSDL. Cả hai gửi HTTP/JSON tới SRV-KHO; máy chủ là tiến trình duy nhất mở kho.db và dùng khóa ghi BEGIN IMMEDIATE nên hai yêu cầu đồng thời được ghi lần lượt. Tình huống TC10 chạy song song 50 nhập ở SP01 và 50 xuất ở SP02 cùng một mã hàng: tồn cuối đúng bằng tồn đầu (mục 3.4, 10)."],
  ["Vì sao không chỉ lưu số lượng tồn mà còn phải lưu lịch sử giao dịch?", "Để truy vết ai – ở đâu – lúc nào, để phát hiện gửi trùng, để tính lại và đối chiếu tồn sau sự cố hoặc khôi phục (Σ NHAP − Σ XUAT), và để sửa sai minh bạch bằng giao dịch điều chỉnh (mục 6.4)."],
  ["Mã giao dịch dùng để làm gì?", "Là định danh duy nhất của một lần nhập/xuất do máy khách sinh trước khi gửi. Gửi lại vẫn dùng mã cũ nên máy chủ nhận ra trùng và không đổi tồn lần hai (KT2); tiền tố SPxx cho biết nguồn gốc và tránh trùng giữa các điểm quét (mục 8.1)."],
  ["Nếu số điểm quét tăng từ 2 lên 4, cần xem xét nâng cấp những thành phần nào?", "Theo giả định G2, tải đỉnh tăng từ 0,67 lên 1,33 giao dịch/giây; dữ liệu tăng từ khoảng 1,7 lên 3,5 GB/năm (301 B/giao dịch); băng thông chỉ vài chục kbit/s nên mạng chưa phải điểm nghẽn. Cần xem: số cổng switch (đã để sẵn Fa0/12–16), vùng phủ và số máy trên AP Wi-Fi, khai báo SP03/SP04 trong ScanPoints và tài khoản mới, dung lượng NAS và thời gian sao lưu, CPU/RAM máy chủ và khả năng ghi đồng thời của SQLite (đủ cho hàng chục giao dịch/giây; nhiều kho/nhiều điểm hơn nữa thì chuyển PostgreSQL), UPS. Bảng ước lượng chi tiết do SV1 lập và SV4 đo kiểm chứng."],
  ["(Câu hỏi của phiếu) Vì sao quét thành công chưa chứng minh máy chủ đã lưu giao dịch?", "Tiếng “bíp” chỉ xác nhận bước ① – máy đọc được mã. Sau đó gói tin có thể mất ở bước ② hoặc ⑥, máy chủ có thể từ chối ở bước ③ (trùng, sai mã hàng, không đủ tồn, không có quyền), hoặc lỗi trước COMMIT. Chỉ phản hồi 201 OK – được gửi sau khi COMMIT – hoặc 409 (đã lưu từ trước), hoặc tra GET /api/transactions/{txn_id} mới chứng minh giao dịch đã nằm trong CSDL."],
];
qa.forEach(([q, a], i) => { c.push(P(`**Câu ${i + 1}. ${q}**`, { keepNext: true, after: 40 })); c.push(P(a)); });

// ---- 13 ----
c.push(H1("13. Giới hạn, nguồn tham khảo và sử dụng AI"));
c.push(H2("13.1. Phần được mô phỏng thay vì triển khai bằng thiết bị thật"));
c.push(B("Switch, router, Wi-Fi, VLAN, ACL, port-security: chỉ chứng minh trong Packet Tracer; không khẳng định thông lượng, vùng phủ sóng hay khả năng chịu tải thật."));
c.push(B("NAS sao lưu được thay bằng thư mục backup/ trên cùng laptop – chưa bảo vệ được trước hỏng ổ cứng như NAS thật."));
c.push(B("Máy quét mã vạch được thay bằng nhập bàn phím (giả định G4); không kiểm tra tốc độ đọc mã hay mã vạch hỏng."));
c.push(B("Số liệu ước lượng dựa trên giả định G2 và phép đo dung lượng trên laptop; cần SV4 đo tải thực tế để xác nhận."));
c.push(H2("13.2. Tài liệu tham khảo"));
[
  "Cisco Networking Academy – Cisco Packet Tracer và tài liệu cấu hình VLAN, 802.1Q trunk, router-on-a-stick, extended ACL, port-security trên Cisco IOS.",
  "IEEE 802.1Q – Bridges and Bridged Networks (VLAN tagging).",
  "RFC 1918 – Address Allocation for Private Internets (dải 192.168.0.0/16).",
  "RFC 9110 – HTTP Semantics (mã trạng thái 200, 201, 400, 401, 403, 404, 409, 422, 500).",
  "SQLite Documentation – CREATE TABLE, FOREIGN KEY, CHECK, CREATE TRIGGER, BEGIN IMMEDIATE, Write-Ahead Logging (sqlite.org).",
  "Python 3 Documentation – module sqlite3, threading.",
  "Phiếu giao đề 22 và hướng dẫn chung học phần RIPT1304 – Viện Khoa học Kỹ thuật Bưu điện, PTIT.",
].forEach((s, i) => c.push(P(`[${i + 1}] ${s}`, { after: 60 })));
c.push(H2("13.3. Sử dụng AI"));
c.push(P("Bản nháp tài liệu, cấu hình mẫu, các script và sơ đồ được soạn với sự hỗ trợ của trợ lý AI (Claude – Anthropic). SV1 đã đọc lại toàn bộ, chạy lại `kiem_tra_thiet_ke.py`, `do_dung_luong.py`, `xuat_tu_dien.py`, nạp cấu hình vào Packet Tracer để kiểm tra, và chịu trách nhiệm giải thích, chỉnh sửa các phần đã nộp. *(SV1 bổ sung: phần nào tự chỉnh sửa, lỗi nào đã tự phát hiện và xử lý.)*"));

// ---- Phụ lục ----
c.push(H1("Phụ lục A. Danh mục file minh chứng của SV1"));
c.push(...T(["File", "Nội dung"], [
  ["01_SoDoHaTang.png", "Sơ đồ kiến trúc hạ tầng, 3 VLAN, phần chạy thật / chỉ trên sơ đồ"],
  ["02_MoHinhDuLieu.png", "Sơ đồ các bảng và quan hệ"],
  ["03_ThietKeDuLieu.docx / .pdf", "Tài liệu này"],
  ["04_SoDoLuongDuLieu.png", "Lưu đồ luồng dữ liệu có nhánh lỗi, trùng, mất mạng"],
  ["05_GiaoUocAPI.md", "Giao ước API, danh sách mã lỗi, ma trận quyền"],
  ["06_TuDienDuLieu.md", "Từ điển dữ liệu (sinh từ du_lieu/TuDienDuLieu.csv)"],
  ["cau_hinh/R1-KHO_router.txt, SW1-KHO_switch.txt, AP-KHO_wifi.txt", "Cấu hình thiết bị mạng"],
  ["cau_hinh/BangDiaChiIP.csv, QuyTacTruyCap.csv", "Bảng IP và quy tắc truy cập"],
  ["cau_hinh/HuongDan_PacketTracer.md", "Cách dựng file .pkt và 13 phép kiểm tra"],
  ["du_lieu/schema.sql, seed_data.sql", "Lược đồ CSDL và dữ liệu mẫu giả"],
  ["du_lieu/kiem_tra_thiet_ke.py, ketqua_kiemtra.txt", "Script và kết quả kiểm chứng 11 tình huống"],
  ["du_lieu/do_dung_luong.py, ketqua_do_dung_luong.txt", "Script và kết quả đo byte/giao dịch"],
  ["du_lieu/xuat_tu_dien.py", "Kiểm tra từ điển khớp schema, xuất 06_TuDienDuLieu.md"],
  ["nguon_so_do/", "Mã nguồn SVG/HTML của các sơ đồ + render.ps1 để xuất lại PNG"],
], [4, 5]));

(async () => {
  const doc = makeDoc(c, { title: "03_ThietKeDuLieu – Đề tài 22", footer: "Đề tài 22 – SV1 – 03_ThietKeDuLieu · Trang " });
  await save(doc, p("03_ThietKeDuLieu.docx"));
  console.log("OK", tcs.length, "TC");
})();
