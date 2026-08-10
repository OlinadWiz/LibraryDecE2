#!/bin/sh
set -eu

decoder="${1:?decoder required}"
version="${2:?version required}"
revision="${3:?revision required}"
architecture="${4:?architecture required}"
plugin_so="${5:?plugin path required}"
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
Depends: gstreamer1.0 (>= 1.28.5)
Description: GStreamer dashdemux2 adaptive streaming backend for JasonTV ($decoder)
EOF

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
