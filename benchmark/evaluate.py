"""Prepare blinded packets or score completed Omenizator reviews."""
import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def cases():
    catalog = (ROOT / "references/evaluare.md").read_text(encoding="utf-8")
    rows = {}
    for line in catalog.splitlines():
        if line.startswith(("| A", "| L")):
            case, register, before, reference, invariant = (
                cell.strip() for cell in line.strip("|").split("|")
            )
            if case in rows:
                raise ValueError(f"Duplicate case: {case}")
            rows[case] = (register, before, reference, invariant)
    return rows


def read_csv(path):
    try:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            header = stream.readline()
            stream.seek(0)
            for delimiter in (",", ";"):
                fields = next(csv.reader([header], delimiter=delimiter), [])
                if len(fields) > 1 and fields[0] == "id":
                    return list(csv.DictReader(stream, delimiter=delimiter))
    except UnicodeDecodeError as error:
        raise ValueError(f"{path}: save as CSV UTF-8 in Excel and retry") from error
    raise ValueError(f"{path}: expected an id header and comma or semicolon delimiter")


def write_csv(path, headers, rows):
    with path.open("x", encoding="utf-8-sig", newline="") as stream:
        writer = csv.writer(stream)
        writer.writerow(headers)
        writer.writerows(rows)


def prepare(args):
    dataset = cases()
    run = json.loads(args.run.read_text(encoding="utf-8"))
    for field in ("model", "skill", "catalog", "parameters"):
        if field not in run:
            raise ValueError(f"Missing run metadata: {field}")
    candidates = run["candidates"]
    if set(candidates) != set(dataset):
        raise ValueError("Candidate IDs must match all benchmark cases")
    if any(not isinstance(value, str) or not value.strip() for value in candidates.values()):
        raise ValueError("Every candidate must contain a nonempty text")
    args.out.mkdir()
    for reviewer in range(1, 4):
        order = list(dataset)
        rng = random.Random(f"{args.seed}/{reviewer}")
        rng.shuffle(order)
        packet, key = [], []
        for case in order:
            register, before, _, _ = dataset[case]
            texts = [before, candidates[case]]
            candidate_side = "B"
            if rng.randrange(2):
                texts.reverse()
                candidate_side = "A"
            packet.append((case, register, *texts, "", ""))
            key.append((case, candidate_side))
        write_csv(args.out / f"review-{reviewer}.csv",
                  ("id", "register", "A", "B", "naturalness", "register_fit"), packet)
        write_csv(args.out / f"key-{reviewer}.csv", ("id", "candidate"), key)
    write_csv(args.out / "fidelity.csv",
              ("id", "before", "candidate", "invariant", "fidelity", "before_count", "after_count"),
              [(case, before, candidates[case], invariant, "", "", "")
               for case, (_, before, _, invariant) in dataset.items()])
    (args.out / "run.json").write_text(json.dumps(run, ensure_ascii=False, indent=2),
                                      encoding="utf-8")


def indexed(path, dataset):
    rows = read_csv(path)
    indexed_rows = {row["id"]: row for row in rows}
    if set(indexed_rows) != set(dataset) or len(indexed_rows) != len(rows):
        raise ValueError(f"{path}: missing, unknown or duplicate case ID")
    return indexed_rows


def score(args):
    dataset = cases()
    report = defaultdict(Counter)
    fidelity = indexed(args.out / "fidelity.csv", dataset)
    for case, row in fidelity.items():
        register, before, _, _ = dataset[case]
        stats = report[register]
        if row["fidelity"] not in {"pass", "fail"}:
            raise ValueError(f"{case}: fidelity must be pass or fail")
        counts = [int(row[field]) for field in ("before_count", "after_count")]
        if min(counts) < 0:
            raise ValueError(f"{case}: pattern counts must be nonnegative")
        stats["cases"] += 1
        stats["fidelity_pass"] += row["fidelity"] == "pass"
        stats["clean_controls_unchanged"] += case in {"A3", "L3"} and row["candidate"] == before
        if row["fidelity"] == "fail":
            stats["rejected"] += 1
            continue
        stats["before_patterns"] += counts[0]
        stats["after_patterns"] += counts[1]
    for reviewer in range(1, 4):
        packet = indexed(args.out / f"review-{reviewer}.csv", dataset)
        key = indexed(args.out / f"key-{reviewer}.csv", dataset)
        for case, row in packet.items():
            side = key[case]["candidate"]
            if side not in {"A", "B"}:
                raise ValueError(f"{case}: invalid key")
            for criterion in ("naturalness", "register_fit"):
                vote = row[criterion]
                if vote not in {"A", "B", "tie"}:
                    raise ValueError(f"{case}: {criterion} must be A, B or tie")
                outcome = "tie" if vote == "tie" else "candidate" if vote == side else "original"
                if fidelity[case]["fidelity"] == "pass":
                    report[dataset[case][0]][f"{criterion}_{outcome}"] += 1
    result = {}
    for register, stats in report.items():
        before = stats["before_patterns"]
        reduction = (before - stats["after_patterns"]) / before if before else None
        result[register] = dict(stats, rejected=stats["rejected"], pattern_reduction=reduction)
    print(json.dumps(result, ensure_ascii=False, indent=2))


parser = argparse.ArgumentParser(description=__doc__)
commands = parser.add_subparsers(required=True)
prepare_cmd = commands.add_parser("prepare")
prepare_cmd.add_argument("run", type=Path)
prepare_cmd.add_argument("out", type=Path)
prepare_cmd.add_argument("--seed", type=int, required=True)
prepare_cmd.set_defaults(action=prepare)
score_cmd = commands.add_parser("score")
score_cmd.add_argument("out", type=Path)
score_cmd.set_defaults(action=score)
if __name__ == "__main__":
    options = parser.parse_args()
    try:
        options.action(options)
    except ValueError as error:
        parser.exit(2, f"{error}\n")
