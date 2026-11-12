#!/bin/bash
# usage: run.sh RESHIKI_BIN OUTDIR
# A real desktop Copy (Ctrl+A, Ctrl+C) in the ReShiki GUI on X11 under Xvfb, then pastes into
# LibreOffice Writer/Impress, a Chromium page and text box, and a second ReShiki.
# Every ReShiki run has its own fresh RESHIKI_DATA_DIR.
set -u
BIN=$1; OUT=$2; Q=$HOME/linux-copy-text-qa; mkdir -p "$OUT"
export DISPLAY=:88; unset WAYLAND_DISPLAY
Xvfb :88 -screen 0 1600x1000x24 -nolisten tcp >/dev/null 2>&1 & XV=$!; sleep 2
window() { for _ in $(seq 240); do w=$(xdotool search --onlyvisible --pid "$1" 2>/dev/null | tail -1); [ -n "$w" ] && { echo "$w"; return; }; sleep 0.5; done; }
key() { xdotool windowfocus --sync "$1"; sleep 0.3; xdotool key --clearmodifiers "$2"; }
# A separate XDG_SESSION_ID keeps each app its own process instead of a new tab in the first.
open_app() { # FILE LOG -> sets APP, W
  local d; d=$(mktemp -d); DIRS+=("$d")
  XDG_SESSION_ID=reshiki-qa-$(basename "$d") RESHIKI_DATA_DIR=$d "$BIN" --open "$1" > "$2" 2>&1 & APP=$!; W=$(window $APP); sleep 6; }
DIRS=()
for file in caffeine.rsk reaction.cdxml shapes.rsk; do case=${file%.*}
  O=$OUT/$case; mkdir -p "$O"; cp "$Q/fixtures/$file" "$O/source.${file##*.}"
  open_app "$O/source.${file##*.}" "$O/source-app.log"; SRC=$APP; SW=$W
  key $SW ctrl+a; sleep 1; key $SW ctrl+c; sleep 5
  import -window $SW "$O/source-app.png"
  xclip -selection clipboard -t TARGETS -o > "$O/targets.txt" 2>&1
  for t in 'text/plain;charset=utf-8' text/plain UTF8_STRING; do
    printf '%s: ' "$t"; timeout 5 xclip -selection clipboard -t "$t" -o 2>&1 | head -c 300; echo
  done > "$O/text.txt"
  echo "== $case"; cat "$O/targets.txt" | tr '\n' ' '; echo; cat "$O/text.txt"
  if [ "$case" = caffeine ]; then
    for attempt in 1 2 3 4; do # LibreOffice under Xvfb sometimes crashes whatever the payload
      U=$(mktemp -d); soffice -env:UserInstallation=file://$U --norestore --nologo --nodefault --accept="socket,host=localhost,port=2088;urp;" >/dev/null 2>&1 & SO=$!; sleep 10
      timeout 150 python3 -u "$Q/lo_paste.py" 2088 "$O" > "$O/libreoffice.txt" 2>&1
      kill $SO 2>/dev/null; sleep 2; pkill -f "UserInstallation=file://$U"; sleep 1; rm -rf "$U"
      grep -q "^simpress shapes" "$O/libreoffice.txt" && break
      mv "$O/libreoffice.txt" "$O/libreoffice-failed-attempt$attempt.txt"
    done; cat "$O/libreoffice.txt"
    for page in probe probe-textarea; do C=$(mktemp -d)
      timeout 60 node "$Q/cdp_paste.mjs" /usr/bin/chromium "$Q/$page.html" 9388 "$C" "$O/chromium-$page.png" > "$O/chromium-$page.json" 2>&1; rm -rf "$C"
      python3 -c "import json,sys; d=json.load(open(sys.argv[1])); r=d['result']; print(sys.argv[2], d['browser'], r['types'], 'imgs', len(r['inserted']['imgs']), 'text', repr(r['inserted']['text']))" "$O/chromium-$page.json" "chromium-$page"
    done
    cp "$Q/fixtures/empty.rsk" "$O/target.rsk"
    open_app "$O/target.rsk" "$O/target-app.log"; TGT=$APP; TW=$W
    key $TW ctrl+v; sleep 6; import -window $TW "$O/reshiki-paste.png"
    key $TW ctrl+s; sleep 3
    python3 - "$O/source.rsk" "$O/target.rsk" <<'PY' | tee "$O/reshiki-paste.txt"
import json, sys
s, t = (json.load(open(p)) for p in sys.argv[1:])
def summary(d):
    return {"atoms": len(d.get("atoms", [])), "bonds": len(d.get("bonds", [])), "captions": [a.get("text") for a in d.get("annotations", [])]}
print("source:", summary(s)); print("pasted:", summary(t))
print("pasted the drawing (caption kept):", summary(s) == summary(t))
PY
    kill $TGT 2>/dev/null; wait $TGT 2>/dev/null
  fi
  kill $SRC 2>/dev/null; wait $SRC 2>/dev/null; sleep 1
done
for p in $(pgrep -f -- '--clipboard-worker'); do grep -qz '^DISPLAY=:88$' /proc/$p/environ 2>/dev/null && kill $p; done
kill $XV; rm -rf "${DIRS[@]}"
