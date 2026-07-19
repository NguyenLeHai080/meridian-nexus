import unittest

from validate_pull_request import validate_dependabot_pull_request


class DependabotGovernanceTests(unittest.TestCase):
    def test_accepts_verified_bot_on_dev(self) -> None:
        accepted = validate_dependabot_pull_request(
            "dependabot[bot]",
            "chore(deps): bump the backend-compatible group in /BE",
            "dependabot/pip/BE/dev/backend-compatible-123",
            "dev",
        )

        self.assertTrue(accepted)

    def test_does_not_exempt_human_author(self) -> None:
        accepted = validate_dependabot_pull_request(
            "developer",
            "chore(deps): bump a dependency",
            "dependabot/pip/BE/dev/package-1.0.0",
            "dev",
        )

        self.assertFalse(accepted)

    def test_rejects_protected_environment_target(self) -> None:
        with self.assertRaises(SystemExit):
            validate_dependabot_pull_request(
                "dependabot[bot]",
                "chore(deps): bump a dependency",
                "dependabot/pip/BE/dev/package-1.0.0",
                "staging",
            )

    def test_rejects_non_dependency_title(self) -> None:
        with self.assertRaises(SystemExit):
            validate_dependabot_pull_request(
                "dependabot[bot]",
                "feat: change application behavior",
                "dependabot/pip/BE/dev/package-1.0.0",
                "dev",
            )


if __name__ == "__main__":
    unittest.main()
