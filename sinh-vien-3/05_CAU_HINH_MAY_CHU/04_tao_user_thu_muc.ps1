<#
 04_tao_user_thu_muc.ps1  (SV3 - CV01/CV02, tang 3 phan quyen he dieu hanh)
 Tao user he dieu hanh rieng cho dich vu (wh_service) va sao luu (wh_backup),
 tao thu muc du lieu va thu muc sao luu TACH RIENG, phan quyen NTFS toi thieu.
 Mat khau duoc hoi khi chay, khong ghi vao file.
 Chay bang PowerShell "Run as administrator".
#>
param(
    [string]$Goc = "C:\SmartWarehouse"
)

$ErrorActionPreference = "Stop"

function Tao-User($ten, $moTa) {
    if (-not (Get-LocalUser -Name $ten -ErrorAction SilentlyContinue)) {
        $mk = Read-Host "Nhap mat khau cho user $ten" -AsSecureString
        New-LocalUser -Name $ten -Password $mk -Description $moTa `
            -PasswordNeverExpires -UserMayNotChangePassword | Out-Null
        Write-Host "Da tao user $ten"
    } else {
        Write-Host "User $ten da ton tai, bo qua"
    }
}

Write-Host "=== [1/3] Tao user he dieu hanh ==="
Tao-User "wh_service" "Chay dich vu API kho (khong phai admin)"
Tao-User "wh_backup"  "Chay sao luu CSDL (khong phai admin)"

Write-Host "=== [2/3] Tao thu muc tach rieng ==="
$dirApp    = Join-Path $Goc "app"
$dirData   = Join-Path $Goc "data"
$dirLogs   = Join-Path $Goc "logs"
$dirBackup = Join-Path $Goc "backup"
$dirEvid   = Join-Path $Goc "evidence"
foreach ($d in @($dirApp, $dirData, $dirLogs, $dirBackup, $dirEvid)) {
    New-Item -ItemType Directory -Force -Path $d | Out-Null
}

Write-Host "=== [3/3] Phan quyen NTFS ==="
# Ghi chu: thu muc du lieu that cua MySQL nam o C:\ProgramData\MySQL va do tai khoan dich vu MySQL quan ly - KHONG doi quyen thu muc do.
# 'data' o day la thu muc du lieu cua ung dung (file tam, tep cau hinh du lieu), tach khoi 'backup'.

function Dat-Quyen($duongDan, $quyenList) {
    icacls $duongDan /inheritance:r | Out-Null
    icacls $duongDan /grant:r "*S-1-5-32-544:(OI)(CI)F" "*S-1-5-18:(OI)(CI)F" | Out-Null   # Administrators, SYSTEM
    foreach ($q in $quyenList) { icacls $duongDan /grant:r $q | Out-Null }
}

Dat-Quyen $dirApp    @("wh_service:(OI)(CI)RX")   # chi doc + chay ma nguon
Dat-Quyen $dirData   @("wh_service:(OI)(CI)M")    # doc/ghi du lieu ung dung
Dat-Quyen $dirLogs   @("wh_service:(OI)(CI)M")
Dat-Quyen $dirBackup @("wh_backup:(OI)(CI)M")     # CHI wh_backup; wh_service KHONG co quyen vao day
Dat-Quyen $dirEvid   @()                           # chi Administrators/SYSTEM

Write-Host ""
Write-Host "Quyen hien tai (chup anh lam minh chung):"
foreach ($d in @($dirApp, $dirData, $dirBackup)) {
    Write-Host "--- $d"
    icacls $d
}
