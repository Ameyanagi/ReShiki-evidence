#!/bin/sh
# Before (main, df1f03d40): the folders through check -> download -> install ->
# relaunch, with main's own src/updates/install.sh as the helper.
# usage: before-main.sh <path to main's install.sh>
# Rust's part on main is reproduced by hand, as src/updates.rs and
# src/updates/install.rs do it there: the check file is
# <data>/update-cache.json, and prepare() makes a `.reshiki-update-XXXXXX`
# temp folder beside the app and downloads, verifies and unpacks in it.
set -eu
helper=$1
root=$(mktemp -d)
data=$root/data apps=$root/Applications
show() { echo; echo "## $1"; (cd "$root" && find data Applications | sort); }
mkdir -p "$data" "$apps/ReShiki"
printf '#!/bin/sh\n# old\nexit 0\n' > "$apps/ReShiki/reshiki"; chmod +x "$apps/ReShiki/reshiki"
echo '{}' > "$apps/ReShiki/build.json"
echo true > "$data/update-preferences.json"
show "before"
echo '{"checked_at":100,"result":{"Ok":{"version":"9.9.9"}}}' > "$data/update-cache.json"
show "after launch and a check"
stage=$apps/.reshiki-update-Ab12Cd
payload=$stage/extracted/reshiki-9.9.9-linux-arm64
mkdir -p "$payload"
echo sums > "$stage/SHA256SUMS"; echo archive > "$stage/reshiki-9.9.9-linux-arm64.tar.gz"
printf '#!/bin/sh\n# new\nexit 0\n' > "$payload/reshiki"; chmod +x "$payload/reshiki"
echo '{}' > "$payload/build.json"
show "after the download"
cp "$helper" "$stage/install.sh"
/bin/sh "$stage/install.sh" 2147483647 "$apps/ReShiki" "$payload" "$stage" "" linux > "$stage/install.log" 2>&1
show "after the helper (installed: $(sed -n 2p "$apps/ReShiki/reshiki"))"
# main does nothing about update files at launch.
show "after the next launch"
rm -rf "$root"
