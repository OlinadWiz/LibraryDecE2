#!/usr/bin/env python3
from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "upstream")
path = root / "subprojects/gst-plugins-good/ext/adaptivedemux2/meson.build"
source = path.read_text(encoding="utf-8")
old = "adaptive_xml2_dep = dependency('libxml-2.0', version : '>= 2.8', allow_fallback: true,"
new = "adaptive_xml2_dep = dependency('libxml-2.0', version : '>= 2.8', static: true, allow_fallback: true,"
if old not in source:
    raise SystemExit("Expected adaptivedemux2 libxml2 dependency not found")
path.write_text(source.replace(old, new), encoding="utf-8")
