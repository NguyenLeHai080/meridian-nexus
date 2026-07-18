# Development Workflow

This repository uses automated formatting and quality gates. Generated output, dependencies, local environment files, and databases must not be committed.

## Frontend

Run from `FE`:

```bash
npm ci
npm run quality
npm audit --audit-level=high
```

## Backend

Run from `BE` after installing `requirements-dev.txt`:

```bash
ruff format --check northstar tests_python scripts
ruff check northstar tests_python scripts
pytest
pip-audit -r requirements.txt
```

## Change process

1. Create an issue describing the change and acceptance criteria.
2. Create `feat/<name>` from `dev`, or `hotfix/<name>` from `prod` for an emergency fix.
3. Keep changes inside the module that owns the behavior.
4. Add tests for changed contracts, permissions, and business branches.
5. Run all quality checks before pushing.
6. Use a Conventional Commit message containing the issue ID.
7. Open a pull request and wait for CI and review before merging.

## Readable React code

- Shared layouts compose dedicated header, main, footer, or sidebar components.
- Prefer explicit `if/else` blocks for branching behavior.
- Keep API calls and business mutations outside layout components.
- Reuse focused hooks, stores, schemas, and components instead of duplicating logic.

See `CONTRIBUTING.md` and `docs/GITFLOW.md` for repository governance.
