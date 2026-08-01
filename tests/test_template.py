from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

import yaml


ROOT = pathlib.Path(__file__).resolve().parents[1]


class TemplateTests(unittest.TestCase):
    def test_neutral_template_validates(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts/validate_project.py"), str(ROOT)],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_configurator_replaces_project_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            destination = pathlib.Path(temporary) / "project"
            shutil.copytree(
                ROOT,
                destination,
                ignore=shutil.ignore_patterns(".git", "__pycache__"),
            )
            subprocess.run(
                [
                    sys.executable,
                    str(destination / "scripts/configure_project.py"),
                    "--root",
                    str(destination),
                    "--title",
                    "History of Example Technology",
                    "--slug",
                    "example-technology",
                    "--thesis",
                    "Example technology emerged through a documented sequence of experiments.",
                ],
                check=True,
                stdout=subprocess.PIPE,
                text=True,
            )
            config = yaml.safe_load(
                (destination / "config/project.yaml").read_text(encoding="utf-8")
            )
            self.assertEqual(config["project"]["slug"], "example-technology")
            self.assertEqual(config["project"]["title"], "History of Example Technology")
            validation = subprocess.run(
                [
                    sys.executable,
                    str(destination / "scripts/validate_project.py"),
                    str(destination),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_optional_integration_lock_and_missing_checkouts_validate(self) -> None:
        lock = json.loads(
            (ROOT / "integrations/integrations.lock.json").read_text(encoding="utf-8")
        )
        self.assertEqual(lock["schema_version"], 1)
        self.assertEqual(
            {item["id"] for item in lock["integrations"]},
            {"video-shotcraft", "openmontage"},
        )
        for item in lock["integrations"]:
            self.assertEqual(len(item["commit"]), 40)
            self.assertTrue(item["checkout"].startswith(".integrations/"))
            self.assertFalse(item["direct_code_adaptation_default"])

        result = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/check_optional_integrations.py"),
                "--root",
                str(ROOT),
                "--allow-missing",
            ],
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_documentary_visual_development_skill_is_complete(self) -> None:
        skill_root = ROOT / "skills/documentary-visual-development"
        skill = (skill_root / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("TODO", skill)
        self.assertIn("name: documentary-visual-development", skill)
        self.assertIn("scripts/apply_visual_overlays.py", skill)
        self.assertTrue((skill_root / "references/visual-workflow.md").is_file())
        self.assertTrue((skill_root / "references/upstream-integrations.md").is_file())

        metadata = yaml.safe_load(
            (skill_root / "agents/openai.yaml").read_text(encoding="utf-8")
        )
        self.assertIn(
            "$documentary-visual-development",
            metadata["interface"]["default_prompt"],
        )


if __name__ == "__main__":
    unittest.main()
