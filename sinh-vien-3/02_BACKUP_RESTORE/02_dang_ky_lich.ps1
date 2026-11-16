<#
 02_dang_ky_lich.ps1  (SV3 - CV03)
 1) Tao file cau hinh dang nhap cho mysqldump (hoi mat khau, khoa quyen file chi con Administrators + SYSTEM).
 2) Dang ky tac vu Windows Task Scheduler chay 01_sao_luu.ps1 theo lich.
 Chay bang PowerShell "Run as administrator".

 Vi du:
   .\02_dang_ky_lich.ps1                    # sao luu moi ngay luc 02:00
   .\02_dang_ky_lich.ps1 -ChuKyPhut 5       # DEMO: sao luu moi 5 phut (de co ban sao luu do lich tao truoc khi nop)
   .\02_dang_ky_lich.ps1 -ChayNgay          # dang ky xong chay thu 1 lan ngay
 Tac vu chay bang tai khoan SYSTEM de tranh loi thieu quyen "Log on as a batch job".
#>
param(
    [string]$TenTask    = "WH-SaoLuu-CSDL",
    [string]$Gio        = "02:00",
    [int]$ChuKyPhut     = 0,
    [string]$UserDump   = "wh_dump",
    [string]$ThuMucSaoLuu = "C:\SmartWarehouse\backup",
    [string]$ThuMucScript = "C:\SmartWarehouse\app",
    [switch]$ChayNgay
)

$ErrorActionPreference = "Stop"

New-Item -ItemType Directory -Force -Path $ThuMucSaoLuu | Out-Null
New-Item -ItemType Directory -Force -Path $ThuMucScript | Out-Null

# --- 1. File cau hinh dang nhap ---
$cnf = Join-Path $ThuMucSaoLuu ".my_dump.cnf"
$mk  = Read-Host "Nhap mat khau cua tai khoan MySQL '$UserDump' (da tao bang 00_tao_user_sao_luu.sql)" -AsSecureString
$mkRo = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($mk))
$noiDung = "[client]`r`nuser=$UserDump`r`npassword=`"$mkRo`"`r`nhost=127.0.0.1`r`n"
[IO.File]::WriteAllText($cnf, $noiDung, (New-Object Text.UTF8Encoding($false)))
$mkRo = $null
icacls $cnf /inheritance:r | Out-Null
icacls $cnf /grant:r "*S-1-5-32-544:F" "*S-1-5-18:F" | Out-Null   # Administrators, SYSTEM
Write-Host "Da tao $cnf (chi Administrators va SYSTEM doc duoc)."

# --- 2. Sao chep script sao luu ---
$nguon = Join-Path $PSScriptRoot "01_sao_luu.ps1"
$dich  = Join-Path $ThuMucScript "01_sao_luu.ps1"
Copy-Item -Path $nguon -Destination $dich -Force
Write-Host "Da chep script sao luu den $dich"

# --- 3. Dang ky tac vu ---
$hanhDong = New-ScheduledTaskAction -Execute "powershell.exe" `
    -Argument ("-NoProfile -ExecutionPolicy Bypass -File `"{0}`" -Nguon Lich" -f $dich)

if ($ChuKyPhut -gt 0) {
    $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date).AddMinutes(1) `
        -RepetitionInterval (New-TimeSpan -Minutes $ChuKyPhut) -RepetitionDuration (New-TimeSpan -Days 3650)
    Write-Host "Lich: moi $ChuKyPhut phut (che do demo)."
} else {
    $trigger = New-ScheduledTaskTrigger -Daily -At $Gio
    Write-Host "Lich: moi ngay luc $Gio."
}
$principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount -RunLevel Highest
$caiDat = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask -TaskName $TenTask -Action $hanhDong -Trigger $trigger `
    -Principal $principal -Settings $caiDat -Force | Out-Null

Write-Host "Da dang ky tac vu '$TenTask'. Thong tin (chup anh lam minh chung cau hinh lich):"
Get-ScheduledTask -TaskName $TenTask | Get-ScheduledTaskInfo | Format-List TaskName, NextRunTime, LastRunTime, LastTaskResult
(Get-ScheduledTask -TaskName $TenTask).Triggers | Format-List *

if ($ChayNgay) {
    Start-ScheduledTask -TaskName $TenTask
    Start-Sleep -Seconds 8
    Write-Host "Noi dung nhat ky backup.log:"
    Get-Content (Join-Path $ThuMucSaoLuu "backup.log") -Tail 5
}
