#!/usr/bin/env python3
"""PR velocity check - identifies stale PRs and suggests unblock actions."""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

STALE_HOURS = int(sys.argv[1]) if len(sys.argv) > 1 else 24

def get_github_token():
    """Get GitHub token using the same method as git credential helper."""
    token_script = Path.home() / ".openclaw" / "github-app-token.py"
    result = subprocess.run(["python3", str(token_script)], capture_output=True, text=True)
    return result.stdout.strip()

def get_pr_status():
    """Fetch all open PRs with their status."""
    token = get_github_token()
    env = {"GH_TOKEN": token}
    result = subprocess.run(
        ["gh", "pr", "list", "--json", "number,title,updatedAt,statusCheckRollup,headRefName", "--limit", "50"],
        capture_output=True,
        text=True,
        env={**subprocess.os.environ, **env}
    )
    return json.loads(result.stdout)

def check_ci_status(checks):
    """Determine overall CI status from status check rollup."""
    if not checks:
        return "NO_CI"
    
    completed = [c for c in checks if c.get("conclusion")]
    if not completed:
        return "PENDING"
    
    conclusions = [c["conclusion"] for c in completed]
    if all(c in ("SUCCESS", "SKIPPED") for c in conclusions):
        return "PASSING"
    elif any(c == "FAILURE" for c in conclusions):
        return "FAILING"
    else:
        return "MIXED"

def main():
    print(f"🔍 PR Velocity Check (stale threshold: {STALE_HOURS}h)")
    print("=" * 70)
    print()
    
    try:
        prs = get_pr_status()
    except Exception as e:
        print(f"Error fetching PRs: {e}", file=sys.stderr)
        sys.exit(1)
    
    now = datetime.now(timezone.utc)
    stale_count = 0
    passing_awaiting = 0
    failing_ci = 0
    
    print(f"📊 Summary")
    print("-" * 20)
    print(f"Total open PRs: {len(prs)}")
    print()
    print("📋 PR Status Details")
    print("-" * 20)
    
    for pr in prs:
        number = pr["number"]
        title = pr["title"]
        branch = pr["headRefName"]
        updated_at = datetime.fromisoformat(pr["updatedAt"].replace("Z", "+00:00"))
        age = now - updated_at
        age_hours = int(age.total_seconds() / 3600)
        
        ci_status = check_ci_status(pr.get("statusCheckRollup", []))
        
        # Determine status and action
        if ci_status == "PASSING":
            if age.total_seconds() > STALE_HOURS * 3600:
                status_icon = "⚠️  STALE"
                action = f"Ready for review ({age_hours}h stale)"
                stale_count += 1
            else:
                status_icon = "✅ READY"
                action = f"Awaiting review ({age_hours}h old)"
            passing_awaiting += 1
        elif ci_status == "FAILING":
            status_icon = "❌ FAILING"
            action = "Needs fixes"
            failing_ci += 1
        elif ci_status == "PENDING":
            status_icon = "🟡 PENDING"
            action = "CI running"
        else:
            status_icon = "⚪ UNKNOWN"
            action = "Check status"
        
        print()
        print(f"{status_icon}  PR #{number}: {title}")
        print(f"    Branch: {branch}")
        print(f"    Age: {age_hours}h")
        print(f"    Next action: {action}")
        print(f"    Link: https://github.com/sportnumerics/rankings/pull/{number}")
    
    print()
    print("=" * 70)
    print("📈 Velocity Metrics")
    print("-" * 20)
    print(f"Passing & awaiting review: {passing_awaiting}")
    print(f"Stale (>{STALE_HOURS}h, passing CI): {stale_count}")
    print(f"Failing CI: {failing_ci}")
    print()
    
    if stale_count > 0:
        print(f"⚠️  Action needed: {stale_count} stale PR(s) ready for review")
        sys.exit(1)
    else:
        print("✅ No stale PRs detected")
        sys.exit(0)

if __name__ == "__main__":
    main()
