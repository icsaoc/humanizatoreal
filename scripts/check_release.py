"""Check that release metadata and documented behavior agree with the repo data."""
import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETIRED_CLAIMS = (
    "lexic autentic", "surse reale", "~280", "regionalisme vii", "registru de atestări",
    "glas moldovenesc", "ritm moldovenesc", "folosește dmr", "detect_technical_register",
    "lexic atestat",
)
DOCS = ("README.md", "SKILL.md", "CONTRIBUTING.md", "benchmark/*.md", "examples/*.md",
        "references/*.md")


def read(root, name):
    return (root / name).read_text(encoding="utf-8")


def find(pattern, text, label, errors):
    match = re.search(pattern, text, re.M)
    if not match:
        errors.append(f"{label}: not found")
        return None
    return match.group(1)


def check_versions(root, errors):
    cff = read(root, "CITATION.cff")
    if find(r"^cff-version: (.+)$", cff, "CFF cff-version", errors) != "1.2.0":
        errors.append("CFF cff-version must be 1.2.0")
    version = find(r"^version: (.+)$", cff, "CFF version", errors)
    readme = read(root, "README.md")
    sources = {
        "SKILL version": find(r"^version: (.+)$", read(root, "SKILL.md"), "SKILL version", errors),
        "README badge": find(r"badge/version-([\d.]+)-", readme, "README badge", errors),
        "README clone tag": find(r"git clone --branch v([\d.]+) ", readme, "README clone tag", errors),
        "README tree": find(r"YAML frontmatter \(v([\d.]+)\)", readme, "README tree", errors),
    }
    for label, value in sources.items():
        if value != version:
            errors.append(f"{label} is {value}, CFF version is {version}")
    released = re.findall(r"^## \[([\d.]+)\] - (\S+)$", read(root, "CHANGELOG.md"), re.M)
    if not released or released[0][0] != version:
        errors.append(f"CHANGELOG top release must be {version}")
    elif find(r"^date-released: (.+)$", cff, "CFF date-released", errors) != released[0][1]:
        errors.append("CFF date-released must match the CHANGELOG date")
    return version


def check_install(root, errors):
    target = find(r'^git clone --branch \S+ \S+ "(.+)"$', read(root, "README.md"),
                  "README install target", errors)
    if target != "$HOME/.claude/skills/omenizator":
        errors.append(f"README install target must be the Claude path, found {target}")


def check_inventory(root, errors):
    rows = [line for line in read(root, "references/lexicon-subset.md").splitlines()
            if line.startswith("|") and "declanșator" not in line
            and not re.match(r"^\|[ \-|]*$", line)]
    count = str(len(rows))
    claims = {
        "README text": (r"are (\d+) de rânduri", "README.md"),
        "README badge": (r"inventar-(\d+)%20", "README.md"),
        "Lexicon header": (r"Inventar public:\*\* (\d+)", "references/lexicon-subset.md"),
        "Glossary": (r"(\d+) de rânduri", "references/glosar-dmr.md"),
    }
    for label, (pattern, name) in claims.items():
        value = find(pattern, read(root, name), label, errors)
        if value is not None and value != count:
            errors.append(f"{label} says {value} rows, the inventory has {count}")


def check_activation(root, errors):
    table = [line for line in read(root, "references/provenienta-lexicala.md").splitlines()
             if line.startswith("| LEX-")]
    active = [line for line in table if "inactiv" not in line.split("|")[3]]
    for line in active:
        if "NEDESEMNAT" in line:
            errors.append(f"{line.split('|')[1].strip()} is active without a reviewer")
    if active:
        return
    if "Zero perechi" not in read(root, "README.md"):
        errors.append("README must state that zero pairs are approved")
    skill = read(root, "SKILL.md")
    if "niciuna activă" not in skill:
        errors.append("SKILL must state that no substitution is active")
    for mode in ("--argou", "stil=admin"):
        if not re.search(rf"`{mode}`\): opțiune inactivă", skill):
            errors.append(f"SKILL must mark {mode} as inactive")
        if not re.search(rf"`{mode}`\) \| Inactiv", read(root, "README.md")):
            errors.append(f"README must mark {mode} as inactive")


def check_meaning_rule(root, errors):
    if "„poate respinge” nu devine „respinge”" not in read(root, "SKILL.md"):
        errors.append("SKILL lost the modality rule")
    if "Păstrează posibilitatea reală" not in read(root, "references/tipare.md"):
        errors.append("Catalog pattern 2 lost the modality rule")


def check_catalog(root, errors):
    catalog = read(root, "references/tipare.md")
    ids = [int(value) for value in re.findall(r"^(\d+)\. \*\*", catalog, re.M)]
    if ids != list(range(1, len(ids) + 1)):
        errors.append("Catalog IDs must be consecutive")
    for name, pattern in (("README.md", r"\((\d+) semne\)"), ("SKILL.md", r"(\d+) semne")):
        if find(pattern, read(root, name), f"{name} pattern count", errors) != str(len(ids)):
            errors.append(f"{name} pattern count does not match the catalog")


def doc_paths(root):
    for pattern in DOCS:
        yield from sorted(root.glob(pattern))


def check_claims(root, errors):
    for path in doc_paths(root):
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if path.name == "lexicon-subset.md" and line.startswith("- **v"):
                continue
            lowered = line.lower()
            for claim in RETIRED_CLAIMS:
                if claim in lowered:
                    errors.append(f"{path.relative_to(root)}:{number}: retired claim {claim!r}")


def check_links(root, errors):
    for path in doc_paths(root):
        text = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\((?!https?:|#)([^)#\s]+)", text):
            if not (path.parent / target).exists():
                errors.append(f"{path.relative_to(root)}: broken link {target}")
    for target in re.findall(r"`(references/[\w.-]+\.md)`", read(root, "SKILL.md")):
        if not (root / target).exists():
            errors.append(f"SKILL.md: missing reference {target}")


def check_release(root, tag=None):
    errors = []
    version = check_versions(root, errors)
    if tag and tag != f"v{version}":
        errors.append(f"Tag {tag} does not match version {version}")
    for check in (check_install, check_inventory, check_activation, check_meaning_rule,
                  check_catalog, check_claims, check_links):
        check(root, errors)
    return errors


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--tag")
    options = parser.parse_args()
    problems = check_release(options.root, options.tag)
    for problem in problems:
        print(problem)
    print(f"{len(problems)} problem(s)")
    raise SystemExit(1 if problems else 0)
