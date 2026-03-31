#!/usr/bin/env python3
"""
Quick test to verify Playwright can fetch NCAA.com stats.
"""

from playwright.sync_api import sync_playwright
import sys

def test_ncaa_goals_leaders():
    """Test fetching goals per game leaders from NCAA.com"""
    url = "https://www.ncaa.com/stats/lacrosse-men/d1/current/individual/222"
    
    print(f"Testing Playwright with NCAA.com...")
    print(f"URL: {url}\n")
    
    with sync_playwright() as p:
        print("Launching Chromium...")
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to page...")
        page.goto(url, wait_until="networkidle", timeout=30000)
        
        print("Waiting for stats table...")
        page.wait_for_selector("table tbody tr", timeout=10000)
        
        print("Extracting data...")
        rows = page.query_selector_all("table tbody tr")
        
        print(f"\n✅ Found {len(rows)} player rows\n")
        print("Top 5 Goals Leaders:")
        print("-" * 60)
        
        for i, row in enumerate(rows[:5], 1):
            cols = row.query_selector_all("td")
            if len(cols) >= 8:
                rank = cols[0].inner_text().strip()
                name = cols[1].inner_text().strip()
                school = cols[2].inner_text().strip()
                player_class = cols[3].inner_text().strip()
                position = cols[4].inner_text().strip()
                games = cols[5].inner_text().strip()
                total = cols[6].inner_text().strip()
                per_game = cols[7].inner_text().strip()
                
                print(f"{rank}. {name} ({school}) - {per_game} GPG")
                print(f"   Class: {player_class}, Pos: {position}, Games: {games}, Total: {total}")
        
        browser.close()
        print("\n✅ Test successful! Playwright can fetch NCAA.com data.")
        return True

if __name__ == "__main__":
    try:
        success = test_ncaa_goals_leaders()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
