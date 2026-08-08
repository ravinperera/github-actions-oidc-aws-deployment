from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "validate_examples.py"
SPEC = importlib.util.spec_from_file_location("validate_examples", SCRIPT_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class ValidateExamplesTests(unittest.TestCase):
    def run_with_root(self, root: Path, check) -> tuple[int, list[str]]:
        original_root = validator.ROOT
        validator.ROOT = root
        try:
            errors: list[str] = []
            checked = check(errors)
            return checked, errors
        finally:
            validator.ROOT = original_root

    def test_markdown_links_accept_local_targets_and_reject_bad_paths(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            docs = root / "docs"
            docs.mkdir()
            (root / "README.md").write_text("# Example\n", encoding="utf-8")
            (docs / "guide.md").write_text(
                "[valid](../README.md)\n"
                "[missing](missing.md)\n"
                "[escape](../../outside.md)\n",
                encoding="utf-8",
            )

            checked, errors = self.run_with_root(root, validator.validate_markdown_links)

        self.assertEqual(checked, 2)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("missing local link target" in error for error in errors))
        self.assertTrue(any("link escapes repository" in error for error in errors))

    def test_workflow_validation_rejects_static_credential_markers(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow_dir = root / ".github" / "workflows"
            workflow_dir.mkdir(parents=True)
            (workflow_dir / "unsafe.yml").write_text(
                "name: Unsafe example\n"
                "jobs:\n"
                "  test:\n"
                "    env:\n"
                "      AWS_ACCESS_KEY_ID: placeholder\n"
                "      AWS_SECRET_ACCESS_KEY: placeholder\n",
                encoding="utf-8",
            )

            checked, errors = self.run_with_root(root, validator.validate_workflows)

        self.assertEqual(checked, 1)
        self.assertEqual(len(errors), 2)
        self.assertTrue(any("AWS_ACCESS_KEY_ID" in error for error in errors))
        self.assertTrue(any("AWS_SECRET_ACCESS_KEY" in error for error in errors))

    def test_workflow_validation_accepts_oidc_only_workflow(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow_dir = root / ".github" / "workflows"
            workflow_dir.mkdir(parents=True)
            (workflow_dir / "oidc.yml").write_text(
                "name: OIDC\n"
                "permissions:\n"
                "  contents: read\n"
                "  id-token: write\n",
                encoding="utf-8",
            )

            checked, errors = self.run_with_root(root, validator.validate_workflows)

        self.assertEqual(checked, 1)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
