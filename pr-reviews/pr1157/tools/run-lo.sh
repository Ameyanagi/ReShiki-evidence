#!/bin/bash
# LibreOffice only, a fresh soffice profile per payload.
cd ~/clip2-linux; W=~/dev/ReShiki-clip-text/target-linux/debug/examples/clipboard_worker
export DISPLAY=:87; unset WAYLAND_DISPLAY
Xvfb :87 -screen 0 1600x1000x24 -nolisten tcp >/dev/null 2>&1 & XV=$!; sleep 2
for v in ${@:-copy-control copy-text image-control image-text}; do
  O=out/$v; mkdir -p $O; echo "=== $v"
  $W < $O/request.json > $O/ack.txt 2> $O/worker.err & WP=$!; sleep 3
  U=$(mktemp -d); soffice -env:UserInstallation=file://$U --norestore --nologo --nodefault --accept="socket,host=localhost,port=2087;urp;" >/dev/null 2>&1 & SO=$!; sleep 8
  timeout 120 python3 -u lo_paste.py 2087 > $O/libreoffice.txt 2>&1; grep -v " | " $O/libreoffice.txt
  kill $SO 2>/dev/null; sleep 2; pkill -f "UserInstallation=file://$U"; sleep 1; rm -rf $U
  kill $WP 2>/dev/null; sleep 1
done
kill $XV
