# Đề tài 22 - SV1-09: Tạo 07_UocLuong_MoRong.xlsx bằng Microsoft Excel (COM).
# Mọi kết quả là CÔNG THỨC tham chiếu ô giả định -> sửa giả định là bảng tự tính lại.
# Chạy: powershell -ExecutionPolicy Bypass -File tao_bang_uoc_luong.ps1
$ErrorActionPreference = "Stop"
# Excel COM đọc mã định dạng số theo ngôn ngữ của luồng gọi (máy vi-VN hiểu "0.00" thành sai):
# gán NumberFormat qua InvokeMember với văn hóa en-US để mã định dạng luôn được hiểu đúng.
$EN = [System.Globalization.CultureInfo]::GetCultureInfo("en-US")
function NF($rng, [string]$fmt) { [void][System.__ComObject].InvokeMember("NumberFormat", [Reflection.BindingFlags]::SetProperty, $null, $rng, @($fmt), $EN) }
$excel_truoc = @(Get-Process EXCEL -ErrorAction SilentlyContinue | ForEach-Object Id)
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$out  = Join-Path (Split-Path -Parent $here) "07_UocLuong_MoRong.xlsx"

$BLUE = 16711680; $GREEN = 32768; $YELLOW = 10092543; $HEAD = 15652797; $GREY = 15921906; $RED = 255

$xl = New-Object -ComObject Excel.Application
$xl.Visible = $false; $xl.DisplayAlerts = $false
$wb = $xl.Workbooks.Add()
while ($wb.Worksheets.Count -lt 4) { $null = $wb.Worksheets.Add([Type]::Missing, $wb.Worksheets.Item($wb.Worksheets.Count)) }
$gd = $wb.Worksheets.Item(1); $gd.Name = "GiaDinh"
$ul = $wb.Worksheets.Item(2); $ul.Name = "UocLuong"
$kl = $wb.Worksheets.Item(3); $kl.Name = "KetLuan"
$tt = $wb.Worksheets.Item(4); $tt.Name = "ThuTai_GiaLap"
foreach ($s in @($gd, $ul, $kl, $tt)) { $s.Cells.Font.Name = "Arial"; $s.Cells.Font.Size = 10 }

function Head($ws, $row, $cols) {
  for ($i = 0; $i -lt $cols.Count; $i++) {
    $c = $ws.Cells.Item($row, $i + 1); $c.Value2 = $cols[$i]; $c.Font.Bold = $true
    $c.Interior.Color = $HEAD; $c.WrapText = $true; $c.VerticalAlignment = -4108
  }
}
function Title($ws, $t, $sub) {
  $ws.Cells.Item(1, 1).Value2 = $t; $ws.Cells.Item(1, 1).Font.Bold = $true; $ws.Cells.Item(1, 1).Font.Size = 13
  $ws.Cells.Item(2, 1).Value2 = $sub; $ws.Cells.Item(2, 1).Font.Bold = $true; $ws.Cells.Item(2, 1).Font.Color = $RED
}

# ======================= GiaDinh =======================
Title $gd "ĐỀ TÀI 22 – GIẢ ĐỊNH CHO MÔ HÌNH ƯỚC LƯỢNG KHI TĂNG TỪ 2 LÊN 4 ĐIỂM QUÉT" "ĐÂY LÀ ƯỚC LƯỢNG, CHƯA ĐO THỰC TẾ. Chữ xanh = giả định nhập tay (sửa được). Nền vàng = giả định then chốt."
Head $gd 4 @("Mã", "Giả định", "Giá trị", "Đơn vị", "Tên dùng trong công thức", "Nguồn / căn cứ")
$gia_dinh = @(
  @("G01", "Số điểm quét hiện tại", 2, "điểm", "SoDiem", "Phiếu giao đề – yêu cầu 2 (mô phỏng 2 điểm quét)", 0),
  @("G02", "Hệ số mở rộng số điểm quét", 2, "lần", "HeSo", "Phiếu giao đề – yêu cầu 4 (tăng gấp đôi)", 0),
  @("G03", "Khoảng cách giữa 2 lần quét lúc cao điểm", 3, "giây/GD/điểm", "KhoangCach", "Giả định G2 của nhóm (03_ThietKeDuLieu, mục 2)", 1),
  @("G04", "Tỉ lệ tải trung bình so với tải đỉnh", 0.5, "%", "TiLeTB", "Giả định nhóm: trong ca không quét liên tục", 1),
  @("G05", "Giờ làm việc mỗi ngày", 8, "giờ", "GioNgay", "Giả định G2: 1 ca 8 giờ", 0),
  @("G06", "Ngày làm việc mỗi năm", 300, "ngày", "NgayNam", "Giả định G2", 0),
  @("G07", "Dung lượng CSDL cho mỗi giao dịch", 301, "byte", "BytePerGD", "ĐO THẬT: du_lieu/do_dung_luong.py ngày 26/10/2026, 100.000 GD (gồm bảng, 2 chỉ mục, AuditLog)", 1),
  @("G08", "Dữ liệu mạng cho mỗi giao dịch (yêu cầu + phản hồi + TCP/HTTP)", 2048, "byte", "ByteMang", "Ước lượng: JSON ~250 B + header HTTP ~400 B mỗi chiều + bắt tay/đóng TCP; SV4 đo lại bằng Wireshark", 1),
  @("G09", "Tốc độ cổng mạng nhỏ nhất trên đường đi", 100, "Mbit/s", "TocDoCong", "Cổng FastEthernet của switch 2960 (01_SoDoHaTang)", 0),
  @("G10", "Năng lực xử lý ước lượng của máy chủ", 50, "GD/s", "NangLuc", "Giả định thận trọng = ½ kết quả chạy thử máy chủ giả lập (~100 GD/s, sheet ThuTai_GiaLap); SV4 đo trên máy chủ SV3", 1),
  @("G11", "Số bản sao lưu giữ lại", 11, "bản", "SoBanSao", "Thiết kế sao lưu: 7 bản ngày + 4 bản tuần", 0),
  @("G12", "Dung lượng NAS dùng được", 1000, "GB", "NAS", "NAS 2 × 1 TB RAID 1 (03_ThietKeDuLieu, mục 3.2)", 0),
  @("G13", "Số cổng switch dành cho điểm quét có dây", 7, "cổng", "CongCoDay", "SW1-KHO: Fa0/9-10 và Fa0/12-16 (Fa0/11 cho AP)", 0),
  @("G14", "Tỉ lệ điểm quét dùng cáp", 0.5, "%", "TiLeCoDay", "Thiết kế hiện tại: SP01 có dây, SP02 Wi-Fi", 0),
  @("G15", "Số máy quét Wi-Fi khuyến nghị tối đa trên 1 AP", 25, "thiết bị", "MaxWifi", "Mức thông dụng cho AP văn phòng; cần khảo sát sóng thực tế (Packet Tracer không chứng minh được)", 0),
  @("G16", "Số địa chỉ dùng được của VLAN 30", 253, "địa chỉ", "IPVlan30", "Mạng /24: 256 − mạng − broadcast − gateway", 0),
  @("G17", "Giới hạn giao dịch/ngày/điểm của txn_id", 9999, "GD", "MaxGDNgay", "Định dạng SPxx-yyyymmdd-nnnn (4 chữ số)", 0),
  @("G18", "Số điểm quét tối đa theo mã SP##", 99, "điểm", "MaxSP", "CHECK scan_point_id GLOB 'SP[0-9][0-9]' (schema.sql)", 0),
  @("G19", "Ngưỡng cảnh báo mức sử dụng", 0.7, "%", "NguongCanhBao", "Quy ước nhóm: vượt 70% phải lên kế hoạch nâng cấp", 0),
  @("G20", "Thời gian lưu dữ liệu trong CSDL", 1, "năm", "NamLuu", "Giả định nhóm", 0)
)
$r = 5
foreach ($g in $gia_dinh) {
  $gd.Cells.Item($r, 1).Value2 = $g[0]; $gd.Cells.Item($r, 2).Value2 = $g[1]
  $c = $gd.Cells.Item($r, 3); $c.Value2 = [double]$g[2]; $c.Font.Color = $BLUE
  if ($g[3] -eq "%") { NF $c "0%" } else { NF $c "#,##0" }
  if ($g[6] -eq 1) { $c.Interior.Color = $YELLOW }
  $gd.Cells.Item($r, 4).Value2 = $g[3]; $gd.Cells.Item($r, 5).Value2 = $g[4]; $gd.Cells.Item($r, 6).Value2 = $g[5]
  $null = $wb.Names.Add($g[4], "=GiaDinh!`$C`$$r")
  $r++
}
$gd.Columns.Item(1).ColumnWidth = 6; $gd.Columns.Item(2).ColumnWidth = 52; $gd.Columns.Item(3).ColumnWidth = 10
$gd.Columns.Item(4).ColumnWidth = 13; $gd.Columns.Item(5).ColumnWidth = 18; $gd.Columns.Item(6).ColumnWidth = 95
$gd.Range("A4:F$($r-1)").Borders.LineStyle = 1

# ======================= UocLuong =======================
Title $ul "ĐỀ TÀI 22 – BẢNG ƯỚC LƯỢNG TÀI NGUYÊN: 2 ĐIỂM QUÉT → 4 ĐIỂM QUÉT" "ĐÂY LÀ ƯỚC LƯỢNG, CHƯA ĐO THỰC TẾ. Cột E–J là công thức từ sheet GiaDinh. Cột L–M (nền vàng) do SV4 điền số đo thực tế."
Head $ul 4 @("STT", "Chỉ tiêu", "Đơn vị", "Công thức (diễn giải)", "2 điểm quét", "4 điểm quét", "Tăng (4/2)", "Giới hạn", "% dùng ở 4 điểm", "Đánh giá", "Thành phần cần xem xét", "Đo thực tế 2 điểm (SV4)", "Đo thực tế 4 điểm (SV4)", "Sai lệch ước lượng – đo (4 điểm)")
# STT, chỉ tiêu, đơn vị, diễn giải, công thức E (dùng {N} = số điểm của cột), giới hạn H, định dạng, thành phần, đo được?
$hang = @(
  @("Số điểm quét", "điểm", "G01 × (1 hoặc G02)", "{N}", "=MaxSP", "#,##0", "Bảng ScanPoints (SP##), giấy phép/tài khoản", 0),
  @("Tải đỉnh", "GD/s", "Số điểm ÷ G03", "={N}/KhoangCach", "=NangLuc", "0.00", "CPU/RAM máy chủ, khả năng ghi đồng thời của CSDL", 1),
  @("Tải trung bình", "GD/s", "Tải đỉnh × G04", "={N}/KhoangCach*TiLeTB", "", "0.00", "", 0),
  @("Giao dịch/ngày/điểm quét (đỉnh)", "GD", "3600 ÷ G03 × G05", "=3600/KhoangCach*GioNgay", "=MaxGDNgay", "#,##0", "Định dạng txn_id (4 chữ số)", 0),
  @("Giao dịch/ngày toàn kho (đỉnh)", "GD", "Số điểm × STT 4", "={N}*3600/KhoangCach*GioNgay", "", "#,##0", "", 1),
  @("Giao dịch/ngày toàn kho (trung bình)", "GD", "STT 5 × G04", "={N}*3600/KhoangCach*GioNgay*TiLeTB", "", "#,##0", "", 0),
  @("Giao dịch/năm (trung bình)", "GD", "STT 6 × G06", "={N}*3600/KhoangCach*GioNgay*TiLeTB*NgayNam", "", "#,##0", "", 0),
  @("CSDL tăng mỗi ngày (đỉnh)", "MB", "STT 5 × G07 ÷ 10^6", "={N}*3600/KhoangCach*GioNgay*BytePerGD/10^6", "", "0.00", "Ổ SSD máy chủ", 1),
  @("CSDL sau thời gian lưu (trung bình)", "GB", "STT 7 × G07 × G20 ÷ 10^9", "={N}*3600/KhoangCach*GioNgay*TiLeTB*NgayNam*BytePerGD*NamLuu/10^9", "", "0.00", "Ổ SSD máy chủ", 0),
  @("CSDL sau thời gian lưu (cận trên – cả năm ở tải đỉnh)", "GB", "STT 5 × G06 × G07 × G20 ÷ 10^9", "={N}*3600/KhoangCach*GioNgay*NgayNam*BytePerGD*NamLuu/10^9", "", "0.00", "Ổ SSD máy chủ", 0),
  @("Dung lượng sao lưu cần (cận trên)", "GB", "STT 10 × G11", "={N}*3600/KhoangCach*GioNgay*NgayNam*BytePerGD*NamLuu/10^9*SoBanSao", "=NAS", "0.00", "NAS sao lưu, thời gian sao lưu", 0),
  @("Băng thông đỉnh", "kbit/s", "Tải đỉnh × G08 × 8 ÷ 1000", "={N}/KhoangCach*ByteMang*8/1000", "=TocDoCong*1000", "0.00", "Switch, AP Wi-Fi (thông lượng thật cần đo)", 1),
  @("Cổng switch cho điểm quét có dây", "cổng", "LÀM TRÒN LÊN(Số điểm × G14)", "=ROUNDUP({N}*TiLeCoDay,0)", "=CongCoDay", "#,##0", "Switch SW1-KHO (cổng dự phòng Fa0/12-16)", 0),
  @("Máy quét dùng Wi-Fi", "thiết bị", "Số điểm − STT 13", "={N}-ROUNDUP({N}*TiLeCoDay,0)", "=MaxWifi", "#,##0", "AP-KHO: vùng phủ, số máy kết nối", 0),
  @("Địa chỉ IP cần trong VLAN 30", "địa chỉ", "Số điểm + 1 (quản lý AP)", "={N}+1", "=IPVlan30", "#,##0", "Quy hoạch IP, dải DHCP", 0),
  @("Tài khoản NHANVIEN (1 người/điểm/ca)", "tài khoản", "Số điểm", "={N}", "", "#,##0", "Bảng Users, phân quyền", 0)
)
$r = 5; $i = 1
foreach ($h in $hang) {
  $ul.Cells.Item($r, 1).Value2 = [double]$i; $ul.Cells.Item($r, 2).Value2 = $h[0]; $ul.Cells.Item($r, 3).Value2 = $h[1]; $ul.Cells.Item($r, 4).Value2 = $h[2]
  $f2 = $h[3].Replace("{N}", "SoDiem"); $f4 = $h[3].Replace("{N}", "(SoDiem*HeSo)")
  if ($h[3] -eq "{N}") { $f2 = "=SoDiem"; $f4 = "=SoDiem*HeSo" }
  $ul.Cells.Item($r, 5).Formula = $f2; $ul.Cells.Item($r, 6).Formula = $f4
  $ul.Cells.Item($r, 5).Font.Color = $GREEN; $ul.Cells.Item($r, 6).Font.Color = $GREEN
  NF $ul.Cells.Item($r, 5) $h[5]; NF $ul.Cells.Item($r, 6) $h[5]
  $ul.Cells.Item($r, 7).Formula = "=IF(E$r=0,`"`",F$r/E$r)"; NF $ul.Cells.Item($r, 7) "0.0`"x`""
  if ($h[4] -ne "") {
    $ul.Cells.Item($r, 8).Formula = $h[4]; $ul.Cells.Item($r, 8).Font.Color = $GREEN; NF $ul.Cells.Item($r, 8) "#,##0"
    $ul.Cells.Item($r, 9).Formula = "=F$r/H$r"; NF $ul.Cells.Item($r, 9) "0.0%"
    $ul.Cells.Item($r, 10).Formula = "=IF(I$r>=1,`"VƯỢT – phải nâng cấp`",IF(I$r>=NguongCanhBao,`"Cảnh báo – lên kế hoạch`",`"Đủ`"))"
  } else { $ul.Cells.Item($r, 10).Value2 = "—" }
  $ul.Cells.Item($r, 11).Value2 = $h[6]
  if ($h[7] -eq 1) {
    $ul.Range("L$($r):M$($r)").Interior.Color = $YELLOW; NF $ul.Range("L$($r):M$($r)") $h[5]
    $ul.Cells.Item($r, 14).Formula = "=IF(M$r=`"`",`"`",(F$r-M$r)/M$r)"; NF $ul.Cells.Item($r, 14) "0.0%"
  } else { $ul.Range("L$($r):N$($r)").Interior.Color = $GREY }
  $r++; $i++
}
# Hàng đo bổ sung chỉ có ở thực tế
$ul.Cells.Item($r, 1).Value2 = [double]$i; $ul.Cells.Item($r, 2).Value2 = "Độ trễ phản hồi p95 (yêu cầu thiết kế)"; $ul.Cells.Item($r, 3).Value2 = "ms"
$ul.Cells.Item($r, 4).Value2 = "Không ước lượng – chỉ đo. Yêu cầu ≤ 500 ms (máy khách chờ tối đa 5 s)"
$ul.Cells.Item($r, 8).Value2 = [double]500; $ul.Cells.Item($r, 8).Font.Color = $BLUE
$ul.Cells.Item($r, 9).Formula = "=IF(M$r=`"`",`"`",M$r/H$r)"; NF $ul.Cells.Item($r, 9) "0.0%"
$ul.Cells.Item($r, 10).Formula = "=IF(M$r=`"`",`"Chờ SV4 đo`",IF(I$r>=1,`"VƯỢT – phải nâng cấp`",IF(I$r>=NguongCanhBao,`"Cảnh báo – lên kế hoạch`",`"Đủ`")))"
$ul.Cells.Item($r, 11).Value2 = "Máy chủ, mạng"; $ul.Range("L$($r):M$($r)").Interior.Color = $YELLOW
$last = $r
$ul.Range("A4:N$last").Borders.LineStyle = 1; $ul.Range("A5:N$last").VerticalAlignment = -4160
$w = @(5, 40, 9, 38, 12, 12, 9, 11, 11, 22, 40, 13, 13, 14)
for ($k = 0; $k -lt $w.Count; $k++) { $ul.Columns.Item($k + 1).ColumnWidth = $w[$k] }
$ul.Range("D5:D$last").WrapText = $true; $ul.Range("K5:K$last").WrapText = $true; $ul.Range("B5:B$last").WrapText = $true
$ul.Rows.Item(4).RowHeight = 42
$nr = $last + 2
$ul.Cells.Item($nr, 2).Value2 = "Chú thích màu: chữ xanh dương = số nhập tay · chữ xanh lá = lấy từ sheet GiaDinh · chữ đen = công thức tính · nền vàng = ô SV4 điền số đo · nền xám = chỉ tiêu không đo trực tiếp."
$ul.Cells.Item($nr + 1, 2).Value2 = "Ví dụ cách điền: chạy tai_thu/tai_thu.py trên máy chủ SV3, lấy 'Thông lượng giao dịch mới (GD/s)' của kịch bản 4_diem_quet trong tong_hop.md điền vào M6; p95 điền vào M$last."

# ======================= KetLuan =======================
Title $kl "ĐỀ TÀI 22 – KẾT LUẬN ƯỚC LƯỢNG (tự cập nhật theo sheet GiaDinh)" "ĐÂY LÀ ƯỚC LƯỢNG, CHƯA ĐO THỰC TẾ – cần SV4 đo để xác nhận."
Head $kl 4 @("STT", "Nhận định (công thức)")
$kq = @(
  "=`"Tải đỉnh tăng từ `"&FIXED(UocLuong!E6,2)&`" lên `"&FIXED(UocLuong!F6,2)&`" GD/s, chiếm `"&FIXED(UocLuong!I6*100,1)&`"%`"&`" năng lực máy chủ ước lượng (`"&NangLuc&`" GD/s) → `"&UocLuong!J6&`".`"",
  "=`"Băng thông đỉnh khoảng `"&FIXED(UocLuong!F16,1)&`" kbit/s ở 4 điểm, chỉ bằng `"&FIXED(UocLuong!I16*100,3)&`"%`"&`" cổng `"&TocDoCong&`" Mbit/s → mạng LAN không phải điểm nghẽn.`"",
  "=`"CSDL tăng tối đa `"&FIXED(UocLuong!F12,1)&`" MB/ngày; sau `"&NamLuu&`" năm cận trên `"&FIXED(UocLuong!F14,2)&`" GB; sao lưu `"&SoBanSao&`" bản cần `"&FIXED(UocLuong!F15,1)&`" GB = `"&FIXED(UocLuong!I15*100,1)&`"%`"&`" NAS → `"&UocLuong!J15&`".`"",
  "=`"Cổng switch có dây cần `"&UocLuong!F17&`"/`"&CongCoDay&`" cổng dự phòng; máy quét Wi-Fi `"&UocLuong!F18&`"/`"&MaxWifi&`" trên 1 AP; IP VLAN 30 `"&UocLuong!F19&`"/`"&IPVlan30&`" → không phải mua thêm thiết bị mạng, chỉ cắm vào cổng dự phòng Fa0/12-13.`"",
  "=`"Mỗi điểm quét sinh tối đa `"&FIXED(UocLuong!E8,0)&`" GD/ngày, bằng `"&FIXED(UocLuong!I8*100,1)&`"%`"&`" giới hạn `"&FIXED(MaxGDNgay,0)&`" của txn_id → `"&UocLuong!J8&`". Không phụ thuộc số điểm; chạy 2 ca trở lên phải tăng lên 5 chữ số.`"",
  "Việc phải làm khi thêm SP03, SP04: chạy du_lieu/seed_mo_rong_4_diem.sql (khai báo ScanPoints + tài khoản nv03, nv04), cắm máy vào Fa0/12-13 hoặc Wi-Fi KHO-QUETMA, cập nhật bảng IP.",
  "Thành phần cần theo dõi khi tăng tiếp: (1) năng lực ghi CSDL – SQLite một luồng ghi, chuyển PostgreSQL khi nhiều kho / hàng chục điểm; (2) vùng phủ và số máy trên AP – cần khảo sát sóng thật; (3) thời gian sao lưu khi CSDL lớn; (4) UPS cho máy chủ + switch.",
  "Giới hạn của mô hình: G08 (byte mạng/GD) và G10 (năng lực máy chủ) là giả định chưa đo trên hệ thống thật; Packet Tracer không chứng minh thông lượng hay vùng phủ Wi-Fi. SV4 điền cột L–M sheet UocLuong để kiểm chứng."
)
$r = 5; $i = 1
foreach ($x in $kq) {
  $kl.Cells.Item($r, 1).Value2 = [double]$i
  if ($x.StartsWith("=")) { $kl.Cells.Item($r, 2).Formula = $x } else { $kl.Cells.Item($r, 2).Value2 = $x }
  $kl.Cells.Item($r, 2).WrapText = $true; $r++; $i++
}
$kl.Columns.Item(1).ColumnWidth = 4; $kl.Columns.Item(2).ColumnWidth = 150
$kl.Range("A4:B$($r-1)").Borders.LineStyle = 1; $kl.Range("A5:B$($r-1)").VerticalAlignment = -4160

# ======================= ThuTai_GiaLap =======================
Title $tt "KẾT QUẢ CHẠY THỬ SCRIPT TẢI VỚI MÁY CHỦ GIẢ LẬP (27/10/2026)" "KHÔNG PHẢI SỐ ĐO HỆ THỐNG THẬT – chỉ để thử script và làm căn cứ chọn giả định G10. Nguồn: tai_thu/ket_qua/*THU_GIA_LAP*/tong_hop.md"
Head $tt 4 @("Chỉ tiêu", "Nhịp 3 s – 2 điểm", "Nhịp 3 s – 4 điểm", "Gắng sức – 2 điểm", "Gắng sức – 4 điểm")
$so = @(
  @("Thời gian mỗi kịch bản (s)", 15, 15, 10, 10),
  @("Tổng yêu cầu", 10, 20, 814, 1044),
  @("Giao dịch mới thành công (201)", 9, 19, 767, 998),
  @("Gửi trùng / nhận 409", "1 / 1", "1 / 1", "47 / 47", "46 / 46"),
  @("Thông lượng giao dịch mới (GD/s)", 0.6, 1.267, 76.7, 99.8),
  @("Độ trễ trung bình (ms)", 21.44, 24.13, 24.52, 38.27),
  @("Độ trễ p95 (ms)", 35.69, 39.19, 41.94, 74.51),
  @("Độ trễ lớn nhất (ms)", 39.77, 45.22, 68.4, 219.2),
  @("Lỗi không mong đợi", "0", "0", "0", "0"),
  @("Đối chiếu tồn sau tải (all_match)", "True", "True", "True", "True")
)
$r = 5
foreach ($s in $so) { for ($k = 0; $k -lt 5; $k++) { $v = $s[$k]; if ($v -is [string]) { $tt.Cells.Item($r, $k + 1).Value2 = $v } else { $tt.Cells.Item($r, $k + 1).Value2 = [double]$v }; if ($k -gt 0) { $tt.Cells.Item($r, $k + 1).Font.Color = $BLUE } }; $r++ }
$tt.Columns.Item(1).ColumnWidth = 38; for ($k = 2; $k -le 5; $k++) { $tt.Columns.Item($k).ColumnWidth = 18 }
$tt.Range("A4:E$($r-1)").Borders.LineStyle = 1
$tt.Cells.Item($r + 1, 1).Value2 = "Máy chạy thử: laptop của SV1, Windows 11, Python 3.13.2, SQLite 3.45.3, máy chủ giả lập cong_cu_thu/may_chu_gia_lap.py, cổng 18080 (8080 đang bị chương trình khác dùng)."

$ul.Activate()
$xl.Calculate()
if (Test-Path $out) { Remove-Item $out }
$wb.SaveAs($out, 51)

# ---- Kiểm tra: in kết quả và đếm lỗi công thức ----
$loi = 0
foreach ($s in @($gd, $ul, $kl)) { foreach ($c in $s.UsedRange.Cells) { if ("$($c.Text)".StartsWith("#")) { $loi++; Write-Output "LOI $($s.Name)!$($c.Address(0,0)) = $($c.Text)" } } }
for ($r = 5; $r -le $last; $r++) {
  Write-Output ("{0,-48} | {1,12} | {2,12} | {3,9} | {4,10} | {5,8} | {6}" -f $ul.Cells.Item($r, 2).Text, $ul.Cells.Item($r, 5).Text, $ul.Cells.Item($r, 6).Text, $ul.Cells.Item($r, 7).Text, $ul.Cells.Item($r, 8).Text, $ul.Cells.Item($r, 9).Text, $ul.Cells.Item($r, 10).Text)
}
for ($r = 5; $r -le 9; $r++) { Write-Output ("KL{0}: {1}" -f ($r - 4), $kl.Cells.Item($r, 2).Text) }
Write-Output "So o loi cong thuc: $loi"
$wb.Close($false); $xl.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($xl) | Out-Null
[GC]::Collect(); [GC]::WaitForPendingFinalizers()
Get-Process EXCEL -ErrorAction SilentlyContinue | Where-Object { $excel_truoc -notcontains $_.Id } | Stop-Process -Force
