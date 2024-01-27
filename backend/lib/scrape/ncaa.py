import requests
import datetime
import re
from bs4 import BeautifulSoup

SPORT_MAP = {'MLA': 'ml', 'WLA': 'wl'}

class Ncaa():
  base_url = 'https://stats.ncaa.org'

  def __init__(self, sports=['MLA', 'WLA'], divs=['1', '2', '3']):
    self.sports = sports
    self.divs = divs

  def get_team_list_urls(self, year):
    for sport in self.sports:
      for div in self.divs:
        yield {
            'url': f'{self.base_url}/team/inst_team_list',
            'params': {
                'academic_year': year,
                'division': div,
                'sport_code': sport
            }
        }

  def convert_team_list_html(self, html, location):
    soup = BeautifulSoup(html, 'html.parser')
    team_links = soup.table.table.find_all('a')
    for link in team_links:
      link_parts = link['href'].split('/')
      sport = SPORT_MAP[location['params']['sport_code']]
      yield {
          'name': link.string,
          'schedule': {
              'url': f'{self.base_url}/player/game_by_game',
              'params': {
                  'game_sport_year_ctl_id': link_parts[3],
                  'org_id': link_parts[2],
                  'stats_player_seq': -100
              }
          },
          'id': f'{sport}-ncaa-{link_parts[2]}',
          'div': sport + location['params']['division'],
          'sport': sport,
          'year': location['params']['academic_year'],
          'source': 'ncaa'
      }

  def convert_schedule_html(self, html, team):
    soup = BeautifulSoup(html, 'html.parser')
    game_breakdown_div = soup.find(id='game_breakdown_div')
    rows = game_breakdown_div.table.table.find_all('tr') if game_breakdown_div else []
    games = []
    for row in rows:
      game = {}
      if 'class' in row.attrs or 'style' in row.attrs:
        continue
      cols = list(row.find_all('td'))
      date_col = cols[0]
      opp_col = cols[1]
      result_col = cols[2]

      game['date'] = self._to_iso_format(date_col.string)

      opp_link = opp_col.find(
          lambda tag: tag.name == 'a' and not tag.has_attr('class'))
      opp_string = ' '.join(opp_col.stripped_strings)
      opp_match = re.match(
          r'(?P<away>\@)?\s*(?P<opponent_name>[^\@]+)(\@(?P<neutral_site>.*))?',
          opp_string)
      if not opp_match:
        continue

      game['sport'] = team['sport']
      game['source'] = team['source']

      game['opponent'] = {'name': opp_match.group('opponent_name').strip()}
      game['home'] = opp_match.group('away') is None

      opp_link_parts = opp_link['href'].split('/')
      if len(opp_link_parts) > 2:
        game['opponent']['id'] = '-'.join(
            [team['sport'], team['source'], opp_link_parts[2]])

      result_str = ' '.join(result_col.stripped_strings)
      score_match = re.match(
          r'(?P<outcome>[WL])?\s*(?P<points_for>\d+)\s*\-\s*(?P<points_against>\d+)',
          result_str)
      if score_match:
        game['result'] = {
            'points_for': int(score_match.group('points_for')),
            'points_against': int(score_match.group('points_against'))
        }
      if hasattr(result_col, 'a') and hasattr(result_col.a, 'href'):
        game_details_url = result_col.a['href']
        url_match = re.match(r'/contests/(?P<id>\d+)/box_score', game_details_url)
        if url_match:
          game['details'] = {
            'url': self.base_url + game_details_url
          }
          game['id'] = 'ml-ncaa-' + url_match.group('id')

      games.append(game)
    return {'team': team, 'games': games}

  TEAM_HREF_REGEX = re.compile(r'/teams/(?P<id>\d+)')
  TEAM_NAME_REGEX = re.compile(r'(#\d+ )?(?P<name>[a-zA-Z0-9\-_&\' .()]+) \(\d+-\d+\)')

  def convert_game_details_html(self, html, location, game_id, sport, source, home_team, away_team):
    soup = BeautifulSoup(html, 'html.parser')
    date = self._to_iso_format(next(soup.find('td', string='Game Date:').find_next_sibling('td').stripped_strings))

    def is_team_href(href):
      m = self.TEAM_HREF_REGEX.match(href)
      return m

    team_links = soup.find_all('a', href=is_team_href)

    def get_total_score(link):
      row = link.find_parent('tr')
      cells = row.find_all('td')
      return int(cells[5].get_text(strip=True))

    stats_headers = list(map(lambda x: x.parent, soup.find_all('th', string='Player')))

    def get_stats(header):
      def cols(row, name):
        return list(row.find_all(name))
      def stats(row, keys):
        columns = cols(row, 'td')
        return {v[0]: v[1] for v in (self._map_statistic(sport, source, keys[i], v) for i, v in enumerate(columns)) if v}
      keys = list(map(lambda x: x.get_text(strip=True), cols(header, 'th')))
      stats = list(filter(lambda p: p.get('player'), map(lambda r: stats(r, keys), header.find_next_siblings('tr'))))
      return stats

    away_score = get_total_score(team_links[0])
    home_score = get_total_score(team_links[1])
    result = {'home_score': home_score, 'away_score': away_score} if home_score and away_score else None

    return {
      'date': date,
      'id': game_id,
      'external_link': location['url'],
      'away_team': away_team,
      'home_team': home_team,
      'result': result,
      'away_stats': get_stats(stats_headers[0]),
      'home_stats': get_stats(stats_headers[1])
    }

  PLAYER_HREF_REGEX = re.compile(r'/player/index\?game_sport_year_ctl_id=(?P<gsycid>\d+)&(amp;)?org_id=(?P<org_id>\d+)&(amp;)?stats_player_seq=(?P<spseq>\d+)')

  def _map_statistic(self, sport, source, key, tag):
    text = tag.get_text(strip=True)
    def get_num(t):
      return int(t.replace('/','') if t else 0)

    try:
      match key:
        case 'Player':
          a = tag.find('a')
          if not a:
            return None
          href = a['href']
          href_match = self.PLAYER_HREF_REGEX.match(href)
          if not href_match:
            raise Exception(f'no match {href}')
          last, first = text.split(', ')
          return ('player', {
            'name': f'{first} {last}',
            'id': sport + '-' + source + '-' + href_match.group('spseq'),
            'external_link': self.base_url + href.replace('&amp;', '&')
          })
        case 'Pos':
          return ('position', text) if text else None
        case 'Goals':
          return ('g', get_num(text))
        case 'Assists':
          return ('a', get_num(text))
        case 'GB':
          return ('gb', get_num(text))
        case _:
          return None
    except:
      raise Exception(f'error mapping statistic {tag}')

  def _to_iso_format(self, date):
    return datetime.datetime.strptime(date, '%m/%d/%Y').date().isoformat()
