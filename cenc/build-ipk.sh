#!/bin/sh
set -eu

if [ "$#" -ne 7 ]; then
    echo "usage: $0 PROFILE VERSION REVISION ARCH PLUGIN_SO GST_SERIES RUNTIME_MACHINE" >&2
    exit 2
fi

decoder="$1"
version="$2"
revision="$3"
architecture="$4"
plugin_so="$5"
gst_series="$6"
runtime_machine="$7"
package="jasontv-cenc-${decoder}"
package_version="${version}-${revision}"
output="${package}_${package_version}_${architecture}.ipk"
output_dir="$(pwd)"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT

mkdir -p "$work/control" "$work/data/usr/lib/gstreamer-1.0" \
         "$work/data/usr/share/doc/$package"
install -m 0755 "$plugin_so" "$work/data/usr/lib/gstreamer-1.0/libgstcencdec.so"
install -m 0644 upstream/COPYING "$work/data/usr/share/doc/$package/COPYING"

cat > "$work/control/control" <<EOF
Package: $package
Version: $package_version
Architecture: $architecture
Section: multimedia
Priority: optional
Maintainer: JasonTV contributors
Depends: gstreamer1.0 (>= ${gst_series}.0)
Provides: jasontv-cenc-abi-$decoder
Description: ClearKey CENC GStreamer decryptor for JasonTV ($decoder)
EOF

cat > "$work/control/preinst" <<EOF
#!/bin/sh
set -e
machine="\$(uname -m 2>/dev/null || true)"
[ "\$machine" = "$runtime_machine" ] || { echo "Incompatible CPU: expected $runtime_machine, found \$machine" >&2; exit 1; }
gst="\$(gst-inspect-1.0 --version 2>/dev/null | sed -n 's/^GStreamer[[:space:]]*\([0-9][0-9.]*\).*/\1/p' | head -n1)"
case "\$gst" in $gst_series.*) ;; *) echo "Incompatible GStreamer: expected $gst_series.x, found \${gst:-missing}" >&2; exit 1;; esac
exit 0
EOF
chmod 0755 "$work/control/preinst"

cat > "$work/control/postinst" <<'EOF'
#!/bin/sh
rm -f /root/.cache/gstreamer-1.0/registry.* 2>/dev/null || true
rm -f /home/root/.cache/gstreamer-1.0/registry.* 2>/dev/null || true
exit 0
EOF
chmod 0755 "$work/control/postinst"

(cd "$work/control" && tar --numeric-owner --owner=0 --group=0 -czf "$work/control.tar.gz" .)
(cd "$work/data" && tar --numeric-owner --owner=0 --group=0 -czf "$work/data.tar.gz" .)
printf '2.0\n' > "$work/debian-binary"
(cd "$work" && ar r "$output_dir/$output" debian-binary control.tar.gz data.tar.gz)
echo "$output"
