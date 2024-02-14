from optparse import OptParseError
import unittest

from .types import GameResult, GameStatLine, Location, PlayerSummary, ScheduleGame, ScheduleGameResult, Team, TeamSummary, TeamDetail
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
        self.assertEqual(len(team_list), 76)
        self.assertEqual(
            team_list[0],
            Team(
                name='Air Force',
                schedule=Location(
                    url=
                    'https://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=16320&org_id=721&stats_player_seq=-100'
                ),
                year='2023',
                id='ml-ncaa-721',
                div='ml1',
                sport='ml',
                source='ncaa'))

    def test_ncaa_team_schedule_html(self):
        html = fixtures.ncaa_game_by_game()
        n = ncaa.Ncaa()
        team = Team(
            name='Air Force',
            schedule=Location(
                url=
                'https://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=16320&org_id=721&stats_player_seq=-100'
            ),
            year=2023,
            id='ml-ncaa-721',
            div='ml1',
            sport='ml',
            source='ncaa')
        games = n.convert_schedule_html(html, team)
        self.assertEqual(
            games[0],
            ScheduleGame(
                id='ml-ncaa-1822151',
                date='2020-02-01',
                opponent=TeamSummary(name='Duke', id='ml-ncaa-193'),
                home=False,
                result=ScheduleGameResult(points_for=14, points_against=13),
                source='ncaa',
                sport='ml',
                details=Location(
                    url='https://stats.ncaa.org/contests/1822151/box_score')))
        self.assertEqual(list(map(lambda g: g.opponent.name, games)), [
            'Duke', 'Denver', 'Utah', 'Cleveland St.', 'St. Bonaventure',
            'Virginia', 'Canisius', 'Furman'
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
            Location(url='https://stats.ncaa.org/contests/1822151/box_score'),
            'ml-ncaa-1822151', 'ml', 'ncaa', home_team, away_team)
        self.assertEqual(game_details.date, '2020-02-01')
        self.assertEqual(game_details.id, 'ml-ncaa-1822151')
        self.assertEqual(game_details.external_link,
                         'https://stats.ncaa.org/contests/1822151/box_score')
        self.assertEqual(game_details.home_team, home_team)
        self.assertEqual(game_details.away_team, away_team)
        self.assertEqual(game_details.result,
                         GameResult(home_score=13, away_score=14))
        self.assertEqual(len(game_details.home_stats), 27)
        self.assertEqual(
            game_details.home_stats[0],
            GameStatLine(player=PlayerSummary(
                name='CJ Carpenter',
                id='ml-ncaa-1764378',
                external_link=
                'https://stats.ncaa.org/player/index?game_sport_year_ctl_id=15203&org_id=193&stats_player_seq=1764378'
            ),
                         position='A',
                         gb=2,
                         g=2,
                         a=2))
        self.assertEqual(len(game_details.away_stats), 28)
        self.assertEqual(
            game_details.away_stats[0],
            GameStatLine(player=PlayerSummary(
                name='August Johnson',
                id='ml-ncaa-2126497',
                external_link=
                'https://stats.ncaa.org/player/index?game_sport_year_ctl_id=15203&org_id=721&stats_player_seq=2126497'
            ),
                         position='A',
                         gb=0,
                         g=0,
                         a=0))

    def test_non_divisional_and_alt_id(self):
        html = fixtures.malone_game_by_game()
        n = ncaa.Ncaa()
        team = Team(
            id='ml-ncaa-721',
            name='Malone',
            schedule=Location(
                url=
                'https://stats.ncaa.org/player/game_by_game?game_sport_year_ctl_id=16320&org_id=721&stats_player_seq=-100'
            ),
            div='ml1',
            year='2024',
            sport='ml',
            source='ncaa')
        games = n.convert_schedule_html(html, team)
        self.assertEqual(team.alt_id, '571523')
        self.assertEqual(
            games[0],
            ScheduleGame(date='2024-02-08',
                         opponent=TeamSummary(name='SCAD Savannah',
                                              id='ml-ncaa-nd-scad-savannah'),
                         home=False,
                         source='ncaa',
                         sport='ml'))
        self.assertEqual(
            games[1],
            ScheduleGame(date='2024-02-10',
                         opponent=TeamSummary(name='Shorter', alt_id='571497'),
                         home=False,
                         source='ncaa',
                         sport='ml'))

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
