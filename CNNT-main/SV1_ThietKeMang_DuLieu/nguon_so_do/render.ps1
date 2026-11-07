# Xuất các sơ đồ HTML/SVG trong thư mục này ra PNG bằng Microsoft Edge headless.
# Chạy: powershell -ExecutionPolicy Bypass -File render.ps1
$edge = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$out  = Split-Path -Parent $here
$ds = @(
  @{ name = "01_SoDoHaTang";     w = 1920; h = 1200 },
  @{ name = "02_MoHinhDuLieu";   w = 1920; h = 1160 },
  @{ name = "04_SoDoLuongDuLieu"; w = 1920; h = 1460 }
)
foreach ($d in $ds) {
  $src = Join-Path $here ($d.name + ".html")
  if (-not (Test-Path $src)) { continue }
  $png = Join-Path $out ($d.name + ".png")
  $uri = ([System.Uri]$src).AbsoluteUri
  & $edge --headless=new --disable-gpu --hide-scrollbars --force-device-scale-factor=1.5 `
    --window-size="$($d.w),$($d.h)" --virtual-time-budget=3000 --screenshot="$png" $uri 2>$null | Out-Null
  Write-Output "$($d.name).png : $(Test-Path $png)"
}
