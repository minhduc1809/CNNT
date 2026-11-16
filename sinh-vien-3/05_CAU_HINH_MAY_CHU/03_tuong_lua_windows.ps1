<#
 03_tuong_lua_windows.ps1  (SV3 - CV01, phoi hop SV1)
 Ap dung quy tac truy cap tren may chu bang Windows Firewall theo bang QuyTacTruyCap.csv cua SV1:
   - Diem quet (VLAN 30) -> API 8080 (cho phep), ping (cho phep)
   - Diem quet -> CSDL 3306, SSH 22 (chan)
   - Van phong (VLAN 20) -> API 8080 (cho phep); SSH 22 chi tu PC quan tri
 Chay bang PowerShell "Run as administrator". Co the chay lai nhieu lan (xoa quy tac WH-* cu truoc).
#>
param(
    [string]$MangDiemQuet = "192.168.30.0/24",
    [string]$MangVanPhong = "192.168.20.0/24",
    [string]$MayQuanTri = "192.168.20.12",
    [int]$CongAPI = 8080,
    [int]$CongCSDL = 3306,
    [int]$CongSSH = 22
)

$ErrorActionPreference = "Stop"

Write-Host "Xoa quy tac WH-* cu (neu co)..."
Get-NetFirewallRule -DisplayName "WH-*" -ErrorAction SilentlyContinue | Remove-NetFirewallRule

# Bat firewall cho moi profile
Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled True

# --- CHO PHEP ---
New-NetFirewallRule -DisplayName "WH-ALLOW-API-tu-diem-quet" -Direction Inbound -Protocol TCP `
    -LocalPort $CongAPI -RemoteAddress $MangDiemQuet -Action Allow -Profile Any | Out-Null
New-NetFirewallRule -DisplayName "WH-ALLOW-API-tu-van-phong" -Direction Inbound -Protocol TCP `
    -LocalPort $CongAPI -RemoteAddress $MangVanPhong -Action Allow -Profile Any | Out-Null
New-NetFirewallRule -DisplayName "WH-ALLOW-PING-tu-diem-quet" -Direction Inbound -Protocol ICMPv4 `
    -IcmpType 8 -RemoteAddress $MangDiemQuet -Action Allow -Profile Any | Out-Null
New-NetFirewallRule -DisplayName "WH-ALLOW-SSH-tu-may-quan-tri" -Direction Inbound -Protocol TCP `
    -LocalPort $CongSSH -RemoteAddress $MayQuanTri -Action Allow -Profile Any | Out-Null

# --- CHAN (quy tac chan duoc uu tien hon quy tac cho phep) ---
New-NetFirewallRule -DisplayName "WH-BLOCK-CSDL-tu-diem-quet-va-van-phong" -Direction Inbound -Protocol TCP `
    -LocalPort $CongCSDL -RemoteAddress @($MangDiemQuet, $MangVanPhong) -Action Block -Profile Any | Out-Null
New-NetFirewallRule -DisplayName "WH-BLOCK-SSH-tu-diem-quet" -Direction Inbound -Protocol TCP `
    -LocalPort $CongSSH -RemoteAddress $MangDiemQuet -Action Block -Profile Any | Out-Null

Write-Host "Da tao quy tac. Danh sach:"
Get-NetFirewallRule -DisplayName "WH-*" |
    Format-Table DisplayName, Direction, Action, Enabled -AutoSize

Write-Host ""
Write-Host "LUU Y: quy tac CHO PHEP SSH chi co tac dung khi da cai OpenSSH Server (Windows co the khong co SSH)."
Write-Host "Kiem chung hai chieu tu may diem quet (xem bang ket qua o BangKiemTraKetNoi cua SV1):"
Write-Host "  Test-NetConnection <IP may chu> -Port $CongAPI   -> mong doi TcpTestSucceeded = True"
Write-Host "  Test-NetConnection <IP may chu> -Port $CongCSDL  -> mong doi TcpTestSucceeded = False"
Write-Host "  Test-NetConnection <IP may chu> -Port $CongSSH   -> mong doi TcpTestSucceeded = False"
