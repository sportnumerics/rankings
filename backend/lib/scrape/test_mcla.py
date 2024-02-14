import unittest
from . import mcla
from . import fixtures
from .types import Team, Location, ScheduleGame, ScheduleGameResult, TeamSummary, PlayerSummary, GameResult, GameStatLine


class TestMcla(unittest.TestCase):

    def test_mcla_urls(self):
        m = mcla.Mcla()
        self.assertEqual(
            next(m.get_team_list_urls('2020'))['url'],
            'https://mcla.us/teams/2020')

    def test_mcla_team_list_html(self):
        html = fixtures.mcla_team_list()
        m = mcla.Mcla()
        team_list = list(
            m.convert_team_list_html(html, '2020',
                                     next(m.get_team_list_urls('2020'))))
        self.assertEqual(len(team_list), 163)
        self.assertEqual(
            team_list[0],
            Team(name='Alabama',
                 schedule=Location(
                     url='https://mcla.us/team/alabama/2020/schedule.html'),
                 roster=Location(
                     url='https://mcla.us/team/alabama/2020/roster.html'),
                 year='2020',
                 div='mcla1',
                 id='ml-mcla-alabama',
                 sport='ml',
                 source='mcla'))

    def test_mcla_converts_slugs_correctly(self):
        html = fixtures.mcla_team_list()
        m = mcla.Mcla()
        team_list = list(
            m.convert_team_list_html(html, '2020',
                                     next(m.get_team_list_urls('2020'))))
        self.assertEqual(
            team_list[2],
            Team(
                name='Arizona State',
                schedule=Location(
                    url='https://mcla.us/team/arizona_state/2020/schedule.html'
                ),
                roster=Location(
                    url='https://mcla.us/team/arizona_state/2020/roster.html'),
                year='2020',
                div='mcla1',
                id='ml-mcla-arizona-state',
                sport='ml',
                source='mcla'))

    def test_mcla_team_schedule_html(self):
        html = fixtures.mcla_schedule()
        m = mcla.Mcla()
        team = Team(
            id='ml-mcla-arizona-state',
            name='Arizona State',
            year='2020',
            sport='ml',
            source='mcla',
            div='mcla1',
            schedule=Location(
                url='https://mcla.us/team/arizona_state/2020/schedule.html'),
            roster=Location(
                url='https://mcla.us/team/arizona_state/2020/roster.html'))
        games = m.convert_schedule_html(html, team)
        self.assertEqual(
            games[0],
            ScheduleGame(id='ml-mcla-23539',
                         date='2020-02-09T13:00:00',
                         opponent=TeamSummary(name='Dominican',
                                              id='ml-mcla-dominican'),
                         home=True,
                         result=ScheduleGameResult(points_for=11,
                                                   points_against=16),
                         source='mcla',
                         sport='ml',
                         details=Location(url='https://mcla.us/game/23539')))
        self.assertEqual(list(map(lambda t: t.opponent.name, games)), [
            'Dominican', 'USC', 'California', 'Cal Poly', 'Santa Clara',
            'Georgia Tech', 'Texas A&M', 'San Diego State', 'UCLA',
            'Brigham Young', 'Concordia-Irvine', 'Chapman', 'Grand Canyon',
            'Arizona'
        ])

    def test_mcla_game_details(self):
        html = fixtures.mcla_game_details()
        m = mcla.Mcla()
        home_team = {
            'name': 'Loyola Marymount',
            'id': 'ml-mcla-loyola-marymount'
        }
        away_team = {'name': 'Air Force', 'id': 'ml-mcla-air-force'}
        game_details = m.convert_game_details_html(
            html, {'url': 'https://mcla.us/games/26005'}, 'ml-mcla-26005',
            'ml', 'mcla', home_team, away_team)
        self.assertEqual(game_details.date, '2023-02-17T19:00:00-07:00')
        self.assertEqual(game_details.id, 'ml-mcla-26005')
        self.assertEqual(game_details.external_link,
                         'https://mcla.us/games/26005')
        self.assertEqual(
            game_details.home_team,
            TeamSummary(name='Loyola Marymount',
                        id='ml-mcla-loyola-marymount'))
        self.assertEqual(game_details.away_team,
                         TeamSummary(name='Air Force', id='ml-mcla-air-force'))
        self.assertEqual(game_details.result,
                         GameResult(home_score=12, away_score=24))
        self.assertEqual(
            game_details.home_stats[0],
            GameStatLine(
                number=5,
                player=PlayerSummary(
                    name='Ben Taylor',
                    id='ml-mcla-56639',
                    external_link='https://mcla.us/player/56639/ben_taylor.html'
                ),
                position='M',
                gb=2,
                g=1,
                a=1))
        self.assertEqual(
            game_details.away_stats[0],
            GameStatLine(player=PlayerSummary(
                name='Aden Extrand',
                id='ml-mcla-59796',
                external_link='https://mcla.us/player/59796/aden_extrand.html'
            ),
                         number=32,
                         position='DM',
                         gb=0,
                         g=0,
                         a=0))

    def test_mcla_roster(self):
        html = fixtures.mcla_roster()
        m = mcla.Mcla()
        team = {
            'name': 'Alabama',
            'year': '2024',
            'sport': 'ml',
            'source': 'mcla'
        }
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
