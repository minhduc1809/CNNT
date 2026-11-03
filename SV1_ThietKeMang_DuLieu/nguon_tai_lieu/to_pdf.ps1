# Chuyển .docx sang .pdf bằng Microsoft Word (COM). Tham số: đường dẫn docx, đường dẫn pdf
param([string]$docx, [string]$pdf)
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
  $doc = $word.Documents.Open($docx, $false, $true)
  $doc.Fields.Update() | Out-Null
  $doc.ExportAsFixedFormat($pdf, 17)
  Write-Output "pages: $($doc.ComputeStatistics(2))"
  $doc.Close($false)
} finally { $word.Quit() }
