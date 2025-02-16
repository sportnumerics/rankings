import unittest

from ..shared.types import GameResult, GameStatLine, Location, PlayerSummary, ScheduleGame, ScheduleGameResult, Team, TeamSummary, TeamDetail
from . import ncaa
from . import fixtures


class TestScrape(unittest.TestCase):
    maxDiff = None

    def test_ncaa_urls(self):
        n = ncaa.Ncaa(['MLA'], ['1', '2'])
        urls = list(n.get_team_list_urls('2020'))
        self.assertEqual(
            urls[0].url,
            'https://stats.ncaa.org/team/inst_team_list?academic_year=2020&division=1&sport_code=MLA'
        )
        self.assertEqual(
            urls[1].url,
            'https://stats.ncaa.org/team/inst_team_list?academic_year=2020&division=2&sport_code=MLA'
        )

    def test_ncaa_team_list_html(self):
        html = fixtures.ncaa_team_list()
        n = ncaa.Ncaa()
        team_list = list(
            n.convert_team_list_html(html, '2023',
                                     next(n.get_team_list_urls('2023'))))
        self.assertEqual(len(team_list), 77)
        self.assertEqual(
            team_list[0],
            Team(name='Air Force',
                 schedule=Location(url='https://stats.ncaa.org/teams/594020'),
                 year='2023',
                 id='ml-ncaa-air-force',
                 div='ml1',
                 sport='ml',
                 source='ncaa'))

    def test_ncaa_team_schedule_html(self):
        html = fixtures.ncaa_game_by_game()
        n = ncaa.Ncaa()
        team = Team(
            name='Air Force',
            schedule=Location(url='https://stats.ncaa.org/teams/594020'),
            year=2023,
            id='ml-ncaa-air-force',
            div='ml1',
            sport='ml',
            source='ncaa')
        games = n.convert_schedule_html(html, team)
        self.assertEqual(
            games[0],
            ScheduleGame(
                id='ml-ncaa-6310104',
                date='2025-02-01',
                opponent=TeamSummary(name='Lafayette', id='ml-ncaa-lafayette'),
                home=False,
                result=ScheduleGameResult(points_for=8, points_against=11),
                source='ncaa',
                sport='ml',
                details=Location(
                    url=
                    'https://stats.ncaa.org/contests/6310104/individual_stats')
            ))
        self.assertEqual(list(map(lambda g: g.opponent.name, games)), [
            'Lafayette', 'Denver', 'Ohio St.', 'Boston U.', 'Quinnipiac',
            'Marist', 'Duke', 'Marquette', 'Jacksonville', 'Bellarmine',
            'Queens (NC)', 'Mercer', 'Utah'
        ])

    def test_ncaa_game_details(self):
        html = fixtures.ncaa_game_details()
        n = ncaa.Ncaa()
        home_team = Team(
            name='Duke',
            id='ml-ncaa-193',
            schedule=Location(
                url=
                'https://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=16320&org_id=721&stats_player_seq=-100'
            ),
            div='ml1',
            year='2024',
            sport='ml',
            source='ncaa')
        away_team = Team(
            name='Air Force',
            id='ml-ncaa-721',
            schedule=Location(
                url=
                'https://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=16320&org_id=721&stats_player_seq=-100'
            ),
            div='ml1',
            year='2024',
            sport='ml',
            source='ncaa')
        game_details = n.convert_game_details_html(
            html,
            Location(
                url='https://stats.ncaa.org/contests/6310104/individual_stats'
            ), 'ml-ncaa-6310104', 'ml', 'ncaa', home_team, away_team)
        self.assertEqual(game_details.date, '2025-02-01')
        self.assertEqual(game_details.id, 'ml-ncaa-6310104')
        self.assertEqual(
            game_details.external_link,
            'https://stats.ncaa.org/contests/6310104/individual_stats')
        self.assertEqual(game_details.home_team, home_team)
        self.assertEqual(game_details.away_team, away_team)
        self.assertEqual(game_details.result,
                         GameResult(home_score=11, away_score=8))
        self.assertEqual(len(game_details.home_stats), 29)
        self.assertEqual(
            game_details.home_stats[0],
            GameStatLine(player=PlayerSummary(
                name='Nicholas Blalock',
                id='ml-ncaa-9099631',
                external_link='https://stats.ncaa.org/players/9099631'),
                         position='A',
                         gb=1,
                         g=1,
                         a=1,
                         number=14))
        self.assertEqual(len(game_details.away_stats), 27)
        self.assertEqual(
            game_details.away_stats[0],
            GameStatLine(player=PlayerSummary(
                name='Connor Albertson',
                id='ml-ncaa-8765561',
                external_link='https://stats.ncaa.org/players/8765561'),
                         position='D',
                         gb=1,
                         g=0,
                         a=0,
                         number=24))

    def test_cross_linking(self):
        n = ncaa.Ncaa()
        schedules = [
            TeamDetail(team=Team(id='ml-ncaa-1',
                                 name='team 1',
                                 alt_id='alt1',
                                 schedule=Location(url='https://schedule/1'),
                                 year='2024',
                                 div='ml1',
                                 sport='ml',
                                 source='ncaa'),
                       games=[
                           ScheduleGame(date='2024-01-31',
                                        sport='ml',
                                        source='ncaa',
                                        home=False,
                                        opponent=TeamSummary(name='team 2',
                                                             alt_id='alt2'))
                       ]),
            TeamDetail(team=Team(id='ml-ncaa-2',
                                 name='team 2',
                                 alt_id='alt2',
                                 schedule=Location(url='https://schedule/2'),
                                 year='2024',
                                 div='ml1',
                                 sport='ml',
                                 source='ncaa'),
                       games=[
                           ScheduleGame(date='2024-01-31',
                                        sport='ml',
                                        source='ncaa',
                                        home=True,
                                        opponent=TeamSummary(name='team 1',
                                                             alt_id='alt1'))
                       ])
        ]
        n.cross_link_schedules(schedules)
        self.assertEqual(schedules[0].games[0].opponent.id, 'ml-ncaa-2')
        self.assertEqual(schedules[1].games[0].opponent.id, 'ml-ncaa-1')
