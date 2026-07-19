# Contributing to Meridian Nexus

## Before coding

- Create or assign a Story, Bug, or Spike issue that meets the Definition of Ready.
- Branch from the correct base: `dev` for features and `prod` for hotfixes.
- Keep the pull request in draft until implementation, tests, risk analysis, and rollback notes are ready.
- Never put credentials, tokens, customer data, or `.env` files in commits or pull requests.

## Branch names

- `feat/<feature_name>`
- `fix/<bug_name>`
- `hotfix/<urgent_fix_name>`
- `refactor/<area_name>`
- `docs/<topic_name>`

Use lowercase snake case after the prefix, for example `feat/customer_profile`.

## Commit messages

Use Conventional Commits:

```text
<type>(<scope>): <description> #<issue_id>
```

Examples:

```text
feat(auth): add session revocation #42
fix(checkout): prevent duplicate order #57
docs(gitflow): document hotfix process #61
```

Allowed types are `feat`, `fix`, `refactor`, `docs`, `chore`, `style`, `perf`, `vendor`, `test`, `ci`, `build`, and `security`.

- Keep the subject concise and imperative.
- Do not end the subject with a period.
- Use one language consistently inside a commit message.
- Include a body when the reason or migration impact is not obvious.
- Use `BREAKING CHANGE:` in the footer for incompatible contracts.

## Pull requests

- Keep each pull request focused on one issue.
- Use a Conventional Commit-style PR title ending with the issue ID.
- Complete every required PR section and at least five Definition of Done checks.
- Classify risk and include acceptance, regression, security, rollout, monitoring, and rollback evidence.
- Do not merge while required checks or review are pending.
- Merge feature, fix, refactor, documentation, and CI branches into `dev` with a merge commit so their reviewed ancestry remains visible.
- Merge promotion PRs from `dev` to `staging`, from `staging` to `prod`, and hotfix synchronization PRs with a merge commit. Squashing long-lived branches breaks their ancestry and causes avoidable conflicts on the next promotion.

## Enterprise gates

The `Enterprise release gate` passes only when governance, backend static analysis, contract tests, adversarial security tests, frontend static analysis, frontend unit tests, production build, dependency/license audit, CodeQL, and container scanning all succeed.

Changes cannot enter `staging` or `prod` until the corresponding GitHub Environment approval is recorded. See `docs/ENTERPRISE_SDLC.md` for Scrum accountability, Definition of Ready, Definition of Done, risk policy, ceremonies, and operational metrics.
