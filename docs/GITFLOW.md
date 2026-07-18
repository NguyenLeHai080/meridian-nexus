# Gitflow

## Permanent branches

| Branch    | Purpose             | Promotion source                 |
| --------- | ------------------- | -------------------------------- |
| `prod`    | Production releases | `staging` or approved `hotfix/*` |
| `staging` | QA and demo         | `dev`                            |
| `dev`     | Feature integration | `feat/*`, `fix/*`, `refactor/*`  |

Direct pushes to `prod` and `staging` are blocked. Changes require pull requests, successful checks, and review.

Every protected branch requires the enterprise release gate. A push to `staging` or `prod` publishes artifacts only after the complete CI workflow succeeds; CD cannot race ahead of CI.

## Feature flow

```text
dev -> feat/<name> -> pull request -> dev -> pull request -> staging -> pull request -> prod
```

```bash
git switch dev
git pull --ff-only origin dev
git switch -c feat/homepage
git add .
git commit -m "feat(homepage): build storefront hero #123"
git push -u origin feat/homepage
```

After review, squash merge the feature into `dev`. Promote the tested commit through pull requests from `dev` to `staging` and from `staging` to `prod` using **merge commits**. The merge commit preserves ancestry between long-lived environment branches.

The staging promotion represents the Sprint increment selected for QA, not an arbitrary collection of partially completed stories. The production promotion requires Product Owner acceptance, QA evidence, release approval, and a confirmed rollback path.

## Hotfix flow

```text
prod -> hotfix/<name> -> pull request -> prod -> synchronization PRs -> staging and dev
```

```bash
git switch prod
git pull --ff-only origin prod
git switch -c hotfix/fix_login_error
git commit -m "fix(auth): resolve production login error #456"
git push -u origin hotfix/fix_login_error
```

After the production PR is merged and deployed, open synchronization PRs from `prod` into `staging` and `dev`. Resolve conflicts explicitly; never silently omit a production fix.

Use merge commits for both synchronization PRs so the production lineage remains visible in every environment branch.

## Release rules

- Never introduce an intentional defect into `prod` to practice hotfixes.
- Run practice exercises in a disposable branch or training repository.
- Squash short-lived branches into `dev`; never squash promotions between `dev`, `staging`, and `prod`.
- Tag production releases using semantic versions such as `v1.2.0`.
- Roll back by redeploying a previously verified immutable image tag, not by editing a running container.
- Promote the same commit and immutable artifact through environments; never rebuild different source for production.
