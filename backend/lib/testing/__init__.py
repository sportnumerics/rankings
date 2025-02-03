from lib.shared.types import ScheduleGame, ScheduleGameResult, Team, TeamDetail, TeamSummary


def create_team(team_id,
                name=None,
                sport='ml',
                source='mcla',
                div='1',
                year=2020) -> Team:
    if not name:
        name = team_id
    return Team(name=name,
                schedule=f'https://example.com/{team_id}',
                year=year,
                id=team_id,
                div=div,
                sport=sport,
                source=source)


def create_schedule(team: Team, games: list[ScheduleGame]) -> TeamDetail:
    return TeamDetail(team=team, games=games)


def home_game(opponent_id, result):
    return create_game(opponent_id, result, home=True)


def away_game(opponent_id, result):
    return create_game(opponent_id, result, home=False)


def create_game(opponent_id, result=None, home=False) -> ScheduleGame:
    game = ScheduleGame(
        date='2020-01-31T13:00:00',
        opponent=TeamSummary(name=opponent_id, id=opponent_id),
        sport='sport',
        source='source',
        home=home,
    )
    if result:
        game.result = ScheduleGameResult(points_for=result[0],
                                         points_against=result[1])
    return game


def create_rating(team_id, ratings):
    overall, offense, defense = ratings
    return {
        'team': team_id,
        'overall': overall,
        'offense': offense,
        'defense': defense
    }
