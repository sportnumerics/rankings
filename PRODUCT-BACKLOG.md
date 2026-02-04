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
1) **Document "how deploy works" (1-page ops doc)**
   - Outcome: reduce friction when something breaks (IAM/Terraform/CloudFront).
   - First increment: add `infrastructure/DEPLOYMENT.md` describing roles, workflows, and common failure modes.
   - Acceptance checks:
     - Covers: which workflows deploy what, which IAM role, where Terraform state lives
     - Includes "how to debug" checklist

### In Progress
- (none)

### PR
- **Add backend end-to-end smoke test in CI** (PR #20) - validates scrape→predict→sync pipeline on PRs, syncs to dev
- **Add Next.js build caching** (PR #13) - caches npm + .next/cache for faster deploys

---

## Next (candidate work)

### Idea
- (seed ideas live in PRODUCT-IDEAS.md; promote the best ones here)

### Blocked
- (none)

---

## Done
- ✅ Add /api/health endpoint with version info + README docs (already present)
- ✅ Fix Terraform deploy failure (PR #9, merged 2026-01-28)
- ✅ Make health_check.sh token-proof (already implemented in scripts/health_check.sh)
