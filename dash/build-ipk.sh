#!/bin/sh
set -eu

decoder="${1:?decoder required}"
version="${2:?version required}"
revision="${3:?revision required}"
architecture="${4:?architecture required}"
plugin_so="${5:?plugin path required}"
gst_series="${6:?GStreamer series required}"
runtime_machine="${7:?runtime machine required}"
package="jasontv-dash-$decoder"
package_version="$version-$revision"
output="${package}_${package_version}_${architecture}.ipk"
output_dir="$(pwd)"

test -f "$plugin_so"
work="$(mktemp -d)"
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/control" "$work/data/usr/lib/gstreamer-1.0" \
         "$work/data/usr/share/doc/$package"
install -m 0755 "$plugin_so" "$work/data/usr/lib/gstreamer-1.0/libgstadaptivedemux2.so"

cat > "$work/control/control" <<EOF
Package: $package
Version: $package_version
Architecture: $architecture
Section: multimedia
Priority: optional
Maintainer: JasonTV contributors
Depends: gstreamer1.0 (>= ${gst_series}.0)
Provides: jasontv-dash-abi-$decoder
Description: GStreamer dashdemux2 adaptive streaming backend for JasonTV ($decoder)
EOF

cat > "$work/control/preinst" <<EOF
#!/bin/sh
set -e
machine="\$(uname -m 2>/dev/null || true)"
[ "\$machine" = "$runtime_machine" ] || { echo "Incompatible CPU: expected $runtime_machine, found \$machine" >&2; exit 1; }
gst="\$(gst-inspect-1.0 --version 2>/dev/null | sed -n 's/^GStreamer[[:space:]]*\([0-9][0-9.]*\).*/\1/p' | head -n1)"
case "\$gst" in $gst_series.*) ;; *) echo "Incompatible GStreamer: expected $gst_series.x, found \${gst:-missing}" >&2; exit 1;; esac
find /usr/lib /lib -name 'libsoup-2.4.so*' -print -quit 2>/dev/null | grep -q . || { echo "Incompatible runtime: libsoup 2.4 missing" >&2; exit 1; }
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

cat > "$work/control/prerm" <<'EOF'
#!/bin/sh
rm -f /root/.cache/gstreamer-1.0/registry.* 2>/dev/null || true
rm -f /home/root/.cache/gstreamer-1.0/registry.* 2>/dev/null || true
exit 0
EOF
chmod 0755 "$work/control/prerm"

(cd "$work/control" && tar --numeric-owner --owner=0 --group=0 -czf "$work/control.tar.gz" .)
(cd "$work/data" && tar --numeric-owner --owner=0 --group=0 -czf "$work/data.tar.gz" .)
printf '2.0\n' > "$work/debian-binary"
(cd "$work" && ar r "$output_dir/$output" debian-binary control.tar.gz data.tar.gz)
echo "$output"
