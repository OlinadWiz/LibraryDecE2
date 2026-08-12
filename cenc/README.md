# JasonTV CENC build

This directory builds the optional native ClearKey/CENC component. Coordinated
ABI profiles are defined in `../native-profiles.json`; see `../native/README.md`.

The GitHub Actions workflow downloads the pinned LGPL `gst-cencdec` source,
cross-compiles it in a matching sysroot and creates a profile-specific IPK.
It implements ISO BMFF `cenc` AES-CTR ClearKey decryption. It is not a Widevine
CDM and must only be used with content and keys the user is authorised to use.

Build output:

`jasontv-cenc-armv7hf-neon-gst128-soup2_1.0.0-r5_cortexa15hf-neon-vfpv4.ipk`

To add a receiver family, add and validate a profile in `native-profiles.json`.

After installation verify on the receiver:

```sh
gst-inspect-1.0 cencdec
```

Keys are intentionally not included in this package or in GitHub artifacts.
