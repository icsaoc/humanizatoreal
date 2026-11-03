# Contributing

Thanks for helping improve Omenizator. Keep contributions small and focused.

## Add a lexicon term

Follow references/provenienta-lexicala.md. Submit the sense, register, source and
locator. Paraphrase the usage note. Argot follows the filter in its inventory.

## Add an example (`examples/`)
1. Provide a realistic `Before (AI)` block and an `After (humanized)` block.
2. Note which patterns were removed.

## Commits
- Sign your commits (`git commit -S`).
- Use Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`).
- Before opening a PR, run `python scripts/check_release.py` and
  `python -m unittest discover -s tests`.

## Review loop

Open a GitHub issue with the catalog version, a redacted example, its register,
the observable pattern, a proposed fix and a human counterexample. Review two
independent occurrences and one false-positive control before acceptance.
Reuse an existing ID for duplicates. Give accepted new patterns the next
unused ID and add a regression pair. Reserve retired IDs permanently.
Catalog SemVer: patch for clarifications, minor for compatible additions,
major for contract changes. Record changes in CHANGELOG.md.
