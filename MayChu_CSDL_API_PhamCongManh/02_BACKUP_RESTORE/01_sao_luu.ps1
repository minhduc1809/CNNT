<#
 01_sao_luu.ps1  (SV3 - CV03)
 Sao luu CSDL smart_warehouse bang mysqldump vao thu muc tach rieng.
 - Dump gom ca stored procedure (--routines), trigger, event.
 - Dung --result-file (khong dung toan tu '>' vi PowerShell 5.1 se ghi file UTF-16, khoi phuc bi loi).
 - Ghi nhat ky backup.log: thoi diem, nguon (Lich/ThuCong), duong dan, kich thuoc, SHA256, thoi gian chay.
 - Xoa ban sao luu cu hon $GiuNgay ngay.
 Thong tin dang nhap doc tu file cau hinh (tao boi 02_dang_ky_lich.ps1), KHONG ghi mat khau trong script.

 Chay thu cong: .\01_sao_luu.ps1
#>
param(
    [string]$ThuMucSaoLuu = "C:\SmartWarehouse\backup",
    [string]$CSDL         = "smart_warehouse",
    [string]$FileCauHinh  = "C:\SmartWarehouse\backup\.my_dump.cnf",
    [string]$MysqldumpExe = "",
    [int]$GiuNgay         = 14,
    [string]$Nguon        = "ThuCong"
)

$ErrorActionPreference = "Stop"

function Tim-Mysqldump {
    if ($MysqldumpExe -and (Test-Path $MysqldumpExe)) { return $MysqldumpExe }
    $c = Get-Command mysqldump.exe -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    $f = Get-ChildItem "C:\Program Files\MySQL\MySQL Server *\bin\mysqldump.exe" -ErrorAction SilentlyContinue |
         Sort-Object FullName -Descending | Select-Object -First 1
    if ($f) { return $f.FullName }
    throw "Khong tim thay mysqldump.exe. Truyen -MysqldumpExe 'duong dan day du'."
}

New-Item -ItemType Directory -Force -Path $ThuMucSaoLuu | Out-Null
$log   = Join-Path $ThuMucSaoLuu "backup.log"
$ts    = Get-Date -Format "yyyyMMdd_HHmmss"
$tmp   = Join-Path $ThuMucSaoLuu ("{0}_{1}.sql.tmp" -f $CSDL, $ts)
$final = Join-Path $ThuMucSaoLuu ("{0}_{1}.sql" -f $CSDL, $ts)
$batDau = Get-Date
$sw = [Diagnostics.Stopwatch]::StartNew()

try {
    if (-not (Test-Path $FileCauHinh)) { throw "Chua co file cau hinh dang nhap: $FileCauHinh (chay 02_dang_ky_lich.ps1 truoc)" }
    $exe = Tim-Mysqldump

    $thamSo = @(
        "--defaults-extra-file=$FileCauHinh",   # phai la tham so dau tien
        "--single-transaction",
        "--routines", "--triggers", "--events",
        "--no-tablespaces",
        "--set-gtid-purged=OFF",
        "--default-character-set=utf8mb4",
        "--result-file=$tmp",
        $CSDL
    )
    & $exe @thamSo
    if ($LASTEXITCODE -ne 0) { throw "mysqldump tra ve ma loi $LASTEXITCODE" }

    if (-not (Test-Path $tmp) -or (Get-Item $tmp).Length -eq 0) { throw "File dump rong hoac khong ton tai" }
    $duoi = (Get-Content $tmp -Tail 3) -join " "
    if ($duoi -notmatch "Dump completed") { throw "File dump khong ket thuc day du (thieu dong 'Dump completed')" }

    Move-Item -Path $tmp -Destination $final
    $sw.Stop()
    $kichThuoc = (Get-Item $final).Length
    $hash = (Get-FileHash -Path $final -Algorithm SHA256).Hash
    $dong = "{0} | Nguon={1} | File={2} | KichThuoc={3} bytes | SHA256={4} | ThoiGian={5:N1} s | KetQua=OK" -f `
            $batDau.ToString("yyyy-MM-dd HH:mm:ss"), $Nguon, $final, $kichThuoc, $hash, $sw.Elapsed.TotalSeconds
    Add-Content -Path $log -Value $dong -Encoding UTF8
    Write-Host $dong

    # Xoa ban cu
    Get-ChildItem $ThuMucSaoLuu -Filter ("{0}_*.sql" -f $CSDL) |
        Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-$GiuNgay) } |
        Remove-Item -Force
    exit 0
}
catch {
    $sw.Stop()
    if (Test-Path $tmp) { Remove-Item $tmp -Force -ErrorAction SilentlyContinue }
    $dong = "{0} | Nguon={1} | KetQua=LOI | ChiTiet={2}" -f $batDau.ToString("yyyy-MM-dd HH:mm:ss"), $Nguon, $_.Exception.Message
    Add-Content -Path $log -Value $dong -Encoding UTF8
    Write-Host $dong -ForegroundColor Red
    exit 1
}
