#!/bin/bash
# usage: linux-run.sh RESHIKI_BIN OUTDIR
# Real desktop Copy (Ctrl+A, Ctrl+C) and Copy Image (Ctrl+Shift+C) in the ReShiki GUI on X11 under
# Xvfb; saves each clipboard image/svg+xml, pastes it into a Chromium page that draws that flavor,
# then publishes the SVG flavor alone and pastes it into a second ReShiki (Ctrl+V, Ctrl+S).
# Every ReShiki run has its own fresh RESHIKI_DATA_DIR.
set -u
BIN=$1; OUT=$2; Q=$HOME/clipsvg-qa; T=$(cd "$(dirname "$0")" && pwd); mkdir -p "$OUT"
export DISPLAY=:89; unset WAYLAND_DISPLAY
Xvfb :89 -screen 0 1600x1000x24 -nolisten tcp >/dev/null 2>&1 & XV=$!; sleep 2
window() { for _ in $(seq 240); do w=$(xdotool search --onlyvisible --pid "$1" 2>/dev/null | tail -1); [ -n "$w" ] && { echo "$w"; return; }; sleep 0.5; done; }
key() { xdotool windowfocus --sync "$1"; sleep 0.3; xdotool key --clearmodifiers "$2"; }
open_app() { # FILE LOG -> sets APP, W
  local d; d=$(mktemp -d); DIRS+=("$d")
  XDG_SESSION_ID=reshiki-qa-$(basename "$d") RESHIKI_DATA_DIR=$d "$BIN" --open "$1" > "$2" 2>&1 & APP=$!; W=$(window $APP); sleep 6; }
DIRS=()
cp "$Q/fixtures/caffeine.rsk" "$OUT/source.rsk"
open_app "$OUT/source.rsk" "$OUT/source-app.log"; SRC=$APP; SW=$W
key $SW ctrl+a; sleep 1
for cmd in copy copy-image; do
  O=$OUT/$cmd; mkdir -p "$O"
  if [ $cmd = copy ]; then key $SW ctrl+c; else key $SW ctrl+shift+c; fi; sleep 5
  import -window $SW "$O/source-app.png"
  xclip -selection clipboard -t TARGETS -o > "$O/targets.txt" 2>&1
  timeout 10 xclip -selection clipboard -t image/svg+xml -o > "$O/clipboard.svg"
  python3 - "$O/clipboard.svg" <<'PY' | tee "$O/svg-summary.txt"
import sys, xml.etree.ElementTree as ET
data = open(sys.argv[1], 'rb').read(); root = ET.fromstring(data)
tag = lambda n: sum(1 for e in root.iter() if e.tag.rsplit('}', 1)[-1] == n)
print(f"bytes {len(data)} text_elements {tag('text')} path_elements {tag('path')} width {root.get('width')} height {root.get('height')} viewBox {root.get('viewBox')} carries_drawing {b'reshiki' in data[:4000].lower()}")
PY
  C=$(mktemp -d); timeout 60 node "$T/cdp_paste.mjs" /usr/bin/chromium "$T/probe-svg.html" 9389 "$C" "$O/chromium-svg.png" > "$O/chromium-svg.json" 2>&1; rm -rf "$C"
  python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print('chromium', d['browser'], json.dumps(d['result'].get('svg') if isinstance(d['result'], dict) else d['result']))" "$O/chromium-svg.json" | tee -a "$O/svg-summary.txt"
done
kill $SRC 2>/dev/null; wait $SRC 2>/dev/null; sleep 1
# The SVG flavor alone, then Paste in a second ReShiki: does the editable drawing come back?
O=$OUT/svg-only-paste; mkdir -p "$O"
xclip -selection clipboard -t image/svg+xml -i "$OUT/copy-image/clipboard.svg"; sleep 1
xclip -selection clipboard -t TARGETS -o > "$O/targets.txt" 2>&1
cp "$Q/fixtures/empty.rsk" "$O/target.rsk"
open_app "$O/target.rsk" "$O/target-app.log"; TGT=$APP; TW=$W
key $TW ctrl+v; sleep 6; import -window $TW "$O/reshiki-paste.png"
key $TW ctrl+s; sleep 3
python3 - "$OUT/source.rsk" "$O/target.rsk" <<'PY' | tee "$O/reshiki-paste.txt"
import json, sys
s, t = (json.load(open(p)) for p in sys.argv[1:])
summary = lambda d: {"atoms": len(d.get("atoms", [])), "bonds": len(d.get("bonds", [])), "captions": [a.get("text") for a in d.get("annotations", [])]}
print("source:", summary(s)); print("pasted:", summary(t)); print("editable drawing restored from the SVG alone:", summary(s) == summary(t))
PY
kill $TGT 2>/dev/null; wait $TGT 2>/dev/null
pkill -f "xclip -selection clipboard -t image/svg+xml -i" 2>/dev/null
for p in $(pgrep -f -- '--clipboard-worker'); do grep -qz '^DISPLAY=:89$' /proc/$p/environ 2>/dev/null && kill $p; done
kill $XV; rm -rf "${DIRS[@]}"
