#!/bin/bash
# usage: run.sh  (from ~/clip2-linux). Publishes each payload through ReShiki's X11 clipboard worker, then pastes.
cd ~/clip2-linux; W=~/dev/ReShiki-clip-text/target-linux/debug/examples/clipboard_worker
export DISPLAY=:87; unset WAYLAND_DISPLAY
Xvfb :87 -screen 0 1600x1000x24 -nolisten tcp >/dev/null 2>&1 & XV=$!; sleep 2
U=$(mktemp -d); soffice -env:UserInstallation=file://$U --norestore --nologo --nodefault --accept="socket,host=localhost,port=2087;urp;" >/dev/null 2>&1 & SO=$!
for v in copy-control copy-text image-control image-text; do
  O=out/$v; mkdir -p $O; echo "=== $v"
  python3 - "$v" > $O/request.json <<'PY'
import base64, json, os, sys
p = sys.argv[1]
order = [l.strip() for l in open(os.path.join(p, "ORDER"))]
print(json.dumps({"operation": "write", "representations": [{"type": k, "data": base64.b64encode(open(os.path.join(p, k), "rb").read()).decode()} for k in order]}))
PY
  $W < $O/request.json > $O/ack.txt 2> $O/worker.err & WP=$!; sleep 3
  echo "TARGETS: $(xclip -selection clipboard -t TARGETS -o | tr '\n' ' ')" | tee $O/targets.txt
  timeout 90 python3 -u lo_paste.py 2087 2>&1 | tee $O/libreoffice.txt
  for page in probe probe-textarea; do C=$(mktemp -d); timeout 60 node cdp_paste.mjs /usr/bin/chromium $PWD/$page.html 9387 $C $O/$page.png > $O/$page.json 2>&1; rm -rf $C
    python3 -c "import json,sys; r=json.load(open(sys.argv[1]))['result']; print(sys.argv[2], r['types'], 'text=',r['text'], 'inserted imgs', len(r['inserted']['imgs']), 'text', repr(r['inserted']['text']))" $O/$page.json chromium-$page; done
  kill $WP 2>/dev/null; sleep 1
done
kill $SO; sleep 2; pkill -f "UserInstallation=file://$U"; kill $XV; rm -rf $U
