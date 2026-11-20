<#
 03_khoi_phuc_va_doi_chieu.ps1  (SV3 - CV03)
 Khoi phuc ban sao luu vao CSDL TACH BIET (smart_warehouse_restore_test), do thoi gian khoi phuc,
 doi chieu voi CSDL goc: so ban ghi, tong ton, CHECKSUM TABLE, so stored procedure.
 So sanh thoi gian khoi phuc do duoc voi RTO gia dinh 30 phut.
 Ket qua ghi vao C:\SmartWarehouse\evidence\restore_test_<thoi gian>.txt

 Chay: .\03_khoi_phuc_va_doi_chieu.ps1                       (dung ban sao luu moi nhat)
       .\03_khoi_phuc_va_doi_chieu.ps1 -SaoLuuMoiTruoc       (sao luu moi ngay truoc khi khoi phuc, de doi chieu khong bi lech)
       .\03_khoi_phuc_va_doi_chieu.ps1 -FileSao "C:\...\smart_warehouse_20261110_020000.sql"
 Mat khau tai khoan MySQL quan tri (can quyen tao CSDL) duoc hoi khi chay, khong luu lai.
 LUU Y: chi tac dong vao CSDL smart_warehouse_restore_test, KHONG sua CSDL goc.
#>
param(
    [string]$ThuMucSaoLuu = "C:\SmartWarehouse\backup",
    [string]$ThuMucMinhChung = "C:\SmartWarehouse\evidence",
    [string]$FileSao = "",
    [string]$CSDLGoc = "smart_warehouse",
    [string]$CSDLThu = "smart_warehouse_restore_test",
    [string]$UserAdmin = "root",
    [string]$MatKhauAdmin = "123456",
    [int]$RTOGiay = 1800,
    [string]$MysqlExe = "",
    [switch]$SaoLuuMoiTruoc,
    [switch]$XoaCSDLThuSau
)

$ErrorActionPreference = "Continue"   # tu kiem tra $LASTEXITCODE, tranh canh bao stderr lam dung script

function Tim-Mysql {
    if ($MysqlExe -and (Test-Path $MysqlExe)) { return $MysqlExe }
    $c = Get-Command mysql.exe -ErrorAction SilentlyContinue
    if ($c) { return $c.Source }
    $f = Get-ChildItem "C:\Program Files\MySQL\MySQL Server *\bin\mysql.exe" -ErrorAction SilentlyContinue |
         Sort-Object FullName -Descending | Select-Object -First 1
    if ($f) { return $f.FullName }
    throw "Khong tim thay mysql.exe. Truyen -MysqlExe 'duong dan day du'."
}

$mysql = Tim-Mysql
try {
    New-Item -ItemType Directory -Force -Path $ThuMucMinhChung -ErrorAction Stop | Out-Null
} catch {
    $ThuMucMinhChung = Join-Path $PSScriptRoot "evidence"
    New-Item -ItemType Directory -Force -Path $ThuMucMinhChung -Force -ErrorAction SilentlyContinue | Out-Null
}
$ketQuaFile = Join-Path $ThuMucMinhChung ("restore_test_{0}.txt" -f (Get-Date -Format "yyyyMMdd_HHmmss"))
$dong = New-Object System.Collections.Generic.List[string]
function Ghi($s) { Write-Host $s; $dong.Add($s) }

# --- mat khau admin ---
if (-not $MatKhauAdmin) {
    if ($env:MYSQL_PWD) {
        $MatKhauAdmin = $env:MYSQL_PWD
    } else {
        $mk = Read-Host "Nhap mat khau MySQL cua '$UserAdmin'" -AsSecureString
        $MatKhauAdmin = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($mk))
    }
}
$env:MYSQL_PWD = $MatKhauAdmin

function SQL($db, $q) {
    $thamSo = @("-u", $UserAdmin, "-h", "127.0.0.1", "-N", "-B", "-e", $q)
    if ($db) { $thamSo += $db }
    $r = & $mysql @thamSo 2>&1 | ForEach-Object { "$_" }
    if ($LASTEXITCODE -ne 0) { throw ("Loi MySQL: " + ($r -join " ")) }
    return (($r | Where-Object { $_ -notmatch "Using a password" }) -join "`n").Trim()
}

try {
    if ($SaoLuuMoiTruoc) {
        Write-Host "Dang sao luu moi truoc khi khoi phuc..."
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File (Join-Path $PSScriptRoot "01_sao_luu.ps1") -Nguon ThuCong -ThuMucSaoLuu $ThuMucSaoLuu
        if ($LASTEXITCODE -ne 0) { throw "Sao luu truoc khi khoi phuc that bai" }
    }

    if (-not $FileSao) {
        $moiNhat = Get-ChildItem $ThuMucSaoLuu -Filter ("{0}_*.sql" -f $CSDLGoc) -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
        if ($moiNhat -and (Test-Path $moiNhat.FullName)) {
            try {
                $testStream = [IO.File]::OpenRead($moiNhat.FullName)
                $testStream.Close()
                $FileSao = $moiNhat.FullName
            } catch {
                $FileSao = ""
            }
        }
        if (-not $FileSao) {
            $fileCucBo = Get-ChildItem $PSScriptRoot -Filter ("smart_warehouse_*.sql") -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
            if ($fileCucBo) {
                $FileSao = $fileCucBo.FullName
            } else {
                throw "Khong co ban sao luu nao doc duoc."
            }
        }
    }
    if (-not (Test-Path $FileSao)) { throw "Khong thay file: $FileSao" }

    Ghi ("Thoi diem chay: {0}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
    Ghi ("File sao luu   : {0}" -f $FileSao)
    Ghi ("Kich thuoc     : {0} bytes" -f (Get-Item $FileSao).Length)
    Ghi ("SHA256         : {0}" -f (Get-FileHash $FileSao -Algorithm SHA256).Hash)
    Ghi ("Phien ban MySQL: {0}" -f (SQL $null "SELECT VERSION();"))
    Ghi ""

    # --- Khoi phuc ---
    $tong = [Diagnostics.Stopwatch]::StartNew()
    $swKP = [Diagnostics.Stopwatch]::StartNew()
    SQL $null "DROP DATABASE IF EXISTS ``$CSDLThu``; CREATE DATABASE ``$CSDLThu`` CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" | Out-Null
    cmd /c "`"$mysql`" -u $UserAdmin -h 127.0.0.1 --default-character-set=utf8mb4 $CSDLThu < `"$FileSao`""
    if ($LASTEXITCODE -ne 0) { throw "Nap file sao luu vao $CSDLThu that bai (ma $LASTEXITCODE)" }
    $swKP.Stop()

    # --- Doi chieu ---
    $bang = @("Products", "Inventory", "Users", "ScanPoints", "warehouse_transactions")
    $chenhLech = New-Object System.Collections.Generic.List[string]

    Ghi "| Hang muc | CSDL goc | CSDL khoi phuc | Ket luan |"
    Ghi "|---|---|---|---|"
    foreach ($b in $bang) {
        $g = SQL $CSDLGoc "SELECT COUNT(*) FROM ``$b``;"
        $t = SQL $CSDLThu "SELECT COUNT(*) FROM ``$b``;"
        $kl = if ($g -eq $t) { "Khop" } else { "LECH" }
        if ($kl -eq "LECH") { $chenhLech.Add("So ban ghi $b : goc=$g, khoi phuc=$t") }
        Ghi ("| So ban ghi {0} | {1} | {2} | {3} |" -f $b, $g, $t, $kl)
    }

    $sg = SQL $CSDLGoc "SELECT IFNULL(SUM(quantity),0) FROM Inventory;"
    $st = SQL $CSDLThu "SELECT IFNULL(SUM(quantity),0) FROM Inventory;"
    $kl = if ($sg -eq $st) { "Khop" } else { "LECH" }
    if ($kl -eq "LECH") { $chenhLech.Add("Tong ton Inventory: goc=$sg, khoi phuc=$st") }
    Ghi ("| Tong ton (SUM quantity) | {0} | {1} | {2} |" -f $sg, $st, $kl)

    foreach ($b in $bang) {
        $cg = (SQL $CSDLGoc "CHECKSUM TABLE ``$b``;") -split "\s+" | Select-Object -Last 1
        $ct = (SQL $CSDLThu "CHECKSUM TABLE ``$b``;") -split "\s+" | Select-Object -Last 1
        $kl = if ($cg -eq $ct) { "Khop" } else { "LECH" }
        if ($kl -eq "LECH") { $chenhLech.Add("CHECKSUM $b : goc=$cg, khoi phuc=$ct") }
        Ghi ("| CHECKSUM {0} | {1} | {2} | {3} |" -f $b, $cg, $ct, $kl)
    }

    $rg = SQL $null "SELECT COUNT(*) FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='$CSDLGoc';"
    $rt = SQL $null "SELECT COUNT(*) FROM information_schema.ROUTINES WHERE ROUTINE_SCHEMA='$CSDLThu';"
    $kl = if ($rg -eq $rt) { "Khop" } else { "LECH" }
    if ($kl -eq "LECH") { $chenhLech.Add("So stored procedure: goc=$rg, khoi phuc=$rt (ban sao luu thieu --routines?)") }
    Ghi ("| So stored procedure | {0} | {1} | {2} |" -f $rg, $rt, $kl)

    $tong.Stop()
    Ghi ""
    Ghi ("Thoi gian khoi phuc (tao CSDL + nap file): {0:N1} giay" -f $swKP.Elapsed.TotalSeconds)
    Ghi ("Thoi gian ca quy trinh (gom doi chieu)   : {0:N1} giay" -f $tong.Elapsed.TotalSeconds)
    Ghi ("RTO gia dinh                              : {0} giay ({1} phut)" -f $RTOGiay, ($RTOGiay / 60))
    $rto = if ($swKP.Elapsed.TotalSeconds -le $RTOGiay) { "TRONG RTO" } else { "VUOT RTO" }
    Ghi ("So sanh voi RTO                           : {0}" -f $rto)
    Ghi ""
    if ($chenhLech.Count -eq 0) {
        Ghi "KET LUAN: moi hang muc doi chieu deu khop."
    } else {
        Ghi "CO CHENH LECH (ghi vao bao cao, giai thich nguyen nhan):"
        $chenhLech | ForEach-Object { Ghi ("  - " + $_) }
        Ghi "Goi y: neu CSDL goc da co giao dich moi SAU thoi diem sao luu thi lech la binh thuong - chay lai voi -SaoLuuMoiTruoc."
    }

    if ($XoaCSDLThuSau) { SQL $null "DROP DATABASE IF EXISTS ``$CSDLThu``;" | Out-Null; Ghi "Da xoa $CSDLThu." }
}
catch {
    Ghi ("LOI: " + $_.Exception.Message)
}
finally {
    Remove-Item Env:\MYSQL_PWD -ErrorAction SilentlyContinue
    $dong | Out-File -FilePath $ketQuaFile -Encoding utf8
    Write-Host "`nDa ghi ket qua: $ketQuaFile"
}
