"""Run: python3 -I -m unittest discover -s tests   (from the release folder)"""
import json, math, pathlib, sys, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src" / "python"))
from meaningful_change import rcv, compare, z_score, index_of_individuality, aps_from_bv, desirable_cva_fallback  # noqa: E402

EX = json.loads((ROOT / "tests" / "literature_examples.json").read_text())["examples"]


class LiteratureExamples(unittest.TestCase):
    def test_published_values(self):
        for ex in EX:
            i = ex["inputs"]
            down, up = rcv(i["cvi"], i["cva"], i.get("probability", 0.95), i.get("sided", "two"),
                           i["model"], i.get("z"))
            # Papers print rounded RCVs computed from unrounded CVs, while we can only feed
            # the rounded CVs they printed. Accept a difference up to one unit of the last
            # printed digit (0.1 for one decimal). All but two printed values also match within half a unit.
            tol = 10 ** -ex["decimals"] + 1e-9
            with self.subTest(ex["id"]):
                if "rcv_up" in ex["expected"]:
                    self.assertLessEqual(abs(up - ex["expected"]["rcv_up"]), tol)
                if "rcv_down" in ex["expected"]:
                    self.assertLessEqual(abs(down - ex["expected"]["rcv_down"]), tol)

    def test_at_least_three_publications(self):
        self.assertGreaterEqual(len({e["doi"] for e in EX}), 3)


class Behaviour(unittest.TestCase):
    def test_z(self):
        self.assertAlmostEqual(z_score(0.95, "two"), 1.959964, places=5)
        self.assertAlmostEqual(z_score(0.95, "one"), 1.644854, places=5)
        self.assertAlmostEqual(z_score(0.99, "two"), 2.575829, places=5)
        self.assertAlmostEqual(z_score(0.90, "two"), 1.644854, places=5)

    def test_symmetric_is_symmetric(self):
        d, u = rcv(10, 2, model="symmetric")
        self.assertAlmostEqual(-d, u)

    def test_lognormal_is_asymmetric(self):
        d, u = rcv(20, 3)
        self.assertGreater(u, -d)
        # multiplicative symmetry: (1+up)(1+down) = 1
        self.assertAlmostEqual((1 + u / 100) * (1 + d / 100), 1.0, places=12)

    def test_lognormal_close_to_symmetric_for_small_cv(self):
        d, u = rcv(1.0, 0.5)
        ds, us = rcv(1.0, 0.5, model="symmetric")
        self.assertAlmostEqual(u, us, delta=0.05)

    def test_cva_required(self):
        with self.assertRaises(ValueError):
            rcv(10, None)

    def test_compare(self):
        r = compare(100, 140, cvi=13.0, cva=3.3, sided="one")
        self.assertAlmostEqual(r.percent_change, 40.0)
        self.assertTrue(r.exceeds)
        self.assertEqual(r.direction, "up")
        r = compare(100, 120, cvi=13.0, cva=3.3, sided="one")
        self.assertFalse(r.exceeds)
        self.assertEqual(r.direction, "none")
        r = compare(100, 70, cvi=13.0, cva=3.3, sided="one")
        self.assertTrue(r.exceeds)
        self.assertEqual(r.direction, "down")

    def test_ii(self):
        self.assertAlmostEqual(index_of_individuality(17.9, 36.2), 0.4945, places=4)

    def test_aps(self):
        a = aps_from_bv(17.9, 36.2, "desirable")
        self.assertAlmostEqual(a["imprecision_max"], 8.95)
        self.assertAlmostEqual(round(a["bias_max"], 1), 10.1)   # thyroid meta-analysis Table 2, TSH bias 10.1
        self.assertAlmostEqual(aps_from_bv(10, None, "optimum")["imprecision_max"], 2.5)
        self.assertAlmostEqual(aps_from_bv(10, None, "minimum")["imprecision_max"], 7.5)
        self.assertAlmostEqual(desirable_cva_fallback(10), 5.0)


if __name__ == "__main__":
    unittest.main()
