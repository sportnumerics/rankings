#!/usr/bin/env python3
import argparse
import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from lib.predict.predict import (PlayerRatingObservation, calculate_ratings,
                                 solve_player_ratings)
from lib.shared.types import (
    Game,
    Location,
    ScheduleGame,
    ScheduleGameResult,
    Team,
    TeamDetail,
    TeamRating,
    TeamSummary,
)


@dataclass
class TeamGame:
    day: date
    home_team: str
    away_team: str
    home_div: str
    sport: str
    home_score: int
    away_score: int


@dataclass
class TeamModel:
    ratings: Dict[str, TeamRating]
    hfa: float


@dataclass
class PlayerObs:
    day: date
    player_id: str
    team_id: str
    opp_id: str
    goals: int
    assists: int


@dataclass
class PlayerModel:
    player_to_idx: Dict[str, int]
    team_to_idx: Dict[str, int]
    goal_ratings: np.ndarray
    assist_ratings: np.ndarray


def parse_day(date_str: str) -> date:
    # date strings are either YYYY-MM-DD or ISO with timezone
    return date.fromisoformat(date_str[:10])


def _deserialize_game(payload: dict, fallback_id: str) -> Game:
    # Production game shape (preferred)
    if 'home_team' in payload and 'away_team' in payload:
        return Game.from_dict(payload)

    # Legacy shape fallback
    home_id = payload.get('homeTeamId')
    away_id = payload.get('awayTeamId')
    result = payload.get('result')

    game_dict = {
        'id': payload.get('id') or fallback_id,
        'external_link': payload.get('external_link') or '',
        'date': payload['date'],
        'home_team': {
            'id': home_id,
            'name': home_id,
        },
        'away_team': {
            'id': away_id,
            'name': away_id,
        },
        'result': {
            'home_score': int(result['points_for']) if result else 0,
            'away_score': int(result['points_against']) if result else 0,
        } if result else None,
    }
    return Game.from_dict(game_dict)


def load_games(games_json_path: Path, games_dir: Path) -> List[Game]:
    games: List[Game] = []

    if games_dir.exists():
        for idx, file in enumerate(sorted(games_dir.glob('*.json'))):
            raw = json.loads(file.read_text())
            game = _deserialize_game(raw, fallback_id=f'file-{idx}')
            if game.result is None:
                continue
            games.append(game)
    elif games_json_path.exists():
        raw = json.loads(games_json_path.read_text())
        idx = 0
        for _, schedule_games in raw.items():
            for g in schedule_games:
                result = g.get('result')
                if not result:
                    continue
                game = _deserialize_game(g, fallback_id=f'legacy-{idx}')
                idx += 1
                if game.result is None:
                    continue
                games.append(game)
    else:
        raise FileNotFoundError(f'No games source found at {games_json_path} or {games_dir}')

    games.sort(key=lambda g: parse_day(g.date))
    return games


def load_team_games(games: List[Game]) -> List[TeamGame]:
    rows: List[TeamGame] = []
    for g in games:
        if not g.result:
            continue
        rows.append(
            TeamGame(
                day=parse_day(g.date),
                home_team=g.home_team.id,
                away_team=g.away_team.id,
                home_div='unknown',
                sport='ml',
                home_score=int(g.result.home_score),
                away_score=int(g.result.away_score),
            ))
    rows.sort(key=lambda x: x.day)
    return rows


def _stub_team(team_id: str) -> Team:
    return Team(
        name=team_id,
        schedule=Location(url=''),
        year='unknown',
        id=team_id,
        div='unknown',
        sport='ml',
        source='backtest',
    )


def fit_team_model(games: List[TeamGame]) -> TeamModel | None:
    if not games:
        return None

    schedules_by_team: Dict[str, TeamDetail] = {}

    def schedule_for(team_id: str):
        if team_id not in schedules_by_team:
            schedules_by_team[team_id] = TeamDetail(team=_stub_team(team_id), games=[])
        return schedules_by_team[team_id]

    for g in games:
        schedule_for(g.home_team).games.append(
            ScheduleGame(
                date=g.day.isoformat(),
                opponent=TeamSummary(name=g.away_team, id=g.away_team),
                sport=g.sport,
                source='backtest',
                home=True,
                result=ScheduleGameResult(points_for=g.home_score, points_against=g.away_score),
            ))
        schedule_for(g.away_team).games.append(
            ScheduleGame(
                date=g.day.isoformat(),
                opponent=TeamSummary(name=g.home_team, id=g.home_team),
                sport=g.sport,
                source='backtest',
                home=False,
                result=ScheduleGameResult(points_for=g.away_score, points_against=g.home_score),
            ))

    ratings, hfa = calculate_ratings(schedules_by_team.values())
    if not ratings:
        return None
    return TeamModel(ratings=ratings, hfa=float(hfa))


def predict_team_scores(model: TeamModel, home_team: str, away_team: str) -> Tuple[float, float] | None:
    home = model.ratings.get(home_team)
    away = model.ratings.get(away_team)
    if not home or not away:
        return None
    home_pred = home.offense - away.defense + model.hfa
    away_pred = away.offense - home.defense - model.hfa
    return float(home_pred), float(away_pred)


def run_team_backtest(games: List[TeamGame], min_train_games: int = 50):
    by_day: Dict[date, List[TeamGame]] = defaultdict(list)
    for g in games:
        by_day[g.day].append(g)

    all_days = sorted(by_day.keys())
    train_pool: List[TeamGame] = []

    abs_err_margin = []
    abs_err_home = []
    winner_hits = 0
    winner_total = 0

    baseline_hits = 0
    baseline_total = 0

    for d in all_days:
        test_games = by_day[d]
        if len(train_pool) >= min_train_games:
            model = fit_team_model(train_pool)
            if model:
                for g in test_games:
                    pred = predict_team_scores(model, g.home_team, g.away_team)
                    if pred is None:
                        continue
                    ph, pa = pred
                    actual_margin = g.home_score - g.away_score
                    pred_margin = ph - pa
                    abs_err_margin.append(abs(pred_margin - actual_margin))
                    abs_err_home.append(abs(ph - g.home_score))
                    winner_hits += int((pred_margin > 0) == (actual_margin > 0))
                    winner_total += 1

                    baseline_hits += int(actual_margin > 0)  # always pick home team
                    baseline_total += 1

        train_pool.extend(test_games)

    return {
        'samples': winner_total,
        'mae_margin': float(np.mean(abs_err_margin)) if abs_err_margin else None,
        'mae_home_score': float(np.mean(abs_err_home)) if abs_err_home else None,
        'winner_accuracy': (winner_hits / winner_total) if winner_total else None,
        'home_baseline_accuracy': (baseline_hits / baseline_total) if baseline_total else None,
    }


def load_player_obs(games: List[Game]) -> List[PlayerObs]:
    obs: List[PlayerObs] = []
    for g in games:
        if not g.home_stats or not g.away_stats:
            continue
        d = parse_day(g.date)
        home = g.home_team.id
        away = g.away_team.id

        for line in g.home_stats:
            pid = line.player.id if line.player else None
            if not pid:
                continue
            obs.append(PlayerObs(d, pid, home, away, int(line.g), int(line.a)))

        for line in g.away_stats:
            pid = line.player.id if line.player else None
            if not pid:
                continue
            obs.append(PlayerObs(d, pid, away, home, int(line.g), int(line.a)))

    obs.sort(key=lambda x: x.day)
    return obs


def fit_player_model(obs: List[PlayerObs], damp: float = 1.0) -> PlayerModel | None:
    if not obs:
        return None
    players = sorted({o.player_id for o in obs})
    teams = sorted({o.team_id for o in obs} | {o.opp_id for o in obs})
    if len(players) < 10 or len(teams) < 2:
        return None

    p_idx = {p: i for i, p in enumerate(players)}
    t_idx = {t: i for i, t in enumerate(teams)}

    goal_obs = [
        PlayerRatingObservation(player=o.player_id,
                                team=o.team_id,
                                opponent=o.opp_id,
                                value=float(o.goals)) for o in obs
    ]
    assist_obs = [
        PlayerRatingObservation(player=o.player_id,
                                team=o.team_id,
                                opponent=o.opp_id,
                                value=float(o.assists)) for o in obs
    ]

    g_r = solve_player_ratings(goal_obs, p_idx, t_idx, damp=damp, normalize=False)
    a_r = solve_player_ratings(assist_obs, p_idx, t_idx, damp=damp, normalize=False)

    return PlayerModel(player_to_idx=p_idx, team_to_idx=t_idx, goal_ratings=g_r, assist_ratings=a_r)


def predict_player_points(model: PlayerModel, player_id: str, team_id: str, opp_id: str) -> float | None:
    if player_id not in model.player_to_idx or team_id not in model.team_to_idx or opp_id not in model.team_to_idx:
        return None
    p = model.player_to_idx[player_id]
    t = model.team_to_idx[team_id]
    o = model.team_to_idx[opp_id]
    n_p = len(model.player_to_idx)
    n_t = len(model.team_to_idx)
    pred_goals = model.goal_ratings[p] + model.goal_ratings[n_p + t] - model.goal_ratings[n_p + n_t + o]
    pred_assists = model.assist_ratings[p] + model.assist_ratings[n_p + t] - model.assist_ratings[n_p + n_t + o]
    return float(pred_goals + pred_assists)


def run_player_backtest(obs: List[PlayerObs], start_train_days: int = 21, step_days: int = 7):
    if not obs:
        return {'samples': 0}

    by_day: Dict[date, List[PlayerObs]] = defaultdict(list)
    for o in obs:
        by_day[o.day].append(o)
    days = sorted(by_day.keys())

    train_end = days[0] + timedelta(days=start_train_days)

    abs_err = []
    within_one = 0
    total = 0

    while train_end < days[-1]:
        train = [o for d in days if d < train_end for o in by_day[d]]
        test_days = [d for d in days if train_end <= d < train_end + timedelta(days=step_days)]
        test = [o for d in test_days for o in by_day[d]]
        if len(train) < 500 or len(test) < 50:
            train_end += timedelta(days=step_days)
            continue
        model = fit_player_model(train)
        if not model:
            train_end += timedelta(days=step_days)
            continue

        for o in test:
            pred = predict_player_points(model, o.player_id, o.team_id, o.opp_id)
            if pred is None:
                continue
            actual = o.goals + o.assists
            err = abs(pred - actual)
            abs_err.append(err)
            within_one += int(err <= 1.0)
            total += 1

        train_end += timedelta(days=step_days)

    return {
        'samples': total,
        'mae_points': float(np.mean(abs_err)) if abs_err else None,
        'within_1_point': (within_one / total) if total else None,
    }


def main():
    p = argparse.ArgumentParser(description='Backtest current team/player models')
    p.add_argument('--data-dir', required=True, help='Local synced data root (e.g. /tmp/sportnumerics-prod-data)')
    p.add_argument('--year', required=True, help='Season year (e.g. 2025)')
    args = p.parse_args()

    data_dir = Path(args.data_dir) / args.year
    games_json = data_dir / 'games.json'
    games_dir = data_dir / 'games'

    games = load_games(games_json, games_dir)

    team_games = load_team_games(games)
    team_metrics = run_team_backtest(team_games)

    player_obs = load_player_obs(games)
    player_metrics = run_player_backtest(player_obs)

    report = {
        'year': args.year,
        'team_backtest': team_metrics,
        'player_backtest': player_metrics,
        'notes': [
            'Team model is strict walk-forward daily fit on prior completed games.',
            'Player model is walk-forward weekly refit using goals+assists per player-game line.',
            'Metrics are baseline for current model form; use to compare future changes.',
        ],
    }

    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    main()
