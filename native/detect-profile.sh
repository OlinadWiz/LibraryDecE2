#!/bin/sh
set -eu

machine="$(uname -m 2>/dev/null || echo unknown)"
gst="$(gst-inspect-1.0 --version 2>/dev/null | sed -n 's/^GStreamer[[:space:]]*\([0-9][0-9.]*\).*/\1/p' | head -n1)"
soup=unknown
if find /usr/lib /lib -name 'libsoup-2.4.so*' -print -quit 2>/dev/null | grep -q .; then
    soup=2
elif find /usr/lib /lib -name 'libsoup-3.0.so*' -print -quit 2>/dev/null | grep -q .; then
    soup=3
fi

case "$machine:$gst:$soup" in
    armv7l:1.26.*:2) profile=armv7hf-neon-gst126-soup2 ;;
    armv7l:1.28.*:2) profile=armv7hf-neon-gst128-soup2 ;;
    *) profile=unsupported ;;
esac

echo "machine=$machine"
echo "gstreamer=${gst:-unknown}"
echo "soup=$soup"
echo "profile=$profile"
[ "$profile" != unsupported ]
