param([string]$Harness)
$ErrorActionPreference = 'Continue'; $ProgressPreference = 'SilentlyContinue'
. F:\clip-run\clipfmt.ps1; . F:\clip-run\republish.ps1; . F:\clip-run\office.ps1
$Release = 'F:\clip-bin\reshiki-clip-11df00d5.exe'
$key = 'HKCU:\Software\Classes\CLSID\{3BAC2B7E-73A2-4F3A-9CE7-5E9B438C59B4}\LocalServer32'
$installed = '"%LOCALAPPDATA%\Programs\ReShiki\reshiki.exe" --ole-server'
"LocalServer32 before: $((Get-ItemProperty $key).'(default)')"
$env:CLIP_RSK = 'F:\clip-run\caffeine.rsk'
$server = $null
function Server {
  # Our isolated OLE server, so Office never starts an unisolated ReShiki.
  if ($script:server -and -not $script:server.HasExited) { return }
  Set-ItemProperty $key '(default)' '"F:\clip-run\no-such-server.exe" --ole-server'
  $env:RESHIKI_DATA_DIR = (New-Item -ItemType Directory -Force "F:\clip-run\data\srv-$(Get-Random)").FullName
  $script:server = Start-Process $Release -ArgumentList '--ole-server' -PassThru; Start-Sleep 3
}
function Copy-With($imageOnly, $tag) {
  $env:RESHIKI_DATA_DIR = (New-Item -ItemType Directory -Force "F:\clip-run\data\copy-$(Get-Random)").FullName
  $env:CLIP_IMAGE_ONLY = $imageOnly
  $o = & $Harness clip_harness --ignored --exact --nocapture 2>&1 | Select-String 'image_only=|test result|panicked'
  "harness: $($o -join ' | ')"
  "--- formats after $tag (enumeration order: index, id, name, bytes, head)"
  Dump-Clipboard "F:\clip-run\out\$tag"
}
function Targets($tag) { Server; Word-Paste; Server; PowerPoint-Paste; Server; Excel-Paste; Edge-Paste $tag }
try {
  "=== 1. Copy (Ctrl+C path: clipboard::copy image_only=false)"
  Copy-With '0' 'copy'; $copy = [RP]::Snapshot(); Targets 'copy'
  "=== 2. Copy Image (Ctrl+Shift+C path: image_only=true)"
  Copy-With '1' 'image'; $image = [RP]::Snapshot(); Targets 'image'
  $png = ($image | ? Name -eq 'PNG' | Select -First 1).Data
  $dib = ($image | ? Id -eq 8 | Select -First 1).Data
  $b64 = [Convert]::ToBase64String($png)
  $html = CfHtml ('<img src="data:image/png;base64,' + $b64 + '" alt="Chemical drawing">')
  "=== 3. Experiments: the Copy formats re-published, plus one extra format"
  foreach ($case in @(@{n='control (Copy formats only)'; names=@(); data=@()},
                      @{n='+ HTML Format (img data URI)'; names=@('HTML Format'); data=@(,$html)},
                      @{n='+ CF_DIB'; names=@('CF_DIB'); data=@(,$dib)},
                      @{n='+ PNG'; names=@('PNG'); data=@(,$png)})) {
    "--- $($case.n)"
    "published: $([RP]::Publish($copy, [string[]]$case.names, [byte[][]]$case.data))"
    Targets ($case.n -replace '[^a-zA-Z]', '')
  }
} catch { "ERROR: $_" }
finally {
  if ($server) { Stop-Process -Id $server.Id -Force -EA SilentlyContinue }
  Get-CimInstance Win32_Process -Filter "Name='reshiki-clip-11df00d5.exe'" | % { Stop-Process -Id $_.ProcessId -Force -EA SilentlyContinue }
  Set-ItemProperty $key '(default)' $installed
  "LocalServer32 restored: $((Get-ItemProperty $key).'(default)')"
}
