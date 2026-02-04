import unittest
from . import mcla
from . import fixtures
from ..shared.types import Team, Location, ScheduleGame, ScheduleGameResult, TeamSummary, PlayerSummary, GameResult, GameStatLine


class TestMcla(unittest.TestCase):

    def test_mcla_urls(self):
        m = mcla.Mcla()
        self.assertEqual(
            next(m.get_team_list_urls('2020')).url,
            'https://mcla.us/teams?current_season_year=2020&view_by=division')

    def test_mcla_team_list_html(self):
        html = fixtures.mcla_team_list()
        m = mcla.Mcla()
        team_list = list(
            m.convert_team_list_html(html, '2026',
                                     next(m.get_team_list_urls('2026'))))
        self.assertEqual(len(team_list), 174)
        self.assertEqual(
            team_list[0],
            Team(name='Alabama',
                 schedule=Location(
                     url='https://mcla.us/teams/alabama/2026/schedule'),
                 roster=Location(
                     url='https://mcla.us/teams/alabama/2026/roster'),
                 year='2026',
                 div='mcla1',
                 id='ml-mcla-alabama',
                 sport='ml',
                 source='mcla'))

    def test_mcla_team_schedule_html(self):
        html = fixtures.mcla_schedule()
        m = mcla.Mcla()
        team = Team(
            id='ml-mcla-arizona-state',
            name='Arizona State',
            year='2024',
            sport='ml',
            source='mcla',
            div='mcla1',
            schedule=Location(
                url='https://mcla.us/teams/arizona-state/2024/schedule'),
            roster=Location(
                url='https://mcla.us/teams/arizona-state/2024/roster'))
        games = m.convert_schedule_html(html, team)
        self.assertEqual(
            games[0],
            ScheduleGame(
                id='ml-mcla-arizona-state-vs-utah-tech-2024-af4b5d',
                date='2024-02-09T19:00:00',
                opponent=TeamSummary(name='UTech', id='ml-mcla-utah-tech'),
                home=True,
                result=ScheduleGameResult(points_for=21, points_against=8),
                source='mcla',
                sport='ml',
                details=Location(
                    url=
                    'https://mcla.us/games/arizona-state-vs-utah-tech-2024-af4b5d'
                )))
        self.assertEqual(list(map(lambda t: t.opponent.name, games)), [
            'UTech', 'Cal Poly', 'Auburn', 'Colorado', 'Utah Valley', 'BYU',
            'Georgia Tech', 'Georgia', 'Chapman', 'San Diego State', 'USC',
            'UCLA', 'Grand Canyon', 'Arizona', 'Arizona', 'Virginia Tech',
            'Liberty'
        ])

    def test_mcla_game_details(self):
        html = fixtures.mcla_game_details()
        m = mcla.Mcla()
        away_team = Team(name='Oregon State',
                         id='ml-mcla-oregon-state',
                         year='2026',
                         div='mcla1',
                         sport='ml',
                         source='mcla',
                         schedule=Location(url='schedule1'))
        home_team = Team(name='Arizona Christian',
                         id='ml-mcla-arizona-christian',
                         year='2026',
                         div='mcla1',
                         sport='ml',
                         source='mcla',
                         schedule=Location(url='schedule2'))
        game_details = m.convert_game_details_html(
            html,
            Location(
                url='https://mcla.us/games/arizona-christian-vs-oregon-state-2026-5d5605'),
            'ml-mcla-arizona-christian-vs-oregon-state-2026-5d5605', 'ml', 'mcla',
            home_team, away_team)
        self.assertEqual(game_details.date, '2026-01-31T12:00:00-05:00')
        self.assertEqual(game_details.id,
                         'ml-mcla-arizona-christian-vs-oregon-state-2026-5d5605')
        self.assertEqual(
            game_details.external_link,
            'https://mcla.us/games/arizona-christian-vs-oregon-state-2026-5d5605')
        self.assertEqual(game_details.home_team,
                         TeamSummary(name='Arizona Christian', id='ml-mcla-arizona-christian'))
        self.assertEqual(game_details.away_team,
                         TeamSummary(name='Oregon State', id='ml-mcla-oregon-state'))
        self.assertEqual(game_details.result,
                         GameResult(home_score=8, away_score=9))
        # This game includes player stats; ensure we parsed them
        self.assertEqual(len(game_details.home_stats), 19)
        self.assertEqual(len(game_details.away_stats), 35)
        self.assertEqual(
            game_details.away_stats[0].player,
            PlayerSummary(id='ml-mcla-alex-kemalyan-7a83bb',
                          name='Alex Kemalyan',
                          external_link='https://mcla.us/players/alex-kemalyan-7a83bb'))

    def test_mcla_roster(self):
        html = fixtures.mcla_roster()
        m = mcla.Mcla()
        team = Team(id='ml-mcla-arizona-state',
                    name='Arizona State',
                    year='2024',
                    div='mcla1',
                    sport='ml',
                    source='mcla',
                    schedule=Location(url='schedule1'))
        roster = m.convert_roster(html, team)

        self.assertEqual(roster.coach.name, 'Justin Straker')
        self.assertEqual(roster.coach.id, 'ml-mcla-justin-straker-9f2386')
        self.assertEqual(roster.coach.external_link,
                         'https://mcla.us/coaches/justin-straker-9f2386')
        self.assertEqual(roster.conference.name,
                         'Southwestern Lacrosse Conference')
        self.assertEqual(roster.conference.id, 'ml-mcla-slc')
        self.assertEqual(roster.conference.external_link,
                         'https://mcla.us/conferences/slc')
        self.assertEqual(len(roster.players), 46)
        first_player = roster.players[0]
        self.assertEqual(first_player.number, 34)
        self.assertEqual(
            first_player.player,
            PlayerSummary(
                id='ml-mcla-luke-baldwin-c56198',
                name='Luke Baldwin',
                external_link='https://mcla.us/players/luke-baldwin-c56198'))
        self.assertEqual(first_player.class_year, 'Fr')
        self.assertEqual(first_player.position, 'Midfield')
        self.assertEqual(first_player.height, '6\' 0"')
        self.assertEqual(first_player.weight, '190 lbs')
        self.assertEqual(first_player.hometown, 'Dallas, TX')
