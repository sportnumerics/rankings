import os
import json
import pathlib
import logging
import numpy as np
from ..shared import shared
from scipy.sparse import coo_matrix
from scipy.sparse import linalg
from dataclasses import dataclass

LOGGER = logging.getLogger(__name__)


def predict(args):
    out_dir = args.out_dir
    for year in shared.years(args.year):
        schedules_dir = os.path.join(args.input_dir, year, 'schedules')
        _, _, filenames = next(os.walk(schedules_dir))

        schedules = list(
            load_from_files(
                map(lambda f: os.path.join(schedules_dir, f), filenames)))

        LOGGER.info(
            f'Calculating team ratings for {len(schedules)} teams in {year}')
        ratings, _ = calculate_ratings(schedules)

        sorted_ratings = sorted(ratings.values(), key=lambda r: -r['overall'])

        pathlib.Path(os.path.join(out_dir, year)).mkdir(parents=True,
                                                        exist_ok=True)
        with open(os.path.join(out_dir, year, 'team-ratings.json'), 'w') as f:
            json.dump(sorted_ratings, f, indent=2)

        rank_players(args, schedules)


def rank_players(args, schedules):
    out_dir = args.out_dir
    year = args.year

    games_dir = os.path.join(args.input_dir, year, 'games')
    _, _, filenames = next(os.walk(games_dir))

    games = list(
        load_from_files(map(lambda f: os.path.join(games_dir, f), filenames)))

    teams_by_id = {}
    for schedule in schedules:
        teams_by_id[schedule['team']['id']] = schedule['team']

    players = {}

    def add_player_stats(entry, team, opponent, game_id, date):
        player_id = entry['player']['id']
        if player_id not in players:
            player = {
                'id': player_id,
                'name': entry['player']['name'],
                'team': teams_by_id.get(team['id'], team),
                'stats': [],
                'external_link': entry['player']['external_link']
            }
            players[player_id] = player
        else:
            player = players[player_id]

        line = {
            'game_id': game_id,
            'date': date,
            'opponent': teams_by_id.get(opponent['id'], opponent),
            'g': entry['g'] if 'g' in entry else 0,
            'a': entry['a'] if 'a' in entry else 0,
            'gb': entry['gb'] if 'gb' in entry else 0
        }
        if 'face_offs' in entry:
            line['face_offs'] = entry['face_offs']
        if 'position' in entry:
            player['position'] = entry['position']
        player['stats'].append(line)
        player['stats'].sort(key=lambda x: x['date'])

    for game in games:
        for entry in game.get('home_stats', []):
            add_player_stats(entry, game['home_team'], game['away_team'],
                             game['id'], game['date'])
        for entry in game.get('away_stats', []):
            add_player_stats(entry, game['away_team'], game['home_team'],
                             game['id'], game['date'])

    LOGGER.info(
        f'Calculating player ratings for {len(players)} players from {len(games)} games in {year}'
    )

    # To get a player ranking we can have pts / assists / goals ranking
    # lets start with pts
    # basically, we'll say each team has a defensive rating
    # and each player has a pts rating
    # we minimize
    # Player_rating - Defense_rating = Points_actual
    # this isn't quite good enough though - the issue is that most players don't score any points
    # so the defensive rating is forced very close to zero
    # we possibly need another factor to represent the rest of the team
    # a very good player does not play independently of his/her team
    # so possibly it should be
    # Player_rating + Offense_rating - Defense_rating = Points_actual
    player_id_to_idx, player_idx_to_id = index_ids([
        entry['player']['id'] for game in games
        for stats in [game.get('home_stats', []),
                      game.get('away_stats', [])] for entry in stats
    ])
    team_id_to_idx, team_idx_to_id = index_ids([
        id for game in games
        for id in [game['away_team']['id'], game['home_team']['id']]
    ])

    data = []
    i = []
    j = []
    constants = []
    n_players = len(player_id_to_idx)
    n_teams = len(team_id_to_idx)

    def get_coefficients(stats):
        for (player, team, opponent, pts) in stats:
            yield ([1, 1, -1], [
                player_id_to_idx[player], n_players + team_id_to_idx[team],
                n_players + n_teams + team_id_to_idx[opponent]
            ], pts)

    def get_ratings(stat):
        for game in games:
            for d, jx, c in get_coefficients([
                (entry['player']['id'], game['home_team']['id'],
                 game['away_team']['id'], stat(entry))
                    for entry in game.get('home_stats', [])
            ]):
                data.extend(d)
                i.extend([len(constants)] * len(jx))
                j.extend(jx)
                constants.append(c)
            for d, jx, c in get_coefficients([
                (entry['player']['id'], game['away_team']['id'],
                 game['home_team']['id'], stat(entry))
                    for entry in game.get('away_stats', [])
            ]):
                data.extend(d)
                i.extend([len(constants)] * len(jx))
                j.extend(jx)
                constants.append(c)

        coefficients = coo_matrix(
            (data, (i, j)), shape=(len(constants), n_players + 2 * n_teams))

        ratings, _, _, _, _, _, _, _, _, _ = linalg.lsqr(coefficients,
                                                         constants,
                                                         damp=1.0)

        min_rating = min(ratings)
        # normalize by subtracting min rating from player ratings
        ratings[0:n_players] -= min_rating
        # and adding min rating to defensive ratings
        ratings[n_players + n_teams:] += min_rating

        return ratings

    goal_ratings = get_ratings(lambda e: e['g'])
    assist_ratings = get_ratings(lambda e: e['a'])

    player_ratings = []
    for i in range(0, n_players):
        player_id = player_idx_to_id[i]
        player = players[player_id]
        player_ratings.append({
            'id': player['id'],
            'name': player['name'],
            'team': player['team'],
            'points': goal_ratings[i] + assist_ratings[i],
            'goals': goal_ratings[i],
            'assists': assist_ratings[i]
        })

    teams = []
    for i in range(0, n_teams):
        team = team_idx_to_id[i]
        teams.append({
            'team': team,
            'goals_off': goal_ratings[n_players + i],
            'goals_def': goal_ratings[n_players + n_teams + i],
            'assists_off': assist_ratings[n_players + i],
            'assists_def': assist_ratings[n_players + n_teams + i]
        })

    sorted_players = sorted(player_ratings, key=lambda r: -r['points'])
    sorted_teams = sorted(teams,
                          key=lambda r: -r['goals_def'] - r['assists_def'])

    pathlib.Path(os.path.join(out_dir, year)).mkdir(parents=True,
                                                    exist_ok=True)
    with open(os.path.join(out_dir, year, 'player-ratings.json'), 'w') as f:
        json.dump(sorted_players, f, indent=2)

    with open(os.path.join(out_dir, year, 'team-player-ratings.json'),
              'w') as f:
        json.dump(sorted_teams, f, indent=2)

    pathlib.Path(os.path.join(out_dir, year, 'players')).mkdir(parents=True,
                                                               exist_ok=True)
    for player in players.values():
        with open(
                os.path.join(out_dir, year, 'players', player['id'] + '.json'),
                'w') as f:
            json.dump(player, f, indent=2)


def index_ids(ids):
    id_to_idx = {}
    idx_to_id = {}
    for i, id in enumerate(set(ids)):
        id_to_idx[id] = i
        idx_to_id[i] = id
    return id_to_idx, idx_to_id


def load_from_files(filenames):
    for file in filenames:
        with open(file) as f:
            yield json.load(f)


def calculate_ratings(schedules):
    game_map = {}
    for schedule in schedules:
        for game in schedule['games']:
            if 'result' not in game:
                continue
            team_id = schedule['team']['id']
            opponent_id = game['opponent']['id']
            gid = game_id(team_id, opponent_id, game['date'])
            g = {
                'team': team_id,
                'opponent': opponent_id,
                'home': game['home'],
                'points_for': game['result']['points_for'],
                'points_against': game['result']['points_against']
            }
            game_map[gid] = g

    games = game_map.values()

    team_groups = group_teams_by_games(games)

    id_to_idx, idx_to_id = index_ids(
        [id for game in games for id in [game['opponent'], game['team']]])
    n_teams = len(idx_to_id)
    offset = len(id_to_idx)

    coefficients = build_offensive_defensive_coefficient_matrix(
        games, id_to_idx)

    constants = build_offensive_defensive_constants(games)

    raw_ratings, _, _, _, _, _, _, _, _, _ = linalg.lsqr(coefficients,
                                                         constants,
                                                         damp=0.2)

    overall = raw_ratings[0:n_teams] + raw_ratings[offset:n_teams + offset]
    hfa = raw_ratings[2 * n_teams]

    results = {}
    for i in range(0, n_teams):
        team = idx_to_id[i]
        results[team] = {
            'team': team,
            'offense': raw_ratings[i],
            'defense': raw_ratings[i + offset],
            'overall': overall[i],
            'group': group_for_team(team_groups, team).id
        }

    return results, hfa


def build_team_map(games):
    ids_to_indicies = {}
    indicies_to_teams = {}

    def add_team_if_necessary(team_id):
        if (team_id not in ids_to_indicies):
            index = len(indicies_to_teams)
            ids_to_indicies[team_id] = index
            indicies_to_teams[index] = team_id

    for game in games:
        team_id = game['team']
        opponent_id = game['opponent']
        add_team_if_necessary(team_id)
        add_team_if_necessary(opponent_id)

    return {
        'ids_to_indicies': ids_to_indicies,
        'indicies_to_teams': indicies_to_teams
    }


def build_offensive_defensive_coefficient_matrix(games, id_to_idx):
    hfa_factors = [
        hfa for g in games for hfa in ((1, -1) if g['home'] else (-1, 1))
    ]
    hfa_i = [i for i in range(0, 2 * len(games))]
    hfa_j = [2 * len(id_to_idx)] * (2 * len(games))

    data = [1, -1, 1, -1] * len(games)
    i = [i for g in range(0, 2 * len(games)) for i in (g, g)]

    def offensive_offset(id):
        return id_to_idx[id]

    def defensive_offset(id):
        return len(id_to_idx) + id_to_idx[id]

    j = [
        k for game in games for k in (offensive_offset(game['team']),
                                      defensive_offset(game['opponent']),
                                      offensive_offset(game['opponent']),
                                      defensive_offset(game['team']))
    ]

    return coo_matrix((data + hfa_factors, (i + hfa_i, j + hfa_j)),
                      shape=(2 * len(games), 2 * len(id_to_idx) + 1))


def build_offensive_defensive_constants(games):
    return np.array(
        [p for g in games for p in (g['points_for'], g['points_against'])])


def game_id(team_id, opponent_id, date):
    if team_id < opponent_id:
        return f'{team_id}_{opponent_id}_{date}'
    else:
        return f'{opponent_id}_{team_id}_{date}'


@dataclass
class Group:
    id: str
    games: list
    team_ids: set[str]


def group_teams_by_games(games):
    groups = []

    idx = 0
    for game in games:
        team_id = game['team']
        opponent_id = game['opponent']
        team_group = group_for_team(groups, team_id)
        opponent_group = group_for_team(groups, opponent_id)
        if (team_group is None and opponent_group is None):
            groups.append(Group(
                id=idx,
                games=[game],
                team_ids=set([team_id, opponent_id])))
            idx += 1
        elif (team_group is None):
            opponent_group.games.append(game)
            opponent_group.team_ids.add(team_id)
        elif (opponent_group is None):
            team_group.games.append(game)
            team_group.team_ids.add(opponent_id)
        elif (team_group == opponent_group):
            team_group.games.append(game)
        else:
            groups.remove(opponent_group)
            team_group.games.append(game)
            team_group.games.extend(opponent_group.games)
            team_group.team_ids.update(opponent_group.team_ids)

    return groups


def group_for_team(groups: list[Group], team_id: str):
    for group in groups:
        if team_id in group.team_ids:
            return group
    return None
