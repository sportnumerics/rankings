import unittest
import datetime
from . import ncaa
from . import fixtures


class TestScrape(unittest.TestCase):
  def test_ncaa_urls(self):
    n = ncaa.Ncaa(['MLA'], ['1', '2'])
    urls = list(n.get_team_list_urls('2020'))
    self.assertEqual(urls[0]['url'],
                     'https://stats.ncaa.org/team/inst_team_list')
    self.assertEqual(urls[0]['params'], {
        'academic_year': '2020',
        'division': '1',
        'sport_code': 'MLA'
    })
    self.assertEqual(urls[1]['url'],
                     'https://stats.ncaa.org/team/inst_team_list')
    self.assertEqual(urls[1]['params'], {
        'academic_year': '2020',
        'division': '2',
        'sport_code': 'MLA'
    })

  def test_ncaa_team_list_html(self):
    html = fixtures.ncaa_team_list()
    n = ncaa.Ncaa()
    team_list = list(
        n.convert_team_list_html(html, next(n.get_team_list_urls('2020'))))
    self.assertEqual(len(team_list), 49)
    self.assertEqual(
        team_list[0], {
            'name': 'Air Force',
            'schedule': {
                'url': 'https://stats.ncaa.org/player/game_by_game',
                'params': {
                    'game_sport_year_ctl_id': '15203',
                    'org_id': '721',
                    'stats_player_seq': -100
                }
            },
            'year': '2020',
            'id': 'ml-ncaa-721',
            'div': 'ml1',
            'sport': 'ml',
            'source': 'ncaa'
        })

  def test_ncaa_team_schedule_html(self):
    html = fixtures.ncaa_game_by_game()
    n = ncaa.Ncaa()
    team = {'name': 'Air Force', 'sport': 'ml', 'source': 'ncaa'}
    schedule = n.convert_schedule_html(html, team)
    self.assertEqual(schedule['team'], team)
    self.assertEqual(
        schedule['games'][0], {
            'id': 'ml-ncaa-1822151',
            'date': '2020-02-01',
            'opponent': {
                'name': 'Duke',
                'id': 'ml-ncaa-193'
            },
            'home': False,
            'result': {
                'points_for': 14,
                'points_against': 13
            },
            'details': {
              'url': 'https://stats.ncaa.org/contests/1822151/box_score'
            }
        })
    self.assertEqual(
        list(map(lambda g: g['opponent']['name'], schedule['games'])), [
            'Duke', 'Denver', 'Utah', 'Cleveland St.', 'St. Bonaventure',
            'Virginia', 'Canisius', 'Furman'
        ])

  def test_ncaa_game_details(self):
    self.maxDiff = None
    html = fixtures.ncaa_game_details()
    n = ncaa.Ncaa()
    game_details = n.convert_game_details_html(html, { 'url': 'https://stats.ncaa.org/contests/1822151/box_score' }, 'ml-ncaa-1822151', 'ml', 'ncaa')
    self.assertEqual(game_details['date'], '2020-02-01')
    self.assertEqual(game_details['id'], 'ml-ncaa-1822151')
    self.assertEqual(game_details['external_link'], 'https://stats.ncaa.org/contests/1822151/box_score')
    self.assertEqual(game_details['home_team'], {
        'name': 'Duke',
        'id': 'ml-ncaa-493848'
    })
    self.assertEqual(game_details['away_team'], {
        'name': 'Air Force',
        'id': 'ml-ncaa-493893'
    })
    self.assertEqual(game_details['result'], {
        'home_score': 13,
        'away_score': 14
    })
    self.assertEqual(len(game_details['home_stats']), 27)
    self.assertEqual(game_details['home_stats'][0], {
        'player': {
            'name': 'CJ Carpenter',
            'id': 'ml-ncaa-1764378',
            'external_link': 'https://stats.ncaa.org/player/index?game_sport_year_ctl_id=15203&org_id=193&stats_player_seq=1764378'
        },
        'position': 'A',
        'gb': 2,
        'g': 2,
        'a': 2
    })
    self.assertEqual(len(game_details['away_stats']), 28)
    self.assertEqual(game_details['away_stats'][0], {
      'player': {
        'name': 'August Johnson',
        'id': 'ml-ncaa-2126497',
        'external_link': 'https://stats.ncaa.org/player/index?game_sport_year_ctl_id=15203&org_id=721&stats_player_seq=2126497'
      },
      'position': 'A',
      'gb': 0,
      'g': 0,
      'a': 0
    })