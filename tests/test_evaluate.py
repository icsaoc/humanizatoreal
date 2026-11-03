import csv
import json
import runpy
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "benchmark/evaluate.py"
CASES = runpy.run_path(str(SCRIPT))["cases"]()
CONTROLS = {case for case, row in CASES.items() if row[3] == "Control curat"}
VOTED = set(CASES) - CONTROLS


class BenchmarkTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        root = Path(temp.name)
        self.out = root / "review"
        run = self.run_file = root / "run.json"
        run.write_text(json.dumps({
            "model": "fixture", "skill": "test", "catalog": "test", "parameters": {},
            "candidates": {key: case[2] for key, case in CASES.items()},
        }), encoding="utf-8")
        self.invoke("prepare", run, self.out, "--seed", 104).check_returncode()

    def invoke(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True, encoding="utf-8",
                              errors="replace")

    def complete(self, fidelity="pass", delimiter=","):
        for path in self.out.glob("*.csv"):
            with path.open(encoding="utf-8-sig", newline="") as stream:
                reader = csv.DictReader(stream)
                fields, rows = reader.fieldnames, list(reader)
            for row in rows:
                if "fidelity" in row:
                    row.update(fidelity=fidelity, before_count="1", after_count="0")
                elif "naturalness" in row:
                    row.update(naturalness="A", register_fit="B")
            with path.open("w", encoding="utf-8-sig", newline="") as stream:
                writer = csv.DictWriter(stream, fields, delimiter=delimiter)
                writer.writeheader()
                writer.writerows(rows)

    def score(self):
        result = self.invoke("score", self.out)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def rows(self, name):
        with (self.out / name).open(encoding="utf-8-sig", newline="") as stream:
            return list(csv.DictReader(stream))

    def sides(self):
        """Count, per register, how many keys place the candidate on side A."""
        total = {"Administrativ": 0, "Literar": 0}
        for reviewer in range(1, 4):
            for row in self.rows(f"key-{reviewer}.csv"):
                total[CASES[row["id"]][0]] += row["candidate"] == "A"
        return total

    def test_prepare_score_and_bom(self):
        for path in self.out.glob("*.csv"):
            self.assertTrue(path.read_bytes().startswith(bytes.fromhex("EFBBBF")))
        on_a = self.sides()
        for reviewer in range(1, 4):
            with (self.out / f"key-{reviewer}.csv").open(encoding="utf-8-sig") as stream:
                key = {row["id"]: row["candidate"] for row in csv.DictReader(stream)}
            with (self.out / f"review-{reviewer}.csv").open(encoding="utf-8-sig") as stream:
                for row in csv.DictReader(stream):
                    case = row["id"]
                    side = key[case]
                    self.assertIn(side, ("A", "B"))
                    self.assertEqual(row[side], CASES[case][2])
                    self.assertEqual(row["B" if side == "A" else "A"], CASES[case][1])
        self.complete()
        for register, stats in self.score().items():
            a, b = on_a[register], 6 - on_a[register]
            self.assertEqual(stats.get("naturalness_candidate", 0), a)
            self.assertEqual(stats.get("naturalness_original", 0), b)
            self.assertEqual(stats.get("register_fit_candidate", 0), b)
            self.assertEqual(stats.get("register_fit_original", 0), a)
            self.assertEqual(stats["clean_controls"], 1)
            self.assertEqual(stats["clean_controls_unchanged"], 1)
            self.assertEqual(stats["cases"], 3)
            self.assertEqual(stats["fidelity_pass"], 3)
            self.assertEqual(stats["rejected"], 0)
            self.assertEqual(stats["pattern_reduction"], 1)

    def test_controls_excluded_from_votes(self):
        for reviewer in range(1, 4):
            self.assertEqual({row["id"] for row in self.rows(f"review-{reviewer}.csv")}, VOTED)
            self.assertEqual({row["id"] for row in self.rows(f"key-{reviewer}.csv")}, VOTED)
        self.assertEqual({row["id"] for row in self.rows("fidelity.csv")}, set(CASES))

    def test_fidelity_sheet_content(self):
        for row in self.rows("fidelity.csv"):
            register, before, candidate, invariant = CASES[row["id"]]
            self.assertEqual(row["before"], before)
            self.assertEqual(row["candidate"], candidate)
            self.assertEqual(row["invariant"], invariant)

    def test_fidelity_pass_counts_only_passes(self):
        self.complete()
        self.rewrite_csv("fidelity.csv", lambda rows: next(
            row for row in rows if row["id"] == "A1").update(fidelity="fail"))
        stats = self.score()["Administrativ"]
        self.assertEqual((stats["cases"], stats["fidelity_pass"], stats["rejected"]), (3, 2, 1))

    def test_invalid_fidelity_value(self):
        self.complete()
        self.rewrite_csv("fidelity.csv", lambda rows: rows[0].update(fidelity="maybe"))
        self.assert_score_error("fidelity must be pass or fail")

    def test_changed_control_not_counted(self):
        self.complete()
        self.rewrite_csv("fidelity.csv", lambda rows: next(
            row for row in rows if row["id"] in CONTROLS
            and CASES[row["id"]][0] == "Administrativ").update(candidate="Alt text."))
        stats = self.score()["Administrativ"]
        self.assertEqual((stats["clean_controls"], stats["clean_controls_unchanged"]), (1, 0))

    def test_missing_key_row(self):
        self.complete()
        self.rewrite_csv("key-1.csv", lambda rows: rows.pop())
        self.assert_score_error("missing, unknown or duplicate case ID")

    def test_semicolon(self):
        self.complete(delimiter=";")
        self.assertEqual(len(self.score()), 2)

    def test_incomplete(self):
        result = self.invoke("score", self.out)
        self.assertEqual(result.returncode, 2)
        self.assertIn("fidelity must be pass or fail", result.stderr)

    def test_cp1250(self):
        path = self.out / "fidelity.csv"
        path.write_bytes("id;register\r\nA1;ț\r\n".replace("ț", "ţ").encode("cp1250"))
        result = self.invoke("score", self.out)
        self.assertEqual(result.returncode, 2)
        self.assertIn("save as CSV UTF-8 in Excel", result.stderr)

    def test_rejected_excluded(self):
        self.complete(fidelity="fail")
        for stats in self.score().values():
            self.assertEqual(stats["rejected"], 3)
            self.assertIsNone(stats["pattern_reduction"])
            self.assertFalse(any(key.startswith(("naturalness_", "register_fit_"))
                                 for key in stats))

    def rewrite_csv(self, name, transform):
        path = self.out / name
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            fields, rows = reader.fieldnames, list(reader)
        transform(rows)
        with path.open("w", encoding="utf-8-sig", newline="") as stream:
            writer = csv.DictWriter(stream, fields)
            writer.writeheader()
            writer.writerows(rows)

    def test_tie(self):
        self.complete()
        def tie(rows):
            next(row for row in rows if row["id"] == "A1").update(
                naturalness="tie", register_fit="tie")

        side = next(row["candidate"] for row in self.rows("key-1.csv") if row["id"] == "A1")
        a = self.sides()["Administrativ"]
        natural = (a - (side == "A"), 6 - a - (side == "B"))
        fit = (6 - a - (side == "B"), a - (side == "A"))
        self.rewrite_csv("review-1.csv", tie)
        stats = self.score()["Administrativ"]
        self.assertEqual(tuple(stats.get(f"naturalness_{k}", 0) for k in
                               ("tie", "candidate", "original")), (1, *natural))
        self.assertEqual(tuple(stats.get(f"register_fit_{k}", 0) for k in
                               ("tie", "candidate", "original")), (1, *fit))

    def assert_score_error(self, message):
        result = self.invoke("score", self.out)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(message, result.stderr)

    def test_invalid_vote(self):
        self.complete()
        self.rewrite_csv("review-1.csv", lambda rows: rows[0].update(naturalness="C"))
        self.assert_score_error("naturalness must be A, B or tie")

    def test_negative_counts(self):
        self.complete()
        self.rewrite_csv("fidelity.csv", lambda rows: rows[0].update(after_count="-1"))
        self.assert_score_error("pattern counts must be nonnegative")

    def test_duplicate_ids(self):
        self.complete()
        self.rewrite_csv("review-1.csv", lambda rows: rows.append(rows[0]))
        self.assert_score_error("missing, unknown or duplicate case ID")

    def test_bad_csv_header(self):
        self.complete()
        (self.out / "review-1.csv").write_text("wrong,header", encoding="utf-8")
        self.assert_score_error("expected an id header")

    def test_invalid_key(self):
        self.complete()
        self.rewrite_csv("key-1.csv", lambda rows: rows[0].update(candidate="C"))
        self.assert_score_error("invalid key")

    def assert_prepare_error(self, transform, message):
        run = json.loads(self.run_file.read_text(encoding="utf-8"))
        transform(run)
        self.run_file.write_text(json.dumps(run), encoding="utf-8")
        out = self.out.with_name("invalid")
        result = self.invoke("prepare", self.run_file, out, "--seed", 104)
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn(message, result.stderr)
        self.assertFalse(out.exists())

    def test_wrong_candidate_ids(self):
        self.assert_prepare_error(lambda run: run["candidates"].update(X1="wrong"),
                                  "Candidate IDs must match all benchmark cases")

    def test_empty_candidate(self):
        self.assert_prepare_error(lambda run: run["candidates"].update(A1="   "),
                                  "Every candidate must contain a nonempty text")

    def test_missing_metadata(self):
        self.assert_prepare_error(lambda run: run.pop("model"), "Missing run metadata: model")

    def test_duplicate_catalog_case(self):
        script = self.out.parent / "benchmark" / SCRIPT.name
        script.parent.mkdir()
        script.write_bytes(SCRIPT.read_bytes())
        catalog = script.parents[1] / "references/evaluare.md"
        catalog.parent.mkdir()
        original = (SCRIPT.parents[1] / "references/evaluare.md").read_text(encoding="utf-8")
        case = next(line for line in original.splitlines() if line.startswith("| A1"))
        catalog.write_text(original + "\n" + case + "\n", encoding="utf-8")
        result = subprocess.run([sys.executable, str(script), "score", str(self.out)],
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertIn("Duplicate case: A1", result.stderr)
