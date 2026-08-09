# JasonTV CENC build

This directory builds the optional native ClearKey/CENC component independently
from the Python JasonTV plugin. The first supported target is Zgemma H7
(`armv7l`, `cortexa15hf-neon-vfpv4`).

The GitHub Actions workflow downloads the pinned LGPL `gst-cencdec` source,
cross-compiles it in a Debian ARMHF sysroot and creates a decoder-specific IPK.
It implements ISO BMFF `cenc` AES-CTR ClearKey decryption. It is not a Widevine
CDM and must only be used with content and keys the user is authorised to use.

Build output:

`jasontv-cenc-zgemmah7_1.0.0-r0_cortexa15hf-neon-vfpv4.ipk`

To add a receiver, extend the matrix in
`.github/workflows/build-cenc-ipk.yml`. A target with another CPU ABI needs its
matching cross compiler and sysroot, not just a renamed package.

After installation verify on the receiver:

```sh
gst-inspect-1.0 cencdec
```

Keys are intentionally not included in this package or in GitHub artifacts.

