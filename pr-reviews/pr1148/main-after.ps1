param([string]$Harness, [string]$Release)
$ErrorActionPreference = 'Continue'; $ProgressPreference = 'SilentlyContinue'
. F:\clip-run\clipfmt.ps1; . F:\clip-run\office.ps1
$key = 'HKCU:\Software\Classes\CLSID\{3BAC2B7E-73A2-4F3A-9CE7-5E9B438C59B4}\LocalServer32'
$installed = '"' + $env:LOCALAPPDATA + '\Programs\ReShiki\reshiki.exe" --ole-server'
$env:CLIP_RSK = 'F:\clip-run\caffeine.rsk'
$server = $null
function Server {
  if ($script:server -and -not $script:server.HasExited) { return }
  Set-ItemProperty $key '(default)' '"F:\clip-run\no-such-server.exe" --ole-server'
  $env:RESHIKI_DATA_DIR = (New-Item -ItemType Directory -Force "F:\clip-run\data\srv-$(Get-Random)").FullName
  $script:server = Start-Process $Release -ArgumentList '--ole-server' -PassThru; Start-Sleep 3
}
function Copy-With($imageOnly, $tag) {
  $env:RESHIKI_DATA_DIR = (New-Item -ItemType Directory -Force "F:\clip-run\data\copy-$(Get-Random)").FullName
  $env:CLIP_IMAGE_ONLY = $imageOnly
  $o = & $Harness clip_harness --ignored --exact --nocapture 2>&1 | Select-String 'image_only=|test result|panicked'
  "harness: $(($o -join ' | ') -replace 'notices=.*?\] \|', '|')"
  "--- formats after $tag"
  Dump-Clipboard "F:\clip-run\out\after-$tag"
}
function Word-RoundTrip {
  $w = $null; $d = $null
  try {
    $w = New-Object -ComObject Word.Application; $w.DisplayAlerts = 0; $d = $w.Documents.Add()
    $w.Selection.Paste(); $i = $d.InlineShapes.Item(1)
    "Word pasted type=$($i.Type) progid=$($i.OLEFormat.ProgID); copying the object back out of Word"
    $i.Range.Copy(); Start-Sleep 1
    $env:RESHIKI_DATA_DIR = (New-Item -ItemType Directory -Force "F:\clip-run\data\paste-$(Get-Random)").FullName
    $o = & $Harness clip_paste --ignored --exact --nocapture 2>&1 | Select-String 'paste native|test result|panicked'
    "ReShiki paste of the Word object: $($o -join ' | ')"
  } catch { "Word round trip: ERROR $_" }
  finally { if ($d) { $d.Saved = $true; $d.Close([ref]0) }; if ($w) { $w.Quit([ref]0) } }
}
try {
  "=== Copy (after fix)"
  Copy-With '0' 'copy'; Server; Word-Paste; Server; PowerPoint-Paste; Server; Excel-Paste; Edge-Paste 'after-copy'
  "=== Office round trip (after fix)"
  Copy-With '0' 'copy'; Server; Word-RoundTrip
  "=== Copy Image (after fix)"
  Copy-With '1' 'image'; Edge-Paste 'after-image'
} catch { "ERROR: $_" }
finally {
  if ($server) { Stop-Process -Id $server.Id -Force -EA SilentlyContinue }
  Get-Process | ? { $_.Path -eq $Release } | Stop-Process -Force -EA SilentlyContinue
  Set-ItemProperty $key '(default)' $installed
  "LocalServer32 restored: $((Get-ItemProperty $key).'(default)')"
}
