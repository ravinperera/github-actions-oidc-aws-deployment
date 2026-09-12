from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_PATH = Path(__file__).parents[1] / "scripts" / "validate_examples.py"
SPEC = importlib.util.spec_from_file_location("validate_examples_pull_request_target", SCRIPT_PATH)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = validator
SPEC.loader.exec_module(validator)


class PullRequestTargetGuardTests(unittest.TestCase):
    def validate_workflow(self, content: str) -> list[str]:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflow_dir = root / ".github" / "workflows"
            workflow_dir.mkdir(parents=True)
            (workflow_dir / "example.yml").write_text(content, encoding="utf-8")

            original_root = validator.ROOT
            validator.ROOT = root
            try:
                errors: list[str] = []
                validator.validate_workflows(errors)
                return errors
            finally:
                validator.ROOT = original_root

    def test_rejects_pull_request_target_for_oidc_credentials(self) -> None:
        errors = self.validate_workflow(
            "name: Unsafe OIDC trigger\n"
            "on:\n"
            "  pull_request_target:\n"
            "permissions:\n"
            "  contents: read\n"
            "  id-token: write\n"
            "jobs:\n"
            "  deploy:\n"
            "    steps:\n"
            "      - uses: aws-actions/configure-aws-credentials@v4\n"
            "        with:\n"
            "          role-to-assume: arn:aws:iam::111122223333:role/example-role\n"
            "          aws-region: eu-west-2\n"
        )

        self.assertEqual(len(errors), 1)
        self.assertIn("must not use pull_request_target", errors[0])

    def test_accepts_pull_request_for_oidc_credentials(self) -> None:
        errors = self.validate_workflow(
            "name: Reviewed OIDC trigger\n"
            "on:\n"
            "  pull_request:\n"
            "permissions:\n"
            "  contents: read\n"
            "  id-token: write\n"
            "jobs:\n"
            "  deploy:\n"
            "    steps:\n"
            "      - uses: aws-actions/configure-aws-credentials@v4\n"
            "        with:\n"
            "          role-to-assume: arn:aws:iam::111122223333:role/example-role\n"
            "          aws-region: eu-west-2\n"
        )

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
