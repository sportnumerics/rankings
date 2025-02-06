import unittest
from . import mcla2
from . import fixtures
from ..shared.types import Team, Location, ScheduleGame, ScheduleGameResult, TeamSummary, PlayerSummary, GameResult, GameStatLine


class TestMcla2(unittest.TestCase):

    def test_mcla_urls(self):
        m = mcla2.Mcla2()
        self.assertEqual(
            next(m.get_team_list_urls('2020')).url,
            'https://mcla.us/teams?current_season_year=2020&view_by=division')

    def test_mcla_team_list_html(self):
        html = fixtures.mcla2_team_list()
        m = mcla2.Mcla2()
        team_list = list(
            m.convert_team_list_html(html, '2025',
                                     next(m.get_team_list_urls('2025'))))
        self.assertEqual(len(team_list), 212)
        self.assertEqual(
            team_list[0],
            Team(name='Adams State University',
                 schedule=Location(
                     url='https://mcla.us/teams/adams_state/2025/schedule'),
                 roster=Location(
                     url='https://mcla.us/teams/adams_state/2025/roster'),
                 year='2025',
                 div='mcla1',
                 id='ml-mcla-adams-state',
                 sport='ml',
                 source='mcla'))

    def test_mcla_team_schedule_html(self):
        html = fixtures.mcla2_schedule()
        m = mcla2.Mcla2()
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
        html = fixtures.mcla2_game_details()
        m = mcla2.Mcla2()
        home_team = Team(name='Loyola Marymount',
                         id='ml-mcla-loyola-marymount',
                         year='2023',
                         div='mcla1',
                         sport='ml',
                         source='mcla',
                         schedule=Location(url='schedule1'))
        away_team = Team(name='Air Force',
                         id='ml-mcla-air-force',
                         year='2023',
                         div='mcla1',
                         sport='ml',
                         source='mcla',
                         schedule=Location(url='schedule2'))
        game_details = m.convert_game_details_html(
            html,
            Location(
                url=
                'https://mcla.us/games/arizona-state-vs-utah-tech-2024-af4b5d'
            ), 'ml-mcla-arizona-state-vs-utah-tech-2024-af4b5d', 'ml', 'mcla',
            home_team, away_team)
        self.assertEqual(game_details.date, '2024-02-09T19:00:00')
        self.assertEqual(game_details.id,
                         'ml-mcla-arizona-state-vs-utah-tech-2024-af4b5d')
        self.assertEqual(
            game_details.external_link,
            'https://mcla.us/games/arizona-state-vs-utah-tech-2024-af4b5d')
        self.assertEqual(
            game_details.home_team,
            TeamSummary(name='Arizona State', id='ml-mcla-arizona-state'))
        self.assertEqual(game_details.away_team,
                         TeamSummary(name='Utah Tech', id='ml-mcla-utah-tech'))
        self.assertEqual(game_details.result,
                         GameResult(home_score=21, away_score=8))
        self.assertEqual(
            game_details.home_stats[0],
            GameStatLine(
                number=1,
                player=PlayerSummary(
                    name='Owen Kielty',
                    id='ml-mcla-owen-kielty-6fa276',
                    external_link='https://mcla.us/players/owen-kielty-6fa276'
                ),
                position='M',
                gb=1,
                g=1,
                a=0))
        self.assertEqual(
            game_details.away_stats[0],
            GameStatLine(player=PlayerSummary(
                name='Luke Kish',
                id='ml-mcla-luke-kish-fc1b2a',
                external_link='https://mcla.us/players/luke-kish-fc1b2a'),
                         number=1,
                         position='A',
                         gb=0,
                         g=0,
                         a=0))

    def test_mcla_roster(self):
        html = fixtures.mcla_roster()
        m = mcla2.Mcla2()
        team = Team(id='ml-mcla-alabama',
                    name='Alabama',
                    year='2024',
                    div='mcla1',
                    sport='ml',
                    source='mcla',
                    schedule=Location(url='schedule1'))
        roster = m.convert_roster(html, team)

        self.assertEqual(roster.coach.name, 'Shane Ryan')
        self.assertEqual(roster.coach.id, 'ml-mcla-2417')
        self.assertEqual(roster.coach.external_link,
                         'https://mcla.us/coach/2417/shane_ryan')
        self.assertEqual(roster.conference.name,
                         'SouthEastern Lacrosse Conference')
        self.assertEqual(roster.conference.id, 'ml-mcla-selc')
        self.assertEqual(roster.conference.external_link,
                         'https://mcla.us/conference/selc')
        self.assertEqual(len(roster.players), 48)
        first_player = roster.players[0]
        self.assertEqual(first_player.number, 2)
        self.assertEqual(
            first_player.player,
            PlayerSummary(
                id='ml-mcla-56433',
                name='Jack Swartwood',
                external_link='https://mcla.us/player/56433/jack_swartwood.html'
            ))
        self.assertEqual(first_player.class_year, 'Jr')
        self.assertEqual(first_player.eligibility, 'Jr')
        self.assertEqual(first_player.position, 'Mid')
        self.assertEqual(first_player.height, '5\' 8"')
        self.assertEqual(first_player.weight, '160')
        self.assertEqual(first_player.high_school, 'Knoxville Catholic')
        self.assertEqual(first_player.hometown, 'Knoxville, TN')
