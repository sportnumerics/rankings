#!/bin/bash
# PR velocity check - identifies stale PRs and suggests unblock actions
# Usage: ./scripts/pr-velocity-check.sh [--stale-hours 24]

set -e

STALE_HOURS=${1:-24}
STALE_SECONDS=$((STALE_HOURS * 3600))
NOW=$(date +%s)

echo "🔍 PR Velocity Check (stale threshold: ${STALE_HOURS}h)"
echo "================================================"
echo ""

# Get all open PRs with status checks
TOKEN=$(python3 ~/.openclaw/github-app-token.py)
PRS=$(GH_TOKEN=$TOKEN gh pr list --json number,title,updatedAt,statusCheckRollup,headRefName --limit 50)

# Track stats
TOTAL_PRS=$(echo "$PRS" | jq '. | length')
STALE_COUNT=0
PASSING_AWAITING_REVIEW=0
FAILING_CI=0

echo "📊 Summary"
echo "----------"
echo "Total open PRs: $TOTAL_PRS"
echo ""

# Process each PR
echo "📋 PR Status Details"
echo "-------------------"

echo "$PRS" | jq -r '.[] | @json' | while read -r pr; do
    NUMBER=$(echo "$pr" | jq -r '.number')
    TITLE=$(echo "$pr" | jq -r '.title')
    UPDATED_AT=$(echo "$pr" | jq -r '.updatedAt')
    BRANCH=$(echo "$pr" | jq -r '.headRefName')
    
    # Convert updatedAt to seconds
    UPDATED_SECONDS=$(date -d "$UPDATED_AT" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$UPDATED_AT" +%s 2>/dev/null)
    AGE_SECONDS=$((NOW - UPDATED_SECONDS))
    AGE_HOURS=$((AGE_SECONDS / 3600))
    
    # Check CI status
    CI_STATUS=$(echo "$pr" | jq -r '
        if (.statusCheckRollup | length) == 0 then
            "NO_CI"
        else
            [.statusCheckRollup[] | select(.conclusion != null) | .conclusion] |
            if (. | length) == 0 then
                "PENDING"
            elif all(. == "SUCCESS" or . == "SKIPPED") then
                "PASSING"
            elif any(. == "FAILURE") then
                "FAILING"
            else
                "MIXED"
            end
        end
    ')
    
    # Determine status icon and action
    if [ "$CI_STATUS" = "PASSING" ]; then
        if [ $AGE_SECONDS -gt $STALE_SECONDS ]; then
            STATUS_ICON="⚠️  STALE"
            ACTION="Ready for review (${AGE_HOURS}h stale)"
            STALE_COUNT=$((STALE_COUNT + 1))
        else
            STATUS_ICON="✅ READY"
            ACTION="Awaiting review (${AGE_HOURS}h old)"
        fi
        PASSING_AWAITING_REVIEW=$((PASSING_AWAITING_REVIEW + 1))
    elif [ "$CI_STATUS" = "FAILING" ]; then
        STATUS_ICON="❌ FAILING"
        ACTION="Needs fixes"
        FAILING_CI=$((FAILING_CI + 1))
    elif [ "$CI_STATUS" = "PENDING" ]; then
        STATUS_ICON="🟡 PENDING"
        ACTION="CI running"
    else
        STATUS_ICON="⚪ UNKNOWN"
        ACTION="Check status"
    fi
    
    echo ""
    echo "$STATUS_ICON  PR #$NUMBER: $TITLE"
    echo "    Branch: $branch"
    echo "    Age: ${AGE_HOURS}h"
    echo "    Next action: $ACTION"
    echo "    Link: https://github.com/sportnumerics/rankings/pull/$NUMBER"
done

echo ""
echo "================================================"
echo "📈 Velocity Metrics"
echo "-------------------"
echo "Passing & awaiting review: $PASSING_AWAITING_REVIEW"
echo "Stale (>${STALE_HOURS}h, passing CI): $STALE_COUNT"
echo "Failing CI: $FAILING_CI"
echo ""

if [ $STALE_COUNT -gt 0 ]; then
    echo "⚠️  Action needed: $STALE_COUNT stale PR(s) ready for review"
    exit 1
else
    echo "✅ No stale PRs detected"
    exit 0
fi
