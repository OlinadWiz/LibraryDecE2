#!/usr/bin/env python3
"""Apply JasonTV's ClearKey compatibility patch to pinned gst-cencdec."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "upstream")
root_meson = root / "meson.build"
source = root_meson.read_text(encoding="utf-8")
old = "openssl_dep = dependency('openssl', version: '>= 1.0.0g', required : true)"
new = "openssl_dep = dependency('openssl', version: '>= 1.0.0g', required : true, static : true)"
if old not in source:
    raise SystemExit("Expected upstream OpenSSL declaration not found")
source = source.replace(old, new).replace("libxml2_dep = dependency('libxml-2.0', required : true)\n", "")
root_meson.write_text(source, encoding="utf-8")

src_meson = root / "src/meson.build"
src_meson.write_text(src_meson.read_text(encoding="utf-8").replace(", libxml2_dep", ""), encoding="utf-8")
c_file = root / "src/gstcencdec.c"
source = c_file.read_text(encoding="utf-8")
source = source.replace("#include <libxml/parser.h>\n", "").replace("#include <libxml/tree.h>\n", "")
source = source.replace("#include <stdio.h>\n", "#include <stdio.h>\n#include <stdarg.h>\n")
source = source.replace(
    "typedef enum\n{",
    'static void jtv_diag (const char *format, ...)\n{\n  FILE *file = fopen ("/tmp/jasontv-cencdec.log", "a");\n  va_list args;\n  if (!file) return;\n  va_start (args, format);\n  vfprintf (file, format, args);\n  va_end (args);\n  fputc (\'\\n\', file);\n  fclose (file);\n}\n\ntypedef enum\n{')
source = source.replace(
    '#define CLEARKEY_PROTECTION_ID "e2719d58-a985-b3c9-781a-b030af78d30e"',
    '#define CLEARKEY_PROTECTION_ID "e2719d58-a985-b3c9-781a-b030af78d30e"\n'
    '#define WIDEVINE_CENC_ID "edef8ba9-79d6-4ace-a3c8-27dcd51d21ed"\n'
    '#define PLAYREADY_CENC_ID "9a04f079-9840-4286-ab92-e65be0885f95"')
source = source.replace(
    '     "application/x-cenc, protection-system=(string)" CLEARKEY_PROTECTION_ID "; "\n'
    '     "application/x-cenc, protection-system=(string)" M_MPD_PROTECTION_ID "; "\n'
    '     "application/x-cenc, protection-system=(string)" M_PSSH_PROTECTION_ID)',
    '     "application/x-cenc, protection-system=(string)" CLEARKEY_PROTECTION_ID)')
source = source.replace(
    "  CLEARKEY_PROTECTION_ID,\n  M_MPD_PROTECTION_ID,\n  M_PSSH_PROTECTION_ID,\n  NULL",
    "  CLEARKEY_PROTECTION_ID,\n  NULL")
source = re.sub(
    r"static gboolean\ngst_cenc_decrypt_parse_content_protection_element .*?\n}\n\nstatic gboolean\ngst_cenc_decrypt_sink_event_handler",
    "static gboolean\ngst_cenc_decrypt_sink_event_handler", source, flags=re.S)
source = source.replace("  GstCencDrmType drm_type;\n};", "  GstCencDrmType drm_type;\n  guint diag_samples;\n};")
source = source.replace("  self->drm_type = GST_DRM_UNKNOWN;\n}",
                        '  self->drm_type = GST_DRM_UNKNOWN;\n  self->diag_samples = 0;\n  jtv_diag ("element_init");\n}')
source = source.replace('    GST_ERROR_OBJECT (self, "Failed to open keyfile: %s", path);',
                        '    GST_ERROR_OBJECT (self, "Failed to open keyfile: %s", path);\n    jtv_diag ("keyfile_open_failed");')
source = source.replace('    GST_ERROR_OBJECT (self, "Failed to read key from file %s", path);',
                        '    GST_ERROR_OBJECT (self, "Failed to read key from file %s", path);\n    jtv_diag ("keyfile_invalid_size");')
source = source.replace("  g_ptr_array_add (self->keys, kp);\n\n  return kp;",
                        '  g_ptr_array_add (self->keys, kp);\n  jtv_diag ("key_loaded");\n\n  return kp;')
source = source.replace('      GST_ERROR_OBJECT (self, "Failed to get GstProtection metadata from buffer");',
                        '      GST_ERROR_OBJECT (self, "Failed to get GstProtection metadata from buffer");\n      jtv_diag ("protection_meta_missing");')
source = source.replace('    GST_ERROR_OBJECT (self, "Failed to init AES cipher");',
                        '    GST_ERROR_OBJECT (self, "Failed to init AES cipher");\n    jtv_diag ("aes_init_failed");')
source = source.replace("out:\n  return ret;",
                        'out:\n  if (self->diag_samples < 3) {\n    jtv_diag (ret == GST_FLOW_OK ? "sample_decrypted" : "sample_failed");\n    self->diag_samples++;\n  }\n  return ret;', 1)
# Accept the protection UUID commonly advertised by ClearKey playlists even
# when their PSSH also names Widevine or PlayReady.
source = source.replace(
    '     "application/x-cenc, protection-system=(string)" CLEARKEY_PROTECTION_ID)',
    '     "application/x-cenc, protection-system=(string)" CLEARKEY_PROTECTION_ID "; "\n'
    '     "application/x-cenc, protection-system=(string)" WIDEVINE_CENC_ID "; "\n'
    '     "application/x-cenc, protection-system=(string)" PLAYREADY_CENC_ID)')
source = source.replace("  CLEARKEY_PROTECTION_ID,\n  NULL",
                        "  CLEARKEY_PROTECTION_ID,\n  WIDEVINE_CENC_ID,\n  PLAYREADY_CENC_ID,\n  NULL")
source = re.sub(
    r'if\(g_ascii_strcasecmp\(loc, "dash/mpd"\)==0.*?gst_cenc_decrypt_parse_pssh_box \(self, pssi\);\n        }',
    'if (system_id && (g_ascii_strcasecmp(system_id, CLEARKEY_PROTECTION_ID) == 0 ||\n'
    '        g_ascii_strcasecmp(system_id, WIDEVINE_CENC_ID) == 0 ||\n'
    '        g_ascii_strcasecmp(system_id, PLAYREADY_CENC_ID) == 0)) {\n'
    '          GST_DEBUG_OBJECT (self, "event carries ClearKey data");\n'
    '          self->drm_type = GST_DRM_CLEARKEY;\n'
    '        }', source, flags=re.S)
if "xmlReadMemory" in source or "gst_cenc_decrypt_parse_content_protection_element" in source:
    raise SystemExit("Failed to remove upstream libxml2/Marlin code")
for marker in ("WIDEVINE_CENC_ID", "PLAYREADY_CENC_ID", "jtv_diag", "key_loaded"):
    if marker not in source:
        raise SystemExit("Failed to apply CENC marker: " + marker)
c_file.write_text(source, encoding="utf-8")
