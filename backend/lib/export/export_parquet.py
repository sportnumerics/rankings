"""
Export optimized parquet files for frontend queries.

Generates 12 materialized view files, each optimized for a specific page/component.
"""

import logging
import os
import pathlib
from typing import List
import pyarrow as pa
import pyarrow.parquet as pq

from ..shared.types import (
    Game, Player, PlayerRating, TeamDetail, TeamRating
)
from ..shared import shared

LOGGER = logging.getLogger(__name__)


def write_parquet(rows: List[dict], filepath: pathlib.Path, sort_order: List[tuple[str, str]]):
    """Write list of dicts to parquet with specified sort order."""
    if not rows:
        LOGGER.warning(f'No rows to write to {filepath}')
        return
    
    filepath.parent.mkdir(parents=True, exist_ok=True)
    table = pa.Table.from_pylist(rows)
    
    # Convert sort_order using from_ordering
    sorting_columns = None
    if sort_order:
        sorting_columns = pq.SortingColumn.from_ordering(table.schema, sort_order)
    
    pq.write_table(table, filepath, compression='gzip', sorting_columns=sorting_columns)
    LOGGER.debug(f'Wrote {len(rows)} rows to {filepath}')


def export_parquet_views(args):
    """
    Generate 12 optimized parquet files for frontend queries.
    
    Reads from existing data files (team_ratings, player_ratings, schedules, games, players)
    and generates materialized views with optimal sort orders.
    """
    out_dir = args.out_dir
    for year in shared.years(args.year):
        LOGGER.info(f'Exporting parquet views for {year}')
        
        # Load source data
        LOGGER.info('Loading team ratings...')
        team_ratings = load_team_ratings(args.input_dir, year)
        LOGGER.info(f'Loaded {len(team_ratings)} team ratings')
        
        LOGGER.info('Loading player ratings...')
        player_ratings = load_player_ratings(args.input_dir, year)
        LOGGER.info(f'Loaded {len(player_ratings)} player ratings')
        
        LOGGER.info('Loading teams...')
        teams = load_teams(args.input_dir, year)
        LOGGER.info(f'Loaded {len(teams)} teams')
        
        LOGGER.info('Loading schedules...')
        schedules = load_schedules(args.input_dir, year)
        LOGGER.info(f'Loaded {len(schedules)} schedules')
        
        LOGGER.info('Loading games...')
        games = load_games(args.input_dir, year)
        LOGGER.info(f'Loaded {len(games)} games')
        
        LOGGER.info('Loading players...')
        players = load_players(args.input_dir, year)
        LOGGER.info(f'Loaded {len(players)} players')
        
        # Create output directory
        year_dir = pathlib.Path(os.path.join(out_dir, year))
        year_dir.mkdir(parents=True, exist_ok=True)
        
        # Export each materialized view
        # Build team lookup for enriching references (use all teams, not just schedules)
        team_lookup = {t.id: t for t in teams}
        
        export_teams_list(team_ratings, teams, year_dir)
        export_team_metadata(team_ratings, teams, year_dir)
        export_team_schedules(schedules, team_lookup, year_dir)
        export_team_rosters(players, player_ratings, team_lookup, year_dir)
        
        export_players_list(players, player_ratings, team_lookup, year_dir)
        export_player_metadata(players, player_ratings, team_lookup, year_dir)
        export_player_gamelogs(players, team_lookup, year_dir)
        export_goals_leaders(players, player_ratings, team_lookup, year_dir)
        export_assists_leaders(players, player_ratings, team_lookup, year_dir)
        
        export_games_list(games, team_lookup, year_dir)
        export_game_metadata(games, team_lookup, year_dir)
        export_game_boxscores(games, year_dir)
        
        # Write sentinel file to indicate all files are ready
        (year_dir / '_ready').write_text('')
        
        LOGGER.info(f'Completed parquet export for {year}')


def load_team_ratings(input_dir: str, year: str) -> dict[str, TeamRating]:
    """Load team ratings indexed by team id."""
    path = shared.parquet_path(input_dir, year, 'team_ratings', 'data.parquet')
    ratings = list(shared.load_parquet_dataset(TeamRating, path))
    return {r.team: r for r in ratings}


def load_player_ratings(input_dir: str, year: str) -> dict[str, PlayerRating]:
    """Load player ratings indexed by player id."""
    path = shared.parquet_path(input_dir, year, 'player_ratings', 'data.parquet')
    ratings = list(shared.load_parquet_dataset(PlayerRating, path))
    return {r.id: r for r in ratings}


def load_schedules(input_dir: str, year: str) -> List[TeamDetail]:
    """Load team schedules."""
    path = shared.parquet_path(input_dir, year, 'schedules')
    return list(shared.load_parquet_dataset(TeamDetail, path))


def load_games(input_dir: str, year: str) -> List[dict]:
    """Load games as raw dicts (avoid expensive dataclass deserialization)."""
    path = shared.parquet_path(input_dir, year, 'games')
    if not os.path.exists(path):
        LOGGER.warning(f'No games data found at {path}')
        return []
    # Load as dicts instead of Game objects to avoid slow nested deserialization
    return pq.ParquetDataset(path).read().to_pylist()


def load_teams(input_dir: str, year: str) -> List:
    """Load all teams."""
    from ..shared.types import Team
    path = shared.parquet_path(input_dir, year, 'teams')
    return list(shared.load_parquet_dataset(Team, path))


def load_players(input_dir: str, year: str) -> dict[str, dict]:
    """Load full player data as dicts indexed by player id."""
    path = shared.parquet_path(input_dir, year, 'players', 'data.parquet')
    if not os.path.exists(path):
        LOGGER.warning(f'No players data found at {path}')
        return {}
    # Load as dicts to avoid slow nested deserialization
    players = pq.read_table(path).to_pylist()
    return {p['id']: p for p in players}


# --- Teams Pages ---

def export_teams_list(team_ratings: dict[str, TeamRating], 
                      teams: List,
                      year_dir: pathlib.Path):
    """
    File: teams-list.parquet
    Sort: (div ASC, rank ASC)
    Query: SELECT * FROM teams_list WHERE div = ? ORDER BY rank
    """
    rows = []
    
    # Calculate ranks within each division
    teams_by_div = {}
    for team in teams:
        div = team.div
        if div not in teams_by_div:
            teams_by_div[div] = []
        
        # Look up rating; use defaults if team hasn't played
        rating = team_ratings.get(team.id)
        has_rating = rating is not None
        offense = rating.offense if rating else 0.0
        defense = rating.defense if rating else 0.0
        overall = rating.overall if rating else 0.0
        
        teams_by_div[div].append((team.id, offense, defense, overall, has_rating, team))
    
    for div, div_teams in teams_by_div.items():
        # Sort by: rated teams first (desc), then overall desc
        # This puts unrated teams (overall=0.0) below negative-rated teams
        div_teams.sort(key=lambda t: (t[4], t[3]), reverse=True)  # t[4]=has_rating, t[3]=overall
        for rank, (team_id, offense, defense, overall, has_rating, team) in enumerate(div_teams, start=1):
            rows.append({
                'div': div,
                'rank': rank,
                'id': team_id,
                'name': team.name,
                'sport': team.sport,
                'source': team.source,
                'schedule_url': team.schedule.url if team.schedule else None,
                'offense': offense,
                'defense': defense,
                'overall': overall,
            })
    
    rows.sort(key=lambda r: (r['div'], r['rank']))
    write_parquet(rows, year_dir / 'teams-list.parquet',
                       sort_order=[('div', 'ascending'), ('rank', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to teams-list.parquet')


def export_team_metadata(team_ratings: dict[str, TeamRating],
                         teams: List,
                         year_dir: pathlib.Path):
    """
    File: team-metadata.parquet
    Sort: (div ASC, id ASC)
    Query: SELECT * FROM team_metadata WHERE div = ? AND id = ?
    """
    rows = []
    
    # Calculate ranks within each division
    teams_by_div = {}
    for team in teams:
        div = team.div
        if div not in teams_by_div:
            teams_by_div[div] = []
        
        # Look up rating; use defaults if team hasn't played
        rating = team_ratings.get(team.id)
        has_rating = rating is not None
        offense = rating.offense if rating else 0.0
        defense = rating.defense if rating else 0.0
        overall = rating.overall if rating else 0.0
        
        teams_by_div[div].append((team.id, offense, defense, overall, has_rating, team))
    
    for div, div_teams in teams_by_div.items():
        # Sort by: rated teams first (desc), then overall desc
        div_teams.sort(key=lambda t: (t[4], t[3]), reverse=True)  # t[4]=has_rating, t[3]=overall
        for rank, (team_id, offense, defense, overall, has_rating, team) in enumerate(div_teams, start=1):
            rows.append({
                'div': div,
                'id': team_id,
                'name': team.name,
                'sport': team.sport,
                'source': team.source,
                'schedule_url': team.schedule.url if team.schedule else None,
                'offense': offense,
                'defense': defense,
                'overall': overall,
                'rank': rank,
            })
    
    rows.sort(key=lambda r: (r['div'], r['id']))
    write_parquet(rows, year_dir / 'team-metadata.parquet',
                       sort_order=[('div', 'ascending'), ('id', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to team-metadata.parquet')


def export_team_schedules(schedules: List[TeamDetail], team_lookup: dict, year_dir: pathlib.Path):
    """
    File: team-schedules.parquet
    Sort: (div ASC, team_id ASC, date ASC)
    Query: SELECT * FROM team_schedules WHERE div = ? AND team_id = ? ORDER BY date
    """
    rows = []
    
    for schedule in schedules:
        team = schedule.team
        for game in schedule.games:
            # Enrich opponent with full team data
            opponent = team_lookup.get(game.opponent.id or game.opponent.alt_id)
            
            rows.append({
                'div': team.div,
                'team_id': team.id,
                'date': game.date,
                'game_id': f"{team.id}_{game.opponent.id}_{game.date}",
                'opponent_id': game.opponent.id or game.opponent.alt_id,
                'opponent_name': game.opponent.name,
                'opponent_div': opponent.div if opponent else None,
                'opponent_schedule_url': opponent.schedule.url if opponent and opponent.schedule else None,
                'opponent_sport': opponent.sport if opponent else None,
                'opponent_source': opponent.source if opponent else None,
                'home': game.home,
                'points_for': game.result.points_for if game.result else None,
                'points_against': game.result.points_against if game.result else None,
                'details_url': game.details.url if game.details else None,
            })
    
    rows.sort(key=lambda r: (r['div'], r['team_id'], r['date']))
    write_parquet(rows, year_dir / 'team-schedules.parquet',
                       sort_order=[('div', 'ascending'), ('team_id', 'ascending'), ('date', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to team-schedules.parquet')


def export_team_rosters(players: dict[str, dict],
                        player_ratings: dict[str, PlayerRating],
                        team_lookup: dict,
                        year_dir: pathlib.Path):
    """
    File: team-rosters.parquet
    Sort: (div ASC, team_id ASC, number ASC)
    Query: SELECT * FROM team_rosters WHERE div = ? AND team_id = ? ORDER BY number
    """
    rows = []
    
    for player_id, player in players.items():
        rating = player_ratings.get(player_id)
        team_sum = player['team']
        team = team_lookup.get(team_sum['id'])
        if not team:
            continue
        team = team_lookup.get(team_sum['id'])
        if not team:
            continue
        rows.append({
            'div': team.div,
            'team_id': team.id,
            'team_name': team.name,
            'team_schedule_url': team.schedule.url if team.schedule else None,
            'team_sport': team.sport,
            'team_source': team.source,
            'number': player.get('number') or 0,  # Default to 0 for sorting
            'player_id': player['id'],
            'player_name': player['name'],
            'position': player.get('position'),
            'class_year': player.get('class_year'),
            'eligibility': player.get('eligibility'),
            'height': player.get('height'),
            'weight': player.get('weight'),
            'high_school': player.get('high_school'),
            'hometown': player.get('hometown'),
            'external_link': player.get('external_link'),
            'points': rating.points if rating else 0.0,
            'goals': rating.goals if rating else 0.0,
            'assists': rating.assists if rating else 0.0,
        })
    
    rows.sort(key=lambda r: (r['div'], r['team_id'], r['number']))
    write_parquet(rows, year_dir / 'team-rosters.parquet',
                       sort_order=[('div', 'ascending'), ('team_id', 'ascending'), ('number', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to team-rosters.parquet')


# --- Players Pages ---

def export_players_list(players: dict[str, dict],
                        player_ratings: dict[str, PlayerRating],
                        team_lookup: dict,
                        year_dir: pathlib.Path):
    """
    File: players-list.parquet
    Sort: (div ASC, points DESC)
    Query: SELECT * FROM players_list WHERE div = ? ORDER BY points DESC LIMIT 200
    """
    rows = []
    
    for player_id, player in players.items():
        rating = player_ratings.get(player_id)
        if not rating:
            continue
        team_sum = player['team']
        team = team_lookup.get(team_sum['id'])
        if not team:
            continue
        team = team_lookup.get(team_sum['id'])
        if not team:
            continue
        rows.append({
            'div': team.div,
            'points': rating.points,
            'player_id': player['id'],
            'player_name': player['name'],
            'team_id': team.id,
            'team_name': team.name,
            'team_schedule_url': team.schedule.url if team.schedule else None,
            'team_sport': team.sport,
            'team_source': team.source,
            'goals': rating.goals,
            'assists': rating.assists,
            'position': player.get('position'),
            'number': player.get('number'),
            'class_year': player.get('class_year'),
        })
    
    rows.sort(key=lambda r: (r['div'], -r['points']))  # DESC points via negative
    write_parquet(rows, year_dir / 'players-list.parquet',
                       sort_order=[('div', 'ascending'), ('points', 'descending')])
    LOGGER.info(f'Exported {len(rows)} rows to players-list.parquet')


def export_player_metadata(players: dict[str, dict],
                           player_ratings: dict[str, PlayerRating],
                           team_lookup: dict,
                           year_dir: pathlib.Path):
    """
    File: player-metadata.parquet
    Sort: (div ASC, player_id ASC)
    Query: SELECT * FROM player_metadata WHERE div = ? AND player_id = ?
    """
    rows = []
    
    for player_id, player in players.items():
        rating = player_ratings.get(player_id)
        team_sum = player['team']
        team = team_lookup.get(team_sum['id'])
        if not team:
            continue
        rows.append({
            'div': team.div,
            'player_id': player['id'],
            'player_name': player['name'],
            'team_id': team.id,
            'team_name': team.name,
            'team_schedule_url': team.schedule.url if team.schedule else None,
            'team_sport': team.sport,
            'team_source': team.source,
            'points': rating.points if rating else 0.0,
            'goals': rating.goals if rating else 0.0,
            'assists': rating.assists if rating else 0.0,
            'position': player.get('position'),
            'number': player.get('number'),
            'class_year': player.get('class_year'),
            'eligibility': player.get('eligibility'),
            'height': player.get('height'),
            'weight': player.get('weight'),
            'high_school': player.get('high_school'),
            'hometown': player.get('hometown'),
            'external_link': player.get('external_link'),
        })
    
    rows.sort(key=lambda r: (r['div'], r['player_id']))
    write_parquet(rows, year_dir / 'player-metadata.parquet',
                       sort_order=[('div', 'ascending'), ('player_id', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to player-metadata.parquet')


def export_player_gamelogs(players: dict[str, dict], team_lookup: dict, year_dir: pathlib.Path):
    """
    File: player-gamelogs.parquet
    Sort: (div ASC, player_id ASC, date DESC)
    Query: SELECT * FROM player_gamelogs WHERE div = ? AND player_id = ? ORDER BY date DESC
    """
    rows = []
    
    for player_id, player in players.items():
        team_sum = player['team']
        team = team_lookup.get(team_sum['id'])
        if not team:
            continue
        for stat in player.get('stats') or []:
            opponent_sum = stat['opponent']
            opponent = team_lookup.get(opponent_sum.get('id') or opponent_sum.get('alt_id'))
            rows.append({
                'div': team.div,
                'player_id': player['id'],
                'date': stat['date'],
                'game_id': stat['game_id'],
                'opponent_id': opponent_sum.get('id') or opponent_sum.get('alt_id'),
                'opponent_name': opponent_sum['name'],
                'opponent_div': opponent.div if opponent else None,
                'opponent_schedule_url': opponent.schedule.url if opponent and opponent.schedule else None,
                'opponent_sport': opponent.sport if opponent else None,
                'opponent_source': opponent.source if opponent else None,
                'g': stat['g'],
                'a': stat['a'],
                'gb': stat.get('gb'),
            })
    
    # Sort by div, player_id, then date DESC
    rows.sort(key=lambda r: (r['div'], r['player_id'], r['date']), reverse=False)
    # Since we can't specify mixed ASC/DESC in sort, we'll reverse dates after grouping
    # Actually, let's keep dates in DESC order for natural reading
    from itertools import groupby
    sorted_rows = []
    for (div, player_id), group in groupby(rows, key=lambda r: (r['div'], r['player_id'])):
        group_list = list(group)
        group_list.sort(key=lambda r: r['date'], reverse=True)
        sorted_rows.extend(group_list)
    
    write_parquet(sorted_rows, year_dir / 'player-gamelogs.parquet',
                       sort_order=[('div', 'ascending'), ('player_id', 'ascending'), ('date', 'descending')])
    LOGGER.info(f'Exported {len(sorted_rows)} rows to player-gamelogs.parquet')


def export_goals_leaders(players: dict[str, dict],
                         player_ratings: dict[str, PlayerRating],
                         team_lookup: dict,
                         year_dir: pathlib.Path):
    """
    File: goals-leaders.parquet
    Sort: (div ASC, goals DESC)
    Query: SELECT * FROM goals_leaders WHERE div = ? ORDER BY goals DESC LIMIT 50
    """
    rows = []
    
    for player_id, player in players.items():
        rating = player_ratings.get(player_id)
        if not rating:
            continue
        team_sum = player['team']
        team = team_lookup.get(team_sum['id'])
        if not team:
            continue
        rows.append({
            'div': team.div,
            'goals': rating.goals,
            'player_id': player['id'],
            'player_name': player['name'],
            'team_id': team.id,
            'team_name': team.name,
            'team_schedule_url': team.schedule.url if team.schedule else None,
            'team_sport': team.sport,
            'team_source': team.source,
            'points': rating.points,
            'assists': rating.assists,
            'position': player.get('position'),
            'number': player.get('number'),
            'class_year': player.get('class_year'),
        })
    
    rows.sort(key=lambda r: (r['div'], -r['goals']))
    write_parquet(rows, year_dir / 'goals-leaders.parquet',
                       sort_order=[('div', 'ascending'), ('goals', 'descending')])
    LOGGER.info(f'Exported {len(rows)} rows to goals-leaders.parquet')


def export_assists_leaders(players: dict[str, dict],
                           player_ratings: dict[str, PlayerRating],
                           team_lookup: dict,
                           year_dir: pathlib.Path):
    """
    File: assists-leaders.parquet
    Sort: (div ASC, assists DESC)
    Query: SELECT * FROM assists_leaders WHERE div = ? ORDER BY assists DESC LIMIT 50
    """
    rows = []
    
    for player_id, player in players.items():
        rating = player_ratings.get(player_id)
        if not rating:
            continue
        team_sum = player['team']
        team = team_lookup.get(team_sum['id'])
        if not team:
            continue
        rows.append({
            'div': team.div,
            'assists': rating.assists,
            'player_id': player['id'],
            'player_name': player['name'],
            'team_id': team.id,
            'team_name': team.name,
            'team_schedule_url': team.schedule.url if team.schedule else None,
            'team_sport': team.sport,
            'team_source': team.source,
            'points': rating.points,
            'goals': rating.goals,
            'position': player.get('position'),
            'number': player.get('number'),
            'class_year': player.get('class_year'),
        })
    
    rows.sort(key=lambda r: (r['div'], -r['assists']))
    write_parquet(rows, year_dir / 'assists-leaders.parquet',
                       sort_order=[('div', 'ascending'), ('assists', 'descending')])
    LOGGER.info(f'Exported {len(rows)} rows to assists-leaders.parquet')


# --- Games Pages ---

def export_games_list(games: List[dict], team_lookup: dict, year_dir: pathlib.Path):
    """
    File: games-list.parquet
    Sort: (div ASC, date DESC)
    Query: SELECT * FROM games_list WHERE div = ? ORDER BY date DESC LIMIT 100
    
    Note: Each game appears TWICE (once for each team's division) to enable
    efficient division filtering via row group skipping.
    """
    rows = []
    
    for game in games:
        home_team_sum = game['home_team']
        away_team_sum = game['away_team']
        result = game.get('result')
        
        # Enrich with full team data
        home_team = team_lookup.get(home_team_sum['id'])
        away_team = team_lookup.get(away_team_sum['id'])
        
        if not home_team or not away_team:
            continue  # Skip games with missing team data
        
        # Add row for home team's division
        rows.append({
            'div': home_team.div,
            'date': game['date'],
            'game_id': game['id'],
            'external_link': game.get('external_link'),
            'home_team_id': home_team.id,
            'home_team_name': home_team.name,
            'home_team_div': home_team.div,
            'home_team_schedule_url': home_team.schedule.url if home_team.schedule else None,
            'home_team_sport': home_team.sport,
            'home_team_source': home_team.source,
            'away_team_id': away_team.id,
            'away_team_name': away_team.name,
            'away_team_div': away_team.div,
            'away_team_schedule_url': away_team.schedule.url if away_team.schedule else None,
            'away_team_sport': away_team.sport,
            'away_team_source': away_team.source,
            'home_score': result['points_for'] if result and 'points_for' in result else None,
            'away_score': result['points_against'] if result and 'points_against' in result else None,
        })
        
        # Add row for away team's division (if different)
        if away_team.div != home_team.div:
            rows.append({
                'div': away_team.div,
                'date': game['date'],
                'game_id': game['id'],
                'external_link': game.get('external_link'),
                'home_team_id': home_team.id,
                'home_team_name': home_team.name,
                'home_team_div': home_team.div,
                'home_team_schedule_url': home_team.schedule.url if home_team.schedule else None,
                'home_team_sport': home_team.sport,
                'home_team_source': home_team.source,
                'away_team_id': away_team.id,
                'away_team_name': away_team.name,
                'away_team_div': away_team.div,
                'away_team_schedule_url': away_team.schedule.url if away_team.schedule else None,
                'away_team_sport': away_team.sport,
                'away_team_source': away_team.source,
                'home_score': result['points_for'] if result and 'points_for' in result else None,
                'away_score': result['points_against'] if result and 'points_against' in result else None,
            })
    
    rows.sort(key=lambda r: (r['div'], r['date']), reverse=False)
    # Reverse dates within each division
    from itertools import groupby
    sorted_rows = []
    for div, group in groupby(rows, key=lambda r: r['div']):
        group_list = list(group)
        group_list.sort(key=lambda r: r['date'], reverse=True)
        sorted_rows.extend(group_list)
    
    write_parquet(sorted_rows, year_dir / 'games-list.parquet',
                       sort_order=[('div', 'ascending'), ('date', 'descending')])
    LOGGER.info(f'Exported {len(sorted_rows)} rows to games-list.parquet (includes duplicates for cross-division games)')


def export_game_metadata(games: List[dict], team_lookup: dict, year_dir: pathlib.Path):
    """
    File: game-metadata.parquet
    Sort: (game_id ASC, div ASC)
    Query: SELECT * FROM game_metadata WHERE game_id = ? LIMIT 1
    
    Note: Each game appears TWICE for consistency with games-list.
    Sort by game_id first to enable efficient single-game lookups.
    """
    rows = []
    
    for game in games:
        home_team_sum = game['home_team']
        away_team_sum = game['away_team']
        result = game.get('result')
        
        # Enrich with full team data
        home_team = team_lookup.get(home_team_sum['id'])
        away_team = team_lookup.get(away_team_sum['id'])
        
        if not home_team or not away_team:
            continue
        
        # Add row for home team's division
        rows.append({
            'div': home_team.div,
            'game_id': game['id'],
            'date': game['date'],
            'external_link': game.get('external_link'),
            'home_team_id': home_team.id,
            'home_team_name': home_team.name,
            'home_team_div': home_team.div,
            'home_team_schedule_url': home_team.schedule.url if home_team.schedule else None,
            'home_team_sport': home_team.sport,
            'home_team_source': home_team.source,
            'away_team_id': away_team.id,
            'away_team_name': away_team.name,
            'away_team_div': away_team.div,
            'away_team_schedule_url': away_team.schedule.url if away_team.schedule else None,
            'away_team_sport': away_team.sport,
            'away_team_source': away_team.source,
            'home_score': result['points_for'] if result and 'points_for' in result else None,
            'away_score': result['points_against'] if result and 'points_against' in result else None,
        })
        
        # Add row for away team's division (if different)
        if away_team.div != home_team.div:
            rows.append({
                'div': away_team.div,
                'game_id': game['id'],
                'date': game['date'],
                'external_link': game.get('external_link'),
                'home_team_id': home_team.id,
                'home_team_name': home_team.name,
                'home_team_div': home_team.div,
                'home_team_schedule_url': home_team.schedule.url if home_team.schedule else None,
                'home_team_sport': home_team.sport,
                'home_team_source': home_team.source,
                'away_team_id': away_team.id,
                'away_team_name': away_team.name,
                'away_team_div': away_team.div,
                'away_team_schedule_url': away_team.schedule.url if away_team.schedule else None,
                'away_team_sport': away_team.sport,
                'away_team_source': away_team.source,
                'home_score': result['points_for'] if result and 'points_for' in result else None,
                'away_score': result['points_against'] if result and 'points_against' in result else None,
            })
    
    rows.sort(key=lambda r: (r['game_id'], r['div']))
    write_parquet(rows, year_dir / 'game-metadata.parquet',
                       sort_order=[('game_id', 'ascending'), ('div', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to game-metadata.parquet')


def export_game_boxscores(games: List[dict], year_dir: pathlib.Path):
    """
    File: game-boxscores.parquet
    Sort: (game_id ASC, team_id ASC, points DESC)
    Query: SELECT * FROM game_boxscores WHERE game_id = ? ORDER BY team_id, (g + a) DESC
    """
    rows = []
    
    for game in games:
        home_team = game['home_team']
        away_team = game['away_team']
        
        # Home team stats
        for stat in game.get('home_stats') or []:
            points = stat['g'] + stat['a']
            player = stat['player']
            rows.append({
                'game_id': game['id'],
                'team_id': home_team['id'],
                'points_desc': -points,  # Negative for DESC sort in ASC parquet
                'player_id': player['id'],
                'player_name': player['name'],
                'number': stat.get('number'),
                'position': stat.get('position'),
                'g': stat['g'],
                'a': stat['a'],
                'gb': stat.get('gb'),
                'face_offs_won': stat['face_offs']['won'] if stat.get('face_offs') else None,
                'face_offs_lost': stat['face_offs']['lost'] if stat.get('face_offs') else None,
            })
        
        # Away team stats
        for stat in game.get('away_stats') or []:
            points = stat['g'] + stat['a']
            player = stat['player']
            rows.append({
                'game_id': game['id'],
                'team_id': away_team['id'],
                'points_desc': -points,
                'player_id': player['id'],
                'player_name': player['name'],
                'number': stat.get('number'),
                'position': stat.get('position'),
                'g': stat['g'],
                'a': stat['a'],
                'gb': stat.get('gb'),
                'face_offs_won': stat['face_offs']['won'] if stat.get('face_offs') else None,
                'face_offs_lost': stat['face_offs']['lost'] if stat.get('face_offs') else None,
            })
    
    rows.sort(key=lambda r: (r['game_id'], r['team_id'], r['points_desc']))
    write_parquet(rows, year_dir / 'game-boxscores.parquet',
                       sort_order=[('game_id', 'ascending'), ('team_id', 'ascending'), ('points_desc', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to game-boxscores.parquet')
