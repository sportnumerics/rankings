"""
Export optimized parquet files for frontend queries.

Generates 12 materialized view files, each optimized for a specific page/component.
"""

import logging
import os
import pathlib
from typing import Iterable, List
from dataclasses import asdict

from ..shared.types import (
    Game, Player, PlayerRating, TeamDetail, TeamRating
)
from ..shared import shared

LOGGER = logging.getLogger(__name__)


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
        team_ratings = load_team_ratings(args.input_dir, year)
        player_ratings = load_player_ratings(args.input_dir, year)
        schedules = load_schedules(args.input_dir, year)
        games = load_games(args.input_dir, year)
        players = load_players(args.input_dir, year)
        
        # Create output directory
        year_dir = pathlib.Path(os.path.join(out_dir, year))
        year_dir.mkdir(parents=True, exist_ok=True)
        
        # Export each materialized view
        export_teams_list(team_ratings, schedules, year_dir)
        export_team_metadata(team_ratings, schedules, year_dir)
        export_team_schedules(schedules, year_dir)
        export_team_rosters(players, player_ratings, year_dir)
        
        export_players_list(players, player_ratings, year_dir)
        export_player_metadata(players, player_ratings, year_dir)
        export_player_gamelogs(players, year_dir)
        export_goals_leaders(players, player_ratings, year_dir)
        export_assists_leaders(players, player_ratings, year_dir)
        
        export_games_list(games, year_dir)
        export_game_metadata(games, year_dir)
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


def load_games(input_dir: str, year: str) -> List[Game]:
    """Load games with stats."""
    path = shared.parquet_path(input_dir, year, 'games')
    if not os.path.exists(path):
        LOGGER.warning(f'No games data found at {path}')
        return []
    return list(shared.load_parquet_dataset(Game, path))


def load_players(input_dir: str, year: str) -> dict[str, Player]:
    """Load full player data indexed by player id."""
    path = shared.parquet_path(input_dir, year, 'players', 'data.parquet')
    if not os.path.exists(path):
        LOGGER.warning(f'No players data found at {path}')
        return {}
    players = list(shared.load_parquet_dataset(Player, path))
    return {p.id: p for p in players}


# --- Teams Pages ---

def export_teams_list(team_ratings: dict[str, TeamRating], 
                      schedules: List[TeamDetail],
                      year_dir: pathlib.Path):
    """
    File: teams-list.parquet
    Sort: (div ASC, rank ASC)
    Query: SELECT * FROM teams_list WHERE div = ? ORDER BY rank
    """
    rows = []
    
    # Build map of team_id -> TeamDetail for metadata
    team_details = {s.team.id: s.team for s in schedules}
    
    # Calculate ranks within each division
    teams_by_div = {}
    for team_id, rating in team_ratings.items():
        detail = team_details.get(team_id)
        if not detail:
            continue
        div = detail.div
        if div not in teams_by_div:
            teams_by_div[div] = []
        teams_by_div[div].append((team_id, rating, detail))
    
    for div, teams in teams_by_div.items():
        # Sort by overall rating desc to assign ranks
        teams.sort(key=lambda t: t[1].overall, reverse=True)
        for rank, (team_id, rating, detail) in enumerate(teams, start=1):
            rows.append({
                'div': div,
                'rank': rank,
                'id': team_id,
                'name': detail.name,
                'sport': detail.sport,
                'source': detail.source,
                'schedule_url': detail.schedule_url,
                'offense': rating.offense,
                'defense': rating.defense,
                'overall': rating.overall,
            })
    
    rows.sort(key=lambda r: (r['div'], r['rank']))
    shared.dump_parquet(rows, year_dir / 'teams-list.parquet',
                       sort_order=[('div', 'ascending'), ('rank', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to teams-list.parquet')


def export_team_metadata(team_ratings: dict[str, TeamRating],
                         schedules: List[TeamDetail],
                         year_dir: pathlib.Path):
    """
    File: team-metadata.parquet
    Sort: (div ASC, id ASC)
    Query: SELECT * FROM team_metadata WHERE div = ? AND id = ?
    """
    rows = []
    team_details = {s.team.id: s.team for s in schedules}
    
    # Calculate ranks
    teams_by_div = {}
    for team_id, rating in team_ratings.items():
        detail = team_details.get(team_id)
        if not detail:
            continue
        div = detail.div
        if div not in teams_by_div:
            teams_by_div[div] = []
        teams_by_div[div].append((team_id, rating, detail))
    
    for div, teams in teams_by_div.items():
        teams.sort(key=lambda t: t[1].overall, reverse=True)
        for rank, (team_id, rating, detail) in enumerate(teams, start=1):
            rows.append({
                'div': div,
                'id': team_id,
                'name': detail.name,
                'sport': detail.sport,
                'source': detail.source,
                'schedule_url': detail.schedule_url,
                'offense': rating.offense,
                'defense': rating.defense,
                'overall': rating.overall,
                'rank': rank,
            })
    
    rows.sort(key=lambda r: (r['div'], r['id']))
    shared.dump_parquet(rows, year_dir / 'team-metadata.parquet',
                       sort_order=[('div', 'ascending'), ('id', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to team-metadata.parquet')


def export_team_schedules(schedules: List[TeamDetail], year_dir: pathlib.Path):
    """
    File: team-schedules.parquet
    Sort: (div ASC, team_id ASC, date ASC)
    Query: SELECT * FROM team_schedules WHERE div = ? AND team_id = ? ORDER BY date
    """
    rows = []
    
    for schedule in schedules:
        team = schedule.team
        for game in schedule.games:
            rows.append({
                'div': team.div,
                'team_id': team.id,
                'date': game.date,
                'game_id': f"{team.id}_{game.opponent.id}_{game.date}",
                'opponent_id': game.opponent.id or game.opponent.alt_id,
                'opponent_name': game.opponent.name,
                'opponent_div': game.opponent.div,
                'opponent_schedule_url': game.opponent.schedule_url,
                'opponent_sport': game.opponent.sport,
                'opponent_source': game.opponent.source,
                'home': game.home,
                'points_for': game.result.points_for if game.result else None,
                'points_against': game.result.points_against if game.result else None,
                'details_url': game.external_link,
            })
    
    rows.sort(key=lambda r: (r['div'], r['team_id'], r['date']))
    shared.dump_parquet(rows, year_dir / 'team-schedules.parquet',
                       sort_order=[('div', 'ascending'), ('team_id', 'ascending'), ('date', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to team-schedules.parquet')


def export_team_rosters(players: dict[str, Player],
                        player_ratings: dict[str, PlayerRating],
                        year_dir: pathlib.Path):
    """
    File: team-rosters.parquet
    Sort: (div ASC, team_id ASC, number ASC)
    Query: SELECT * FROM team_rosters WHERE div = ? AND team_id = ? ORDER BY number
    """
    rows = []
    
    for player_id, player in players.items():
        rating = player_ratings.get(player_id)
        rows.append({
            'div': player.team.div,
            'team_id': player.team.id,
            'number': player.number or 0,  # Default to 0 for sorting
            'player_id': player.id,
            'player_name': player.name,
            'position': player.position,
            'class_year': player.class_year,
            'eligibility': player.eligibility,
            'height': player.height,
            'weight': player.weight,
            'high_school': player.high_school,
            'hometown': player.hometown,
            'external_link': player.external_link,
            'points': rating.points if rating else 0.0,
            'goals': rating.goals if rating else 0.0,
            'assists': rating.assists if rating else 0.0,
        })
    
    rows.sort(key=lambda r: (r['div'], r['team_id'], r['number']))
    shared.dump_parquet(rows, year_dir / 'team-rosters.parquet',
                       sort_order=[('div', 'ascending'), ('team_id', 'ascending'), ('number', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to team-rosters.parquet')


# --- Players Pages ---

def export_players_list(players: dict[str, Player],
                        player_ratings: dict[str, PlayerRating],
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
        rows.append({
            'div': player.team.div,
            'points': rating.points,
            'player_id': player.id,
            'player_name': player.name,
            'team_id': player.team.id,
            'team_name': player.team.name,
            'team_schedule_url': player.team.schedule_url,
            'team_sport': player.team.sport,
            'team_source': player.team.source,
            'goals': rating.goals,
            'assists': rating.assists,
            'position': player.position,
            'number': player.number,
            'class_year': player.class_year,
        })
    
    rows.sort(key=lambda r: (r['div'], -r['points']))  # DESC points via negative
    shared.dump_parquet(rows, year_dir / 'players-list.parquet',
                       sort_order=[('div', 'ascending'), ('points', 'descending')])
    LOGGER.info(f'Exported {len(rows)} rows to players-list.parquet')


def export_player_metadata(players: dict[str, Player],
                           player_ratings: dict[str, PlayerRating],
                           year_dir: pathlib.Path):
    """
    File: player-metadata.parquet
    Sort: (div ASC, player_id ASC)
    Query: SELECT * FROM player_metadata WHERE div = ? AND player_id = ?
    """
    rows = []
    
    for player_id, player in players.items():
        rating = player_ratings.get(player_id)
        rows.append({
            'div': player.team.div,
            'player_id': player.id,
            'player_name': player.name,
            'team_id': player.team.id,
            'team_name': player.team.name,
            'team_schedule_url': player.team.schedule_url,
            'team_sport': player.team.sport,
            'team_source': player.team.source,
            'points': rating.points if rating else 0.0,
            'goals': rating.goals if rating else 0.0,
            'assists': rating.assists if rating else 0.0,
            'position': player.position,
            'number': player.number,
            'class_year': player.class_year,
            'eligibility': player.eligibility,
            'height': player.height,
            'weight': player.weight,
            'high_school': player.high_school,
            'hometown': player.hometown,
            'external_link': player.external_link,
        })
    
    rows.sort(key=lambda r: (r['div'], r['player_id']))
    shared.dump_parquet(rows, year_dir / 'player-metadata.parquet',
                       sort_order=[('div', 'ascending'), ('player_id', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to player-metadata.parquet')


def export_player_gamelogs(players: dict[str, Player], year_dir: pathlib.Path):
    """
    File: player-gamelogs.parquet
    Sort: (div ASC, player_id ASC, date DESC)
    Query: SELECT * FROM player_gamelogs WHERE div = ? AND player_id = ? ORDER BY date DESC
    """
    rows = []
    
    for player_id, player in players.items():
        for stat in player.stats:
            rows.append({
                'div': player.team.div,
                'player_id': player.id,
                'date': stat.date,
                'game_id': stat.game_id,
                'opponent_id': stat.opponent.id or stat.opponent.alt_id,
                'opponent_name': stat.opponent.name,
                'opponent_div': stat.opponent.div,
                'opponent_schedule_url': stat.opponent.schedule_url,
                'opponent_sport': stat.opponent.sport,
                'opponent_source': stat.opponent.source,
                'g': stat.g,
                'a': stat.a,
                'gb': stat.gb,
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
    
    shared.dump_parquet(sorted_rows, year_dir / 'player-gamelogs.parquet',
                       sort_order=[('div', 'ascending'), ('player_id', 'ascending'), ('date', 'descending')])
    LOGGER.info(f'Exported {len(sorted_rows)} rows to player-gamelogs.parquet')


def export_goals_leaders(players: dict[str, Player],
                         player_ratings: dict[str, PlayerRating],
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
        rows.append({
            'div': player.team.div,
            'goals': rating.goals,
            'player_id': player.id,
            'player_name': player.name,
            'team_id': player.team.id,
            'team_name': player.team.name,
            'team_schedule_url': player.team.schedule_url,
            'team_sport': player.team.sport,
            'team_source': player.team.source,
            'points': rating.points,
            'assists': rating.assists,
            'position': player.position,
            'number': player.number,
            'class_year': player.class_year,
        })
    
    rows.sort(key=lambda r: (r['div'], -r['goals']))
    shared.dump_parquet(rows, year_dir / 'goals-leaders.parquet',
                       sort_order=[('div', 'ascending'), ('goals', 'descending')])
    LOGGER.info(f'Exported {len(rows)} rows to goals-leaders.parquet')


def export_assists_leaders(players: dict[str, Player],
                           player_ratings: dict[str, PlayerRating],
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
        rows.append({
            'div': player.team.div,
            'assists': rating.assists,
            'player_id': player.id,
            'player_name': player.name,
            'team_id': player.team.id,
            'team_name': player.team.name,
            'team_schedule_url': player.team.schedule_url,
            'team_sport': player.team.sport,
            'team_source': player.team.source,
            'points': rating.points,
            'goals': rating.goals,
            'position': player.position,
            'number': player.number,
            'class_year': player.class_year,
        })
    
    rows.sort(key=lambda r: (r['div'], -r['assists']))
    shared.dump_parquet(rows, year_dir / 'assists-leaders.parquet',
                       sort_order=[('div', 'ascending'), ('assists', 'descending')])
    LOGGER.info(f'Exported {len(rows)} rows to assists-leaders.parquet')


# --- Games Pages ---

def export_games_list(games: List[Game], year_dir: pathlib.Path):
    """
    File: games-list.parquet
    Sort: (div ASC, date DESC)
    Query: SELECT * FROM games_list WHERE div = ? ORDER BY date DESC LIMIT 100
    
    Note: Each game appears TWICE (once for each team's division) to enable
    efficient division filtering via row group skipping.
    """
    rows = []
    
    for game in games:
        # Add row for home team's division
        rows.append({
            'div': game.home_team.div,
            'date': game.date,
            'game_id': game.id,
            'external_link': game.external_link,
            'home_team_id': game.home_team.id,
            'home_team_name': game.home_team.name,
            'home_team_div': game.home_team.div,
            'home_team_schedule_url': game.home_team.schedule_url,
            'home_team_sport': game.home_team.sport,
            'home_team_source': game.home_team.source,
            'away_team_id': game.away_team.id,
            'away_team_name': game.away_team.name,
            'away_team_div': game.away_team.div,
            'away_team_schedule_url': game.away_team.schedule_url,
            'away_team_sport': game.away_team.sport,
            'away_team_source': game.away_team.source,
            'home_score': game.home_score,
            'away_score': game.away_score,
        })
        
        # Add row for away team's division (if different)
        if game.away_team.div != game.home_team.div:
            rows.append({
                'div': game.away_team.div,
                'date': game.date,
                'game_id': game.id,
                'external_link': game.external_link,
                'home_team_id': game.home_team.id,
                'home_team_name': game.home_team.name,
                'home_team_div': game.home_team.div,
                'home_team_schedule_url': game.home_team.schedule_url,
                'home_team_sport': game.home_team.sport,
                'home_team_source': game.home_team.source,
                'away_team_id': game.away_team.id,
                'away_team_name': game.away_team.name,
                'away_team_div': game.away_team.div,
                'away_team_schedule_url': game.away_team.schedule_url,
                'away_team_sport': game.away_team.sport,
                'away_team_source': game.away_team.source,
                'home_score': game.home_score,
                'away_score': game.away_score,
            })
    
    rows.sort(key=lambda r: (r['div'], r['date']), reverse=False)
    # Reverse dates within each division
    from itertools import groupby
    sorted_rows = []
    for div, group in groupby(rows, key=lambda r: r['div']):
        group_list = list(group)
        group_list.sort(key=lambda r: r['date'], reverse=True)
        sorted_rows.extend(group_list)
    
    shared.dump_parquet(sorted_rows, year_dir / 'games-list.parquet',
                       sort_order=[('div', 'ascending'), ('date', 'descending')])
    LOGGER.info(f'Exported {len(sorted_rows)} rows to games-list.parquet (includes duplicates for cross-division games)')


def export_game_metadata(games: List[Game], year_dir: pathlib.Path):
    """
    File: game-metadata.parquet
    Sort: (div ASC, game_id ASC)
    Query: SELECT * FROM game_metadata WHERE div = ? AND game_id = ? LIMIT 1
    
    Note: Each game appears TWICE for consistency with games-list.
    """
    rows = []
    
    for game in games:
        # Add row for home team's division
        rows.append({
            'div': game.home_team.div,
            'game_id': game.id,
            'date': game.date,
            'external_link': game.external_link,
            'home_team_id': game.home_team.id,
            'home_team_name': game.home_team.name,
            'home_team_div': game.home_team.div,
            'home_team_schedule_url': game.home_team.schedule_url,
            'home_team_sport': game.home_team.sport,
            'home_team_source': game.home_team.source,
            'away_team_id': game.away_team.id,
            'away_team_name': game.away_team.name,
            'away_team_div': game.away_team.div,
            'away_team_schedule_url': game.away_team.schedule_url,
            'away_team_sport': game.away_team.sport,
            'away_team_source': game.away_team.source,
            'home_score': game.home_score,
            'away_score': game.away_score,
        })
        
        # Add row for away team's division (if different)
        if game.away_team.div != game.home_team.div:
            rows.append({
                'div': game.away_team.div,
                'game_id': game.id,
                'date': game.date,
                'external_link': game.external_link,
                'home_team_id': game.home_team.id,
                'home_team_name': game.home_team.name,
                'home_team_div': game.home_team.div,
                'home_team_schedule_url': game.home_team.schedule_url,
                'home_team_sport': game.home_team.sport,
                'home_team_source': game.home_team.source,
                'away_team_id': game.away_team.id,
                'away_team_name': game.away_team.name,
                'away_team_div': game.away_team.div,
                'away_team_schedule_url': game.away_team.schedule_url,
                'away_team_sport': game.away_team.sport,
                'away_team_source': game.away_team.source,
                'home_score': game.home_score,
                'away_score': game.away_score,
            })
    
    rows.sort(key=lambda r: (r['div'], r['game_id']))
    shared.dump_parquet(rows, year_dir / 'game-metadata.parquet',
                       sort_order=[('div', 'ascending'), ('game_id', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to game-metadata.parquet')


def export_game_boxscores(games: List[Game], year_dir: pathlib.Path):
    """
    File: game-boxscores.parquet
    Sort: (game_id ASC, team_id ASC, points DESC)
    Query: SELECT * FROM game_boxscores WHERE game_id = ? ORDER BY team_id, (g + a) DESC
    """
    rows = []
    
    for game in games:
        # Home team stats
        for stat in game.home_stats or []:
            points = stat.g + stat.a
            rows.append({
                'game_id': game.id,
                'team_id': game.home_team.id,
                'points_desc': -points,  # Negative for DESC sort in ASC parquet
                'player_id': stat.player.id,
                'player_name': stat.player.name,
                'number': stat.number,
                'position': stat.position,
                'g': stat.g,
                'a': stat.a,
                'gb': stat.gb,
                'face_offs_won': stat.face_offs.won if stat.face_offs else None,
                'face_offs_lost': stat.face_offs.lost if stat.face_offs else None,
            })
        
        # Away team stats
        for stat in game.away_stats or []:
            points = stat.g + stat.a
            rows.append({
                'game_id': game.id,
                'team_id': game.away_team.id,
                'points_desc': -points,
                'player_id': stat.player.id,
                'player_name': stat.player.name,
                'number': stat.number,
                'position': stat.position,
                'g': stat.g,
                'a': stat.a,
                'gb': stat.gb,
                'face_offs_won': stat.face_offs.won if stat.face_offs else None,
                'face_offs_lost': stat.face_offs.lost if stat.face_offs else None,
            })
    
    rows.sort(key=lambda r: (r['game_id'], r['team_id'], r['points_desc']))
    shared.dump_parquet(rows, year_dir / 'game-boxscores.parquet',
                       sort_order=[('game_id', 'ascending'), ('team_id', 'ascending'), ('points_desc', 'ascending')])
    LOGGER.info(f'Exported {len(rows)} rows to game-boxscores.parquet')
