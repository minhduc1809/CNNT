<#
 05_kiem_tra_may_chu.ps1  (SV3 - CV01)
 Thu thap bang chung cau hinh may chu vao 1 file van ban.
 Chay bang PowerShell "Run as administrator". Khong in mat khau.
#>
param(
    [string]$ThuMucMinhChung = "C:\SmartWarehouse\evidence",
    [string]$Goc = "C:\SmartWarehouse"
)

New-Item -ItemType Directory -Force -Path $ThuMucMinhChung | Out-Null
$file = Join-Path $ThuMucMinhChung ("server_check_{0}.txt" -f (Get-Date -Format "yyyyMMdd_HHmmss"))

function Muc($tieuDe, [scriptblock]$lenh) {
    "`r`n===== $tieuDe =====" | Out-File $file -Append -Encoding utf8
    try { & $lenh 2>&1 | Out-String | Out-File $file -Append -Encoding utf8 }
    catch { "LOI: $_" | Out-File $file -Append -Encoding utf8 }
}

"Thoi diem kiem tra: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss zzz')" | Out-File $file -Encoding utf8
"May: $env:COMPUTERNAME" | Out-File $file -Append -Encoding utf8

Muc "Phien ban he dieu hanh"   { (Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version) }
Muc "ipconfig /all"            { ipconfig /all }
Muc "Mui gio"                  { Get-TimeZone }
Muc "Dong bo gio (w32tm)"      { w32tm /query /status; w32tm /query /configuration | Select-String "NtpServer|Type" }
Muc "Dich vu MySQL"            { Get-Service -Name "MySQL*" | Format-Table Name, Status, StartType -AutoSize }
Muc "Cong 3306 dang lang nghe tren dia chi nao (mong doi 127.0.0.1)" {
    Get-NetTCPConnection -LocalPort 3306 -State Listen | Format-Table LocalAddress, LocalPort, State, OwningProcess -AutoSize }
Muc "Cong API 8080 (neu dich vu dang chay)" {
    Get-NetTCPConnection -LocalPort 8080 -State Listen -ErrorAction SilentlyContinue | Format-Table LocalAddress, LocalPort, State -AutoSize }
Muc "User he dieu hanh rieng" {
    Get-LocalUser -Name wh_service, wh_backup -ErrorAction SilentlyContinue | Format-Table Name, Enabled, PasswordExpires -AutoSize }
Muc "Quy tac tuong lua WH-*"   {
    Get-NetFirewallRule -DisplayName "WH-*" -ErrorAction SilentlyContinue | Format-Table DisplayName, Direction, Action, Enabled -AutoSize }
foreach ($t in @("app","data","logs","backup")) {
    Muc "Quyen thu muc $t" { icacls (Join-Path $Goc $t) }
}

Write-Host "Da ghi: $file"
