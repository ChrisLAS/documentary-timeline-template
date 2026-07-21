from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
