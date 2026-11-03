import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts/check_release.py"
CFF = (REPO / "CITATION.cff").read_text(encoding="utf-8")
VERSION = re.search(r"^version: (.+)$", CFF, re.M).group(1)
RELEASED = re.search(r"^date-released: (.+)$", CFF, re.M).group(1)


class ReleaseGateTest(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "repo"
        shutil.copytree(REPO, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))

    def gate(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), "--root", str(self.root), *args],
                              capture_output=True, text=True, encoding="utf-8", errors="replace")

    def mutate(self, name, old, new):
        path = self.root / name
        text = path.read_text(encoding="utf-8")
        self.assertIn(old, text)
        path.write_text(text.replace(old, new), encoding="utf-8")

    def assert_fails(self, message):
        result = self.gate()
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn(message, result.stdout)

    def test_clean_repo_passes(self):
        result = self.gate()
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_cff_schema_version(self):
        self.mutate("CITATION.cff", "cff-version: 1.2.0", "cff-version: 1.5.0")
        self.assert_fails("cff-version must be 1.2.0")

    def test_skill_version_mismatch(self):
        self.mutate("SKILL.md", f"version: {VERSION}", "version: 9.9.9")
        self.assert_fails("SKILL version is 9.9.9")

    def test_readme_tag_mismatch(self):
        self.mutate("README.md", f"--branch v{VERSION}", "--branch v9.9.9")
        self.assert_fails("README clone tag is 9.9.9")

    def test_changelog_date_mismatch(self):
        self.mutate("CITATION.cff", f"date-released: {RELEASED}", "date-released: 2020-01-01")
        self.assert_fails("date-released must match")

    def test_changelog_top_mismatch(self):
        self.mutate("CHANGELOG.md", f"## [{VERSION}]", "## [9.9.9]")
        self.assert_fails(f"CHANGELOG top release must be {VERSION}")

    def test_readme_mode_claimed_available(self):
        self.mutate("README.md", "`--argou`) | Inactiv", "`--argou`) | Activ")
        self.assert_fails("README must mark --argou as inactive")

    def test_catalog_modality_removed(self):
        self.mutate("references/tipare.md", "Păstrează posibilitatea reală", "Afirmă")
        self.assert_fails("Catalog pattern 2 lost the modality rule")

    def test_pattern_count_mismatch(self):
        self.mutate("README.md", "(29 semne)", "(30 semne)")
        self.assert_fails("README.md pattern count")

    def test_missing_skill_reference(self):
        self.mutate("SKILL.md", "`references/tipare.md`", "`references/lipsa.md`")
        self.assert_fails("missing reference references/lipsa.md")

    def test_wrong_install_path(self):
        self.mutate("README.md", "$HOME/.claude/skills/omenizator", "$HOME/.agents/skills/omenizator")
        self.assert_fails("must be the Claude path")

    def test_inventory_count(self):
        self.mutate("README.md", "are 154 de rânduri", "are 280 de rânduri")
        self.assert_fails("says 280 rows")

    def test_inventory_row_removed(self):
        self.mutate("references/lexicon-subset.md", "| lingusitor | linge-blide | substantiv, personaj tipologic | DMR Vol.1 |\n", "")
        self.assert_fails("the inventory has 153")

    def test_active_entry_without_reviewer(self):
        self.mutate("references/provenienta-lexicala.md", "Viu, condiționat; inactiv", "Viu")
        self.assert_fails("active without a reviewer")

    def test_mode_claimed_available(self):
        self.mutate("SKILL.md", "`--argou`): opțiune inactivă", "`--argou`): opțiune activă")
        self.assert_fails("SKILL must mark --argou as inactive")

    def test_zero_pairs_statement(self):
        self.mutate("README.md", "Zero perechi", "Multe perechi")
        self.assert_fails("zero pairs")

    def test_retired_claim(self):
        self.mutate("README.md", "## Moduri", "## Moduri\n\nLexic autentic.")
        self.assert_fails("retired claim 'lexic autentic'")

    def test_lexicon_history_is_allowed_but_header_is_not(self):
        self.mutate("references/lexicon-subset.md", "# Lexicon DMR", "# Regionalisme vii DMR")
        self.assert_fails("retired claim 'regionalisme vii'")

    def test_modality_rule_removed(self):
        self.mutate("SKILL.md", "(„poate respinge” nu devine „respinge”)", "")
        self.assert_fails("SKILL lost the modality rule")

    def test_catalog_gap(self):
        self.mutate("references/tipare.md", "\n5. **", "\n50. **")
        self.assert_fails("IDs must be consecutive")

    def test_broken_link(self):
        self.mutate("README.md", "(benchmark/README.md)", "(benchmark/LIPSA.md)")
        self.assert_fails("broken link benchmark/LIPSA.md")

    def test_tag_mismatch(self):
        result = self.gate("--tag", "v9.9.9")
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn("does not match version", result.stdout)

    def test_matching_tag_passes(self):
        self.assertEqual(self.gate("--tag", f"v{VERSION}").returncode, 0)
