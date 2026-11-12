#!/bin/bash
# usage: make-app.sh NAME RESHIKI_BIN FILE  -> a throwaway NAME.app that runs the binary with a fresh
# RESHIKI_DATA_DIR on every launch, opening FILE. Launch only with `open -n NAME.app`.
set -eu
NAME=$1; BIN=$2; FILE=$3; APP=$(dirname "$0")/../apps/$NAME.app
rm -rf "$APP"; mkdir -p "$APP/Contents/MacOS"
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleExecutable</key><string>launch</string>
<key>CFBundleIdentifier</key><string>dev.reshiki.qa.$NAME</string>
<key>CFBundleName</key><string>$NAME</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
cat > "$APP/Contents/MacOS/launch" <<LAUNCH
#!/bin/bash
export RESHIKI_DATA_DIR=\$(mktemp -d /tmp/reshiki-qa-$NAME.XXXXXX)
export RESHIKI_INCHI_HELPER=$BIN RESHIKI_NAMING_HELPER=$BIN
echo "data dir \$RESHIKI_DATA_DIR" > /tmp/reshiki-qa-$NAME.log
exec $BIN --open "$FILE" >> /tmp/reshiki-qa-$NAME.log 2>&1
LAUNCH
chmod +x "$APP/Contents/MacOS/launch"; echo "$APP"
