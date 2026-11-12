param([string]$Harness, [string]$Tag = 'pr1', [switch]$SizesOnly)
$ErrorActionPreference = 'Continue'; $ProgressPreference = 'SilentlyContinue'
. F:\clip-run\clipfmt.ps1
$R = 'F:\r462-run'; $Out = "$R\out-$Tag"; New-Item -ItemType Directory -Force $Out | Out-Null
$key = 'HKCU:\Software\Classes\CLSID\{3BAC2B7E-73A2-4F3A-9CE7-5E9B438C59B4}\LocalServer32'
$installed = '"C:\Users\USER\AppData\Local\Programs\ReShiki\reshiki.exe" --ole-server'
$ServerExe = 'F:\clip-bin\reshiki-clip-11df00d5.exe'
$server = $null
$env:RESHIKI_INCHI_HELPER = $ServerExe; $env:RESHIKI_NAMING_HELPER = $ServerExe
"leftover before: $((Get-Process WINWORD,EXCEL,msedge,reshiki-clip-11df00d5 -EA SilentlyContinue | % { "$($_.Name)/$($_.Id)" }) -join ' ')"
"LocalServer32 before: $((Get-ItemProperty $key).'(default)')"
function NewData { $env:RESHIKI_DATA_DIR = (New-Item -ItemType Directory -Force "$R\data\$(Get-Random)").FullName }
function Server {
  if ($script:server -and -not $script:server.HasExited) { return }
  Set-ItemProperty $key '(default)' '"F:\r462-run\no-such-server.exe" --ole-server'
  NewData; $script:server = Start-Process $ServerExe -ArgumentList '--ole-server' -PassThru; Start-Sleep 3
}
function Copy-With($rsk, $imageOnly) {
  NewData; $env:CLIP_RSK = "$R\$rsk.rsk"; $env:CLIP_IMAGE_ONLY = $imageOnly
  $o = & $Harness clip_harness --ignored --exact --nocapture 2>&1 | Select-String 'image_only=|test result: F|panicked|error'
  "  copy: $($o -join ' | ')"
}
function Dump($tag) {
  $d = "$Out\$tag"; Remove-Item -Recurse -Force $d -EA SilentlyContinue
  $lines = Dump-Clipboard $d
  $total = 0; foreach ($l in $lines | Select -Skip 1) { if ($l -match '^\s*\d+\s+\d+\s+.+?\s+(-?\d+)(\s+\S*)?$' -and [long]$Matches[1] -gt 0) { $total += [long]$Matches[1] } }
  "  formats ($tag): total=$total bytes"; $lines | % { "    $_" }
  $files = (Get-ChildItem $d -File -EA SilentlyContinue | ? { $_.Name -match 'PNG|svg|PDF|Portable|CF_DIB|HTML' } | % FullName) -join ';'
  if ($files) { $env:CLIP_FILES = $files; & $Harness file_payload --ignored --exact --nocapture 2>&1 | Select-String '^file ' | % { "    payload: $($_.Line -replace [regex]::Escape($d + '\'), '')" } }
}
function PasteBack { & $Harness clip_paste --ignored --exact --nocapture 2>&1 | Select-String '^paste ' | % { "  ReShiki $($_.Line)" } }
function Media($docx, $pattern) {
  Add-Type -A System.IO.Compression.FileSystem
  $z = [IO.Compression.ZipFile]::OpenRead($docx); $files = @()
  foreach ($e in ($z.Entries | ? FullName -like $pattern)) { $p = "$docx-$($e.Name)"; [IO.Compression.ZipFileExtensions]::ExtractToFile($e, $p, $true); $files += $p }
  $z.Dispose()
  if ($files) { $env:CLIP_FILES = $files -join ';'; & $Harness file_payload --ignored --exact --nocapture 2>&1 | Select-String '^file ' | % { "  saved media: $($_.Line -replace [regex]::Escape($Out + '\'), '')" } } else { "  saved media: none" }
}
function Word-Trip($tag) {
  $w = $null; $d = $null; $f = $null
  try {
    $w = New-Object -ComObject Word.Application; $w.DisplayAlerts = 0; $d = $w.Documents.Add()
    $w.Selection.Paste(); Start-Sleep 1
    "  Word pasted: inline=$($d.InlineShapes.Count) floating=$($d.Shapes.Count) type=$(if ($d.InlineShapes.Count) { $d.InlineShapes.Item(1).Type })"
    if ($d.InlineShapes.Count -ge 1) { $d.InlineShapes.Item(1).Range.Copy() } elseif ($d.Shapes.Count -ge 1) { $d.Shapes.Item(1).Select(); $w.Selection.Copy() }
    Start-Sleep 1; Dump "$tag-word-copyback"; PasteBack
    $f = "$Out\$tag.docx"; $d.SaveAs2($f, 16)
  } catch { "  Word ERROR $_" }
  finally { if ($d) { $d.Saved = $true; $d.Close([ref]0) }; if ($w) { $w.Quit([ref]0) } }
  Start-Sleep 2; if ($f -and (Test-Path $f)) { Media $f 'word/media/*' }
}
function Excel-Trip($tag) {
  $x = $null; $wb = $null; $f = $null
  try {
    $x = New-Object -ComObject Excel.Application; $x.DisplayAlerts = $false; $wb = $x.Workbooks.Add(); $ws = $wb.Worksheets.Item(1)
    $ws.Range('B2').Select() | Out-Null; $ws.Paste(); Start-Sleep 1
    "  Excel pasted: shapes=$($ws.Shapes.Count) type=$(if ($ws.Shapes.Count) { $ws.Shapes.Item(1).Type })"
    if ($ws.Shapes.Count -ge 1) { $ws.Shapes.Item(1).Copy() }
    Start-Sleep 1; Dump "$tag-excel-copyback"; PasteBack
    $f = "$Out\$tag.xlsx"; $wb.SaveAs($f, 51)
  } catch { "  Excel ERROR $_" }
  finally { if ($wb) { $wb.Close($false) }; if ($x) { $x.Quit() } }
  Start-Sleep 2; if ($f -and (Test-Path $f)) { Media $f 'xl/media/*' }
}
function Edge-Trip($tag) {
  $u = "$R\edge-$(Get-Random)"
  $j = & node "$R\cdp_roundtrip.mjs" 'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe' F:\clip-run\probe.html 9413 $u 2>&1
  Start-Sleep 2; Get-CimInstance Win32_Process -Filter "Name='msedge.exe'" | ? CommandLine -like "*$u*" | % { Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue }
  "  Edge: $($j -join ' ')"
  Dump "$tag-edge-copyback"; PasteBack
  Start-Sleep 1; Remove-Item -Recurse -Force $u -EA SilentlyContinue
}
try {
  "=== Sizes (Copy and Copy Image for each drawing)"
  foreach ($rsk in 'caffeine','reaction','atorvastatin-x5','caffeine-photo') {
    foreach ($io in '0','1') { "--- $rsk image_only=$io"; Copy-With $rsk $io; Dump "$rsk-$io" }
  }
  if ($SizesOnly) { return }
  "=== Copy Image -> ReShiki directly"; Copy-With caffeine 1; PasteBack
  "=== Copy Image -> Word -> copy back"; Copy-With caffeine 1; Word-Trip 'image'
  "=== Copy Image -> Excel -> copy back"; Copy-With caffeine 1; Excel-Trip 'image'
  "=== Copy Image -> Edge -> copy back"; Copy-With caffeine 1; Edge-Trip 'image'
  "=== Copy -> Word (OLE object) -> copy back"; Server; Copy-With caffeine 0; Word-Trip 'copy'
  "=== Copy -> Edge -> copy back"; Copy-With caffeine 0; Edge-Trip 'copy'
} catch { "ERROR: $_" }
finally {
  if ($server) { Stop-Process -Id $server.Id -Force -EA SilentlyContinue }
  Get-CimInstance Win32_Process -Filter "Name='reshiki-clip-11df00d5.exe'" | % { Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue }
  Set-ItemProperty $key '(default)' $installed
  "LocalServer32 restored: $((Get-ItemProperty $key).'(default)')"
  "leftover after: $((Get-Process WINWORD,EXCEL,msedge,reshiki-clip-11df00d5 -EA SilentlyContinue | % { "$($_.Name)/$($_.Id)" }) -join ' ')"
}
