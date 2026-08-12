import json
import os
import unittest


ROOT = os.path.dirname(os.path.dirname(__file__))


class NativeProfileTests(unittest.TestCase):
    def test_ustym_openatv8_profile(self):
        with open(os.path.join(ROOT, "native-profiles.json"), encoding="utf-8") as handle:
            profiles = {item["id"]: item for item in json.load(handle)["profiles"]}
        profile = profiles["armv7hf-neon-gst126-soup2"]
        self.assertTrue(profile["enabled"])
        self.assertEqual(profile["runtime_machine"], "armv7l")
        self.assertEqual(profile["gstreamer_series"], "1.26")
        self.assertEqual(profile["gstreamer_source"], "1.26.10")
        self.assertEqual(profile["soup_major"], 2)
        self.assertEqual(profile["libxml_output"], "true")
        self.assertIn("Ustym 4K PRO / openATV 8", profile["tested_receivers"])

    def test_libxml_output_matches_bundled_wrap_versions(self):
        with open(os.path.join(ROOT, "native-profiles.json"), encoding="utf-8") as handle:
            profiles = {item["gstreamer_series"]: item for item in json.load(handle)["profiles"]}
        self.assertEqual(profiles["1.26"]["libxml_output"], "true")
        self.assertEqual(profiles["1.28"]["libxml_output"], "enabled")
        with open(os.path.join(ROOT, ".github", "workflows", "build-native-profiles.yml"),
                  encoding="utf-8") as handle:
            workflow = handle.read()
        self.assertIn('-Dlibxml2:output="$LIBXML_OUTPUT"', workflow)

    def test_detector_recognizes_gstreamer_126(self):
        with open(os.path.join(ROOT, "native", "detect-profile.sh"), encoding="utf-8") as handle:
            detector = handle.read()
        self.assertIn(
            "armv7l:1.26.*:2) profile=armv7hf-neon-gst126-soup2 ;;",
            detector,
        )


if __name__ == "__main__":
    unittest.main()
