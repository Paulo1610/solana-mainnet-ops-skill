import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SkillStructureTests(unittest.TestCase):
    def test_required_files_exist(self):
        required = [
            "README.md",
            "LICENSE",
            "install.sh",
            "install.ps1",
            "skill/SKILL.md",
            "scripts/classify_solana_issue.py",
        ]
        for rel_path in required:
            self.assertTrue((ROOT / rel_path).exists(), rel_path)

    def test_skill_frontmatter_has_name_and_description(self):
        text = (ROOT / "skill" / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"))
        self.assertIn("name: solana-mainnet-ops", text)
        self.assertIn("description:", text)
        self.assertIn("transaction", text.lower())
        self.assertIn("incident", text.lower())

    def test_skill_links_resolve(self):
        text = (ROOT / "skill" / "SKILL.md").read_text(encoding="utf-8")
        for rel_path in [
            "triage.md",
            "transaction-failures.md",
            "rpc-and-congestion.md",
            "indexing-and-webhooks.md",
            "program-log-analysis.md",
            "security-incident.md",
            "launch-readiness.md",
            "resources.md",
        ]:
            self.assertIn(rel_path, text)
            self.assertTrue((ROOT / "skill" / rel_path).exists(), rel_path)

    def test_classifier_detects_fixture_signals(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "classify_solana_issue.py"),
                str(ROOT / "tests" / "fixtures" / "sample-errors.txt"),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        result = json.loads(completed.stdout)
        signals = {item["signal"] for item in result["signals"]}
        self.assertEqual(result["severity"], "sev1")
        self.assertIn("production_user_impact", signals)
        self.assertIn("blockhash_expired", signals)
        self.assertIn("anchor_constraint", signals)
        self.assertIn("compute_exhausted", signals)
        self.assertIn("rpc_throttle_or_provider", signals)
        self.assertIn("webhook_or_indexer_lag", signals)
        self.assertTrue(result["artifacts"]["signatures"])
        self.assertTrue(result["artifacts"]["programs"])
        self.assertTrue(result["suggested_workflow"])

    def test_classifier_markdown_output(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "classify_solana_issue.py"),
                str(ROOT / "examples" / "production-incident-input.txt"),
                "--format",
                "markdown",
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("# Solana Issue Classification", completed.stdout)
        self.assertIn("Severity: `sev1`", completed.stdout)

    def test_example_inputs_have_detected_signals(self):
        for example in [
            "production-incident-input.txt",
            "rpc-throttling-input.txt",
            "jupiter-swap-failure-input.txt",
            "webhook-lag-input.txt",
        ]:
            completed = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts" / "classify_solana_issue.py"),
                    str(ROOT / "examples" / example),
                ],
                check=True,
                capture_output=True,
                text=True,
            )
            result = json.loads(completed.stdout)
            self.assertTrue(result["signals"], example)
            self.assertNotEqual(result["severity"], "unknown", example)


if __name__ == "__main__":
    unittest.main()
