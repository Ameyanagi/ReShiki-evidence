#!/bin/bash
# usage: wayland.sh WORKTREE OUT COMPOSITOR — runs the repo's Wayland clipboard QA in the CI image.
set -eu
W=$1; OUT=$2; C=$3
docker run --rm -v "$W":/src -v reshiki-wayland-qa-target:/target -v reshiki-wayland-qa-rustup:/usr/local/rustup \
  -e CARGO_TARGET_DIR=/target -e CARGO_PROFILE_DEV_DEBUG=0 -e CARGO_INCREMENTAL=0 -e RESHIKI_QA_SOURCE_HEAD=local -w /src \
  ghcr.io/ameyanagi/reshiki-ci-noble-desktop:main bash -ec "
    rustup toolchain install 1.99.1 --profile minimal >/dev/null 2>&1; rustup default 1.99.1 >/dev/null
    cargo build --locked --no-default-features --features wayland-qa --bin reshiki 2>&1 | tail -1
    rm -rf /run/systemd/seats; dbus-daemon --system --fork
    rm -rf /tmp/qa; bash scripts/wayland_clipboard_qa.sh $C /target/debug/reshiki /tmp/qa/$C; echo QA_PASSED
    mkdir -p /src/$OUT; cp -r /tmp/qa/$C /src/$OUT/; chown -R $(id -u):$(id -g) /src/$OUT"
