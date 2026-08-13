# JasonTV native ABI profiles

`native-profiles.json` is the source of truth for coordinated DASH and CENC
builds. Each manual GitHub Actions run accepts one profile ID and builds only
the corresponding pair of IPKs.

From the GitHub Actions page, select **Run workflow** and choose the receiver
profile from the drop-down menu. The same build can be started from the CLI:

```sh
gh workflow run build-native-profiles.yml -f profile=armv7hf-neon-gst128-soup2
gh workflow run build-native-profiles.yml -f profile=armv7hf-neon-gst126-soup2
```

Wait for or inspect the requested run with `gh run watch`. When adding a new
profile to `native-profiles.json`, also add its `id` to the workflow input
options. Existing profiles are not rebuilt.

Supported ARM hard-float profiles include `armv7hf-neon-gst128-soup2`, tested
on Zgemma H7 with openATV 8 and GStreamer 1.28.x, and
`armv7hf-neon-gst126-soup2`, tested on Ustym 4K PRO with openATV 8 and
GStreamer 1.26.10. A profile describes an ABI family, not a receiver model.
Never enable a new profile by changing only its name or IPK
architecture: provide the matching cross compiler, sysroot, Meson cross files,
GStreamer source series and libsoup major version.

On a receiver, copy and run:

```sh
chmod +x detect-profile.sh
./detect-profile.sh
```

Install only artifacts whose profile equals the detected profile. Each IPK
also contains a `preinst` guard that rejects an incompatible CPU or GStreamer
series. Install DASH first, then CENC, restart Enigma2, and verify:

```sh
opkg install jasontv-dash-*.ipk
opkg install jasontv-cenc-*.ipk
rm -f /root/.cache/gstreamer-1.0/registry.*
gst-inspect-1.0 dashdemux2
gst-inspect-1.0 cencdec
```

Keys and channel credentials are never included in these packages.
