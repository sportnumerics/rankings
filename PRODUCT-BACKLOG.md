# Sportnumerics Backlog

A lightweight, assistant-run task management system.

## Status meanings
- **Idea**: worth considering, not yet scoped
- **Ready**: scoped into a small first increment that can be done in <= 1-3 hours
- **In Progress**: being implemented on a branch
- **PR**: PR open, awaiting review/CI
- **Done**: merged
- **Blocked**: needs Will input or external dependency

## Rules
- Prefer *small* increments that ship value or reduce risk.
- Each backlog item must have: **Outcome**, **First increment**, **Acceptance checks**.
- When possible: add/adjust tests with the change.

---

## Now (top priority)

### Ready
1) **Add Next.js build caching in GitHub Actions**
   - Outcome: faster deploy runs; fewer rebuilds; reduced Next.js "No build cache found" warning.
   - First increment: update deploy workflow(s) to cache:
     - `~/.npm` (or npm cache dir)
     - `frontend/.next/cache`
   - Acceptance checks:
     - Workflow run shows cache hit on subsequent runs
     - Deploy job time decreases measurably (even ~20-40%)

2) **Add a minimal /api/health endpoint with version info**
   - Outcome: quick way to confirm deploy + data connectivity from the outside.
   - First increment: implement `/api/health` returning `{ ok: true, gitSha, buildTime }` (and optionally a cheap S3 list/head to confirm bucket access).
   - Acceptance checks:
     - Endpoint returns 200 in dev
     - Included in README for debugging

3) **Document "how deploy works" (1-page ops doc)**
   - Outcome: reduce friction when something breaks (IAM/Terraform/CloudFront).
   - First increment: add `infrastructure/DEPLOYMENT.md` describing roles, workflows, and common failure modes.
   - Acceptance checks:
     - Covers: which workflows deploy what, which IAM role, where Terraform state lives
     - Includes "how to debug" checklist

### In Progress
- (none)

### PR
- (none)

---

## Next (candidate work)

### Idea
- (seed ideas live in PRODUCT-IDEAS.md; promote the best ones here)

### Blocked
- (none)

---

## Done
- ✅ Fix Terraform deploy failure (PR #9, merged 2026-01-28)
- ✅ Make health_check.sh token-proof (already implemented in scripts/health_check.sh)
