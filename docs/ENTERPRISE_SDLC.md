# Enterprise Scrum Delivery Lifecycle

## Accountability

Scrum defines product and delivery accountability; it does not replace engineering controls.

| Role                   | Accountability                                                                | Required evidence                                      |
| ---------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------ |
| Product Owner          | Orders the backlog and accepts product outcomes                               | Acceptance criteria and product sign-off               |
| Scrum Master           | Protects Scrum, removes impediments, and improves flow                        | Ceremony outcomes, blockers, and retrospective actions |
| Developers             | Design, implement, test, review, and operate the increment                    | Code, tests, threat considerations, and runbooks       |
| Tech Lead or CODEOWNER | Reviews architecture, maintainability, and technical risk                     | Approved pull request                                  |
| QA                     | Validates acceptance, regression, and exploratory scenarios                   | Test evidence linked in the pull request               |
| Security reviewer      | Reviews high-risk authentication, authorization, data, and dependency changes | Threat review or explicit no-impact statement          |
| Release Manager        | Controls environment promotion and rollback readiness                         | Deployment approval and release record                 |

The Scrum Master facilitates these controls but must not silently act as Product Owner, QA, security reviewer, and technical approver at the same time.

## Sprint lifecycle

1. **Refinement:** clarify value, acceptance criteria, dependencies, security impact, and estimate.
2. **Sprint planning:** select only items meeting the Definition of Ready and define the Sprint Goal.
3. **Implementation:** create a short-lived branch from `dev`, keep the PR draft while incomplete, and update tests with code.
4. **Review:** move the PR out of draft, obtain CI evidence and CODEOWNER review, then merge into `dev` with a merge commit.
5. **QA promotion:** merge `dev` into `staging` with a merge commit after the Sprint increment is coherent.
6. **Validation:** QA performs acceptance, regression, exploratory, performance, and security checks against staging.
7. **Release:** merge `staging` into `prod` with a merge commit after release approval and rollback confirmation.
8. **Review and retrospective:** inspect outcomes, incidents, lead time, escaped defects, and improvement actions.

## Definition of Ready

An item may enter a sprint only when:

- business value and acceptance criteria are testable;
- dependencies, data classification, and permissions are understood;
- the item is estimated and small enough for one sprint;
- rollout, monitoring, and rollback implications are known;
- unresolved decisions are converted into time-boxed spikes.

## Definition of Done

An increment is done only when:

- acceptance criteria and automated tests pass;
- formatting, linting, type checking, unit, contract, and adversarial tests pass;
- dependency audit, SAST, and container vulnerability gates pass;
- security, privacy, RBAC, migration, and performance impact are reviewed;
- observability and rollback procedures are documented;
- the artifact is immutable, traceable to a commit, and promoted without rebuilding;
- Product Owner acceptance and required environment approvals are recorded.

## Delivery gates

```text
Issue and DoR
  -> Draft PR
  -> PR governance
  -> Static quality
  -> Unit and contract tests
  -> Adversarial security tests
  -> Dependency and CodeQL analysis
  -> Container build and vulnerability scan
  -> Release gate
  -> Staging approval and immutable publication
  -> Runtime smoke and QA evidence
  -> Production approval and publication
  -> Monitoring and rollback window
```

## Risk policy

- **Low:** documentation, isolated presentation, or non-behavioral maintenance.
- **Medium:** ordinary business behavior with bounded data and rollback impact.
- **High:** authentication, authorization, payment, customer data, migrations, or availability-critical changes.
- **Critical:** emergency security fixes, active incidents, destructive migrations, or irreversible external effects.

High and critical changes require explicit security review, focused regression evidence, and a rollback rehearsal or documented impossibility rationale.

## Dependency automation

Dependabot targets `dev` only. Compatible minor and patch updates are grouped by
ecosystem, while major updates remain isolated for breaking-change review. Each
ecosystem is limited to three concurrent pull requests and runs in a staggered
weekly window.

Bot-authored dependency pull requests receive a narrow governance exception:
the verified `dependabot[bot]` identity may omit a manually created issue and
Definition of Done. Branch, target, and Conventional Commit title checks remain
mandatory, and every quality, security, approval, and release gate still runs.

## Hotfix control

P0 and approved P1 incidents may use `hotfix/<name>` from `prod`. The PR still requires an issue, tests, CI, approval, and production environment authorization. After deployment, merge `prod` back into `staging` and `dev` using merge commits, then hold a blameless incident review.

## Metrics

Track sprint goal success, lead time, cycle time, deployment frequency, change failure rate, mean time to recovery, escaped defects, flaky tests, vulnerability age, and rollback frequency. Metrics improve the system; they must not be used to rank individuals.
