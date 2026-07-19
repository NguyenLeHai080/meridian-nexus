import json
import os
import re
from urllib.error import HTTPError
from urllib.request import Request, urlopen


TITLE_PATTERN = re.compile(
    r"^(feat|fix|refactor|docs|chore|style|perf|vendor|test|ci|build|security)"
    r"(?:\([a-z0-9._/-]+\))?!?: .+ #(\d+)$"
)
SHORT_LIVED_BRANCH_PATTERN = re.compile(
    r"^(feat|fix|refactor|docs|chore|test|ci|security)/[a-z0-9][a-z0-9._-]*$"
)
DEPENDABOT_BRANCH_PATTERN = re.compile(r"^dependabot/[A-Za-z0-9_./-]+$")
DEPENDABOT_TITLE_PATTERN = re.compile(
    r"^(?:chore|build)\(deps(?:-dev)?\): (?:bump|update) .+$",
    re.IGNORECASE,
)
REQUIRED_SECTIONS = (
    "## Related issue",
    "## Change",
    "## Risk",
    "## Verification",
    "## Deployment and rollback",
    "## Definition of Done",
)


def fail(message: str) -> None:
    print(f"::error::{message}")
    raise SystemExit(1)


def validate_branch(head_ref: str, base_ref: str) -> None:
    if base_ref == "dev":
        if head_ref == "prod" or SHORT_LIVED_BRANCH_PATTERN.fullmatch(head_ref):
            return
        fail("PRs into dev must come from a short-lived branch or prod hotfix synchronization")

    if base_ref == "staging":
        if head_ref in {"dev", "prod"} or head_ref.startswith("hotfix/"):
            return
        fail("PRs into staging must come from dev, prod, or an approved hotfix branch")

    if base_ref == "prod":
        if head_ref == "staging" or head_ref.startswith("hotfix/"):
            return
        fail("PRs into prod must come from staging or an emergency hotfix branch")

    fail(f"Unsupported protected base branch: {base_ref}")


def validate_issue(issue_id: str) -> None:
    repository = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    request = Request(
        f"https://api.github.com/repos/{repository}/issues/{issue_id}",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    try:
        with urlopen(request, timeout=15) as response:
            issue = json.load(response)
    except HTTPError as error:
        fail(f"Issue #{issue_id} cannot be read: GitHub returned {error.code}")

    if "pull_request" in issue:
        fail(f"#{issue_id} refers to a pull request, not an issue")


def validate_dependabot_pull_request(
    author: str, title: str, head_ref: str, base_ref: str
) -> bool:
    if author != "dependabot[bot]":
        return False

    if base_ref != "dev":
        fail("Dependabot pull requests may target dev only")
    if not DEPENDABOT_BRANCH_PATTERN.fullmatch(head_ref):
        fail("Dependabot must use a GitHub-managed dependabot/* branch")
    if not DEPENDABOT_TITLE_PATTERN.fullmatch(title):
        fail("Dependabot title must use chore(deps) or chore(deps-dev)")

    print(f"Dependabot governance passed for {head_ref} -> {base_ref}")
    return True


def main() -> None:
    title = os.environ.get("PR_TITLE", "").strip()
    body = os.environ.get("PR_BODY", "")
    head_ref = os.environ.get("HEAD_REF", "")
    base_ref = os.environ.get("BASE_REF", "")
    author = os.environ.get("PR_AUTHOR", "")

    if validate_dependabot_pull_request(author, title, head_ref, base_ref):
        return

    title_match = TITLE_PATTERN.fullmatch(title)
    if not title_match:
        fail("PR title must follow: type(scope): concise description #issue_id")

    validate_branch(head_ref, base_ref)
    validate_issue(title_match.group(2))

    missing_sections = [section for section in REQUIRED_SECTIONS if section not in body]
    if missing_sections:
        fail(f"PR body is missing required sections: {', '.join(missing_sections)}")

    if not re.search(r"\b(?:Closes|Fixes|Refs)\s+#\d+\b", body, re.IGNORECASE):
        fail("Related issue must use Closes #id, Fixes #id, or Refs #id")

    if body.count("- [x]") + body.count("- [X]") < 5:
        fail("Definition of Done requires at least five completed checklist items")

    if "Select risk:" in body or "Describe configuration" in body:
        fail("PR template placeholders must be replaced before review")

    print(f"PR governance passed for {head_ref} -> {base_ref}, linked to issue #{title_match.group(2)}")


if __name__ == "__main__":
    try:
        main()
    except KeyError as error:
        fail(f"Missing workflow environment variable: {error.args[0]}")
