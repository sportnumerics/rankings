"""
NCAA.com stats scraper (workaround for stats.ncaa.org Akamai blocking).

Scrapes player and team statistics from NCAA.com public stats pages.
"""

from typing import Any, Iterator
from bs4 import BeautifulSoup
from ..shared.types import Location, PlayerSummary, Scraper
import logging

logger = logging.getLogger(__name__)


class NcaaDotCom(Scraper):
    """Scraper for NCAA.com stats pages (not stats.ncaa.org)"""
    
    base_url = 'https://www.ncaa.com'
    
    # Stat ID mappings from NCAA.com dropdowns
    STAT_IDS = {
        'individual': {
            'goals_per_game': 222,
            'assists_per_game': 223,
            'saves_per_game': 586,
            'save_percentage': 224,
            'goals_against_avg': 225,
            'ground_balls_per_game': 227,
            'points_per_game': 221,
            'faceoff_win_pct': 410,
            'caused_turnovers_per_game': 560,
            'shot_percentage': 562,
            'manup_goals': 960,
        },
        'team': {
            'scoring_offense': 228,
            'scoring_defense': 229,
            'assists_per_game': 535,
            'saves_per_game': 536,
            'points_per_game': 537,
            'ground_balls_per_game': 538,
            'faceoff_win_pct': 230,
            'manup_offense': 231,
            'mandown_defense': 232,
            'scoring_margin': 238,
            'winning_percentage': 233,
        }
    }
    
    def __init__(self, sports=['lacrosse-men', 'lacrosse-women'], divs=['d1', 'd2', 'd3']):
        self.sports = sports
        self.divs = divs
    
    def get_stat_leaders_url(self, sport: str, division: str, stat_type: str, stat_name: str) -> str:
        """
        Build URL for a specific stat leaderboard.
        
        Args:
            sport: 'lacrosse-men' or 'lacrosse-women'
            division: 'd1', 'd2', or 'd3'
            stat_type: 'individual' or 'team'
            stat_name: key from STAT_IDS dict
        
        Returns:
            Full URL to stats page
        """
        stat_id = self.STAT_IDS[stat_type][stat_name]
        return f'{self.base_url}/stats/{sport}/{division}/current/{stat_type}/{stat_id}'
    
    def parse_individual_stats_html(self, html: str, sport: str, division: str, stat_name: str) -> list[dict]:
        """
        Parse individual player stats from NCAA.com HTML table.
        
        Returns list of dicts with keys:
            rank, player_name, school, class, position, games, total, per_game
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find the stats table - it's inside block-stats div
        stats_block = soup.find('div', class_='block-stats')
        if not stats_block:
            logger.warning(f"No stats block found for {sport} {division} {stat_name}")
            return []
        
        table = stats_block.find('table')
        if not table or not table.tbody:
            logger.warning(f"No table found in stats block for {sport} {division} {stat_name}")
            return []
        
        rows = table.tbody.find_all('tr')
        results = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 8:
                continue
            
            try:
                rank_text = cols[0].get_text(strip=True)
                player_name = cols[1].get_text(strip=True)
                
                # School is in col 2, may have image + link
                school_link = cols[2].find('a')
                school_name = school_link.get_text(strip=True) if school_link else cols[2].get_text(strip=True)
                
                player_class = cols[3].get_text(strip=True)
                position = cols[4].get_text(strip=True)
                games = cols[5].get_text(strip=True)
                total = cols[6].get_text(strip=True)
                per_game = cols[7].get_text(strip=True)
                
                results.append({
                    'rank': rank_text,
                    'player_name': player_name,
                    'school': school_name,
                    'class': player_class,
                    'position': position,
                    'games': int(games) if games.isdigit() else 0,
                    'total': float(total) if total.replace('.', '').isdigit() else 0.0,
                    'per_game': float(per_game) if per_game.replace('.', '').isdigit() else 0.0,
                })
            except Exception as e:
                logger.warning(f"Error parsing row: {e}")
                continue
        
        return results
    
    def parse_team_stats_html(self, html: str, sport: str, division: str, stat_name: str) -> list[dict]:
        """
        Parse team stats from NCAA.com HTML table.
        
        Returns list of dicts with keys:
            rank, team_name, per_game (or other stat value)
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        stats_block = soup.find('div', class_='block-stats')
        if not stats_block:
            logger.warning(f"No stats block found for {sport} {division} {stat_name}")
            return []
        
        table = stats_block.find('table')
        if not table or not table.tbody:
            logger.warning(f"No table found in stats block for {sport} {division} {stat_name}")
            return []
        
        rows = table.tbody.find_all('tr')
        results = []
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) < 3:
                continue
            
            try:
                rank_text = cols[0].get_text(strip=True)
                
                # Team name may have link
                team_link = cols[1].find('a')
                team_name = team_link.get_text(strip=True) if team_link else cols[1].get_text(strip=True)
                
                stat_value = cols[2].get_text(strip=True)
                
                results.append({
                    'rank': rank_text,
                    'team_name': team_name,
                    'per_game': float(stat_value) if stat_value.replace('.', '').isdigit() else 0.0,
                })
            except Exception as e:
                logger.warning(f"Error parsing team row: {e}")
                continue
        
        return results
    
    def get_limiter_session_args(self):
        """Rate limiting for NCAA.com - be respectful"""
        return {'per_minute': 30}
    
    def convert_roster(self, html, team):
        """Not implemented for NCAA.com scraper"""
        return None
