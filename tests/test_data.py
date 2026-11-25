"""Checks on the built data files. Run after scripts/build.sh."""
import csv, json, pathlib, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
MARKERS = ROOT.parent / "_raw" / "lifefrom-release-1" / "markers.csv"
KEYS = ["slug", "marker_slug", "name", "specimen", "cvi", "cvi_ci", "cvg", "cva_study",
        "n_subjects", "population", "doi", "source_label", "location"]


class WebJson(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.web = json.loads((ROOT / "web" / "meaningful-change.json").read_text())
        cls.verified = {r["doi"] for r in csv.DictReader((ROOT / "data" / "doi_verification.csv").read_text().splitlines())}

    def test_top_level(self):
        self.assertEqual(set(self.web) - {"generated"}, {"version", "analytes", "formulas"})

    def test_analyte_keys_and_values(self):
        slugs = set()
        for a in self.web["analytes"]:
            self.assertEqual(list(a), KEYS)
            self.assertNotIn(a["slug"], slugs); slugs.add(a["slug"])
            self.assertGreater(a["cvi"], 0)
            if a["cvi_ci"]:
                lo, hi = a["cvi_ci"]
                self.assertLessEqual(lo, a["cvi"]); self.assertGreaterEqual(hi, a["cvi"])
            self.assertIn(a["doi"], self.verified, a["slug"])

    def test_marker_slugs_exist(self):
        if not MARKERS.exists():
            self.skipTest("markers.csv not present")
        known = {r["marker_slug"] for r in csv.DictReader(MARKERS.read_text().splitlines())}
        for a in self.web["analytes"]:
            if a["marker_slug"]:
                self.assertIn(a["marker_slug"], known)


class Estimates(unittest.TestCase):
    def test_every_row_full_text_and_dated(self):
        for r in csv.DictReader((ROOT / "data" / "bv_estimates.csv").read_text().splitlines()):
            self.assertEqual(r["full_text_read"], "yes")
            self.assertEqual(r["access_date"], "2026-11-25")
            self.assertTrue(r["evidence"].strip())

    def test_one_primary_per_analyte(self):
        seen = {}
        for r in csv.DictReader((ROOT / "data" / "bv_estimates.csv").read_text().splitlines()):
            if r["primary"] == "yes":
                k = r["marker_slug"] or r["analyte"]
                self.assertNotIn(k, seen); seen[k] = r["row_id"]
        self.assertGreaterEqual(len(seen), 60)


if __name__ == "__main__":
    unittest.main()
