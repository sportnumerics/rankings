#!/usr/bin/env bash
# PR Health Dashboard
# Shows open PRs sorted by age with actionable merge recommendations

set -euo pipefail

REPO="sportnumerics/rankings"
TOKEN=$(python3 ~/.openclaw/github-app-token.py)
export GH_TOKEN=$TOKEN

echo "📊 PR Health Dashboard - $(date '+%Y-%m-%d %H:%M')"
echo "Repository: $REPO"
echo ""

# Get all open PRs with metadata
PRS=$(gh pr list --repo "$REPO" --state open --limit 50 \
  --json number,title,createdAt,updatedAt,statusCheckRollup,reviewDecision,isDraft,headRefName)

# Count total
TOTAL=$(echo "$PRS" | python3 -c "import sys, json; print(len(json.load(sys.stdin)))")
echo "Total Open PRs: $TOTAL"
echo ""

# Priority categories
echo "═══════════════════════════════════════════════════════════════"
echo "🚨 PRODUCTION HOTFIXES (merge immediately if passing)"
echo "═══════════════════════════════════════════════════════════════"
echo "$PRS" | python3 -c "
import sys, json
from datetime import datetime

prs = json.load(sys.stdin)
hotfixes = [pr for pr in prs if 'hotfix' in pr['headRefName'].lower()]

if not hotfixes:
    print('(none)')
else:
    for pr in sorted(hotfixes, key=lambda x: x['createdAt']):
        num = pr['number']
        title = pr['title']
        created = datetime.fromisoformat(pr['createdAt'].replace('Z', '+00:00'))
        age_hours = (datetime.now(created.tzinfo) - created).total_seconds() / 3600
        
        # Check if all checks passed
        checks = pr.get('statusCheckRollup', [])
        all_passed = all(
            c.get('conclusion') in ['SUCCESS', 'SKIPPED', None] 
            for c in checks
        )
        status = '✅ READY' if all_passed else '⏳ checks running'
        
        print(f'  #{num} {title}')
        print(f'       Age: {age_hours:.1f}h | {status}')
        print(f'       https://github.com/sportnumerics/rankings/pull/{num}')
        print()
"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "✅ READY TO MERGE (all checks passing, awaiting review)"
echo "═══════════════════════════════════════════════════════════════"
echo "$PRS" | python3 -c "
import sys, json
from datetime import datetime

prs = json.load(sys.stdin)
ready = []

for pr in prs:
    if 'hotfix' in pr['headRefName'].lower():
        continue  # Already shown above
    
    checks = pr.get('statusCheckRollup', [])
    all_passed = all(
        c.get('conclusion') in ['SUCCESS', 'SKIPPED', None] 
        for c in checks
    )
    
    if all_passed and not pr['isDraft']:
        ready.append(pr)

if not ready:
    print('(none)')
else:
    # Sort by age (oldest first)
    for pr in sorted(ready, key=lambda x: x['createdAt']):
        num = pr['number']
        title = pr['title']
        created = datetime.fromisoformat(pr['createdAt'].replace('Z', '+00:00'))
        age_days = (datetime.now(created.tzinfo) - created).days
        
        category = '📄 docs' if pr['headRefName'].startswith('docs/') else \
                   '🧪 test' if 'test' in pr['headRefName'].lower() else \
                   '⚡️ feat'
        
        print(f'  {category} #{num} {title}')
        print(f'         Age: {age_days}d | Last update: {pr[\"updatedAt\"][:10]}')
        print(f'         Branch: {pr[\"headRefName\"]}')
        print()
"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "📈 VELOCITY SUMMARY"
echo "═══════════════════════════════════════════════════════════════"
echo "$PRS" | python3 -c "
import sys, json
from datetime import datetime

prs = json.load(sys.stdin)

# Calculate staleness metrics
now = datetime.now()
ages = []
for pr in prs:
    created = datetime.fromisoformat(pr['createdAt'].replace('Z', '+00:00'))
    age_days = (datetime.now(created.tzinfo) - created).days
    ages.append(age_days)

if ages:
    avg_age = sum(ages) / len(ages)
    max_age = max(ages)
    stale_count = sum(1 for a in ages if a > 7)
    
    print(f'  Average PR age: {avg_age:.1f} days')
    print(f'  Oldest PR: {max_age} days')
    print(f'  Stale (>7d): {stale_count} PRs')
    print()
    
    if stale_count > 5:
        print('  ⚠️  High stale PR count — consider batching reviews or closing stale branches')
    elif avg_age > 10:
        print('  ⚠️  High average age — velocity bottleneck detected')
    else:
        print('  ✅ Velocity healthy')
"
echo ""

echo "═══════════════════════════════════════════════════════════════"
echo "🎯 RECOMMENDED ACTIONS"
echo "═══════════════════════════════════════════════════════════════"
echo "$PRS" | python3 -c "
import sys, json
from datetime import datetime

prs = json.load(sys.stdin)

# Find hotfixes
hotfixes = [pr for pr in prs if 'hotfix' in pr['headRefName'].lower()]
if hotfixes:
    for pr in hotfixes[:3]:
        checks = pr.get('statusCheckRollup', [])
        all_passed = all(c.get('conclusion') in ['SUCCESS', 'SKIPPED', None] for c in checks)
        if all_passed:
            print(f'  1. Merge hotfix #{pr[\"number\"]} immediately (production fix)')

# Find oldest ready PR
ready = []
for pr in prs:
    if 'hotfix' not in pr['headRefName'].lower():
        checks = pr.get('statusCheckRollup', [])
        all_passed = all(c.get('conclusion') in ['SUCCESS', 'SKIPPED', None] for c in checks)
        if all_passed and not pr['isDraft']:
            ready.append(pr)

if ready:
    oldest = sorted(ready, key=lambda x: x['createdAt'])[0]
    age_days = (datetime.now(datetime.fromisoformat(oldest['createdAt'].replace('Z', '+00:00')).tzinfo) - 
                datetime.fromisoformat(oldest['createdAt'].replace('Z', '+00:00'))).days
    print(f'  2. Review oldest ready PR #{oldest[\"number\"]} ({age_days}d old)')

if len(ready) > 5:
    print(f'  3. Batch-review {len(ready)} ready PRs to clear backlog')
    print(f'     Suggest: review all test/docs PRs first (low risk)')
"
