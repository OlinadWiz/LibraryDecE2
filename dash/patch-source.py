#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "upstream")
gst_series = sys.argv[2] if len(sys.argv) > 2 else ""
path = root / "subprojects/gst-plugins-good/ext/adaptivedemux2/meson.build"
source = path.read_text(encoding="utf-8")
old = "adaptive_xml2_dep = dependency('libxml-2.0', version : '>= 2.8', allow_fallback: true,"
new = "adaptive_xml2_dep = dependency('libxml-2.0', version : '>= 2.8', static: true, allow_fallback: true,"
if old not in source:
    raise SystemExit("Expected adaptivedemux2 libxml2 dependency not found")
path.write_text(source.replace(old, new), encoding="utf-8")

if gst_series == "1.22":
    libxml_meson = root / "subprojects/libxml2-2.10.3/meson.build"
    libxml_source = libxml_meson.read_text(encoding="utf-8")
    replacements = {
        "cdata.set('SEND_ARG2_CAST', '')":
            "cdata.set('SEND_ARG2_CAST', '(const void *)')",
        "cdata.set('GETHOSTBYNAME_ARG_CAST', '')":
            "cdata.set('GETHOSTBYNAME_ARG_CAST', '(const char *)')",
    }
    for original, replacement in replacements.items():
        if original not in libxml_source:
            raise SystemExit(f"Expected libxml2 2.10.3 setting not found: {original}")
        libxml_source = libxml_source.replace(original, replacement)
    libxml_meson.write_text(libxml_source, encoding="utf-8")
