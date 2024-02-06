from . import ncaa, mcla
from ..shared import shared
from requests_cache import CacheMixin, CachedSession
from requests_ratelimiter import LimiterSession
from datetime import timedelta
import json
import os
import pathlib
import logging
import traceback

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36'


def scrape_team_list(args):
    for year in shared.years(args.year):
        runner = ScrapeRunner(source=args.source,
                              year=year,
                              out_dir=args.out_dir)

        runner.scrape_and_write_team_lists()


def scrape_schedules(args):
    for year in shared.years(args.year):
        runner = ScrapeRunner(source=args.source,
                              year=year,
                              out_dir=args.out_dir,
                              team=args.team,
                              div=args.div,
                              limit=args.limit)

        if not hasattr(args, 'team_list_file') or not args.team_list_file:
            runner.scrape_and_write_team_lists()
            team_list_file = runner.get_team_list_filename()
        else:
            team_list_file = args.team_list_file

        runner.scrape_and_write_schedules(team_list_file)


class LimitedCachedSession(CacheMixin, LimiterSession):
    pass


class ScrapeRunner():

    def __init__(self, source, year, out_dir, team=None, div=None, limit=None):
        if source == 'ncaa':
            self.scraper = ncaa.Ncaa()
        elif source == 'mcla':
            self.scraper = mcla.Mcla()
        else:
            raise Exception(f'Unimplemented source {source}')
        self.source = source

        self.year = year

        self.out_dir = out_dir

        cache_name = os.path.join(self.out_dir, 'cache')
        session_args = self.scraper.get_limiter_session_args()
        Session = LimitedCachedSession if session_args else CachedSession
        self.cache = Session(cache_name=cache_name,
                             expire_after=timedelta(days=1),
                             **session_args)

        self.team = team
        self.div = div
        self.limit = int(limit) if limit else None
        self.log = logging.getLogger(type(self.scraper).__name__)

    def scrape_and_write_team_lists(self):
        self.log.info(
            f'scraping teams for {self.source} ({self.year}) into {self.out_dir}'
        )
        teams = self.scrape_teams()

        pathlib.Path(os.path.join(self.out_dir,
                                  self.year)).mkdir(parents=True,
                                                    exist_ok=True)
        with open(self.get_team_list_filename(), 'w') as f:
            json.dump(list(teams), f, indent=2)

    def scrape_and_write_schedules(self, team_list_file):
        self.log.info(
            f'scraping schedules for {self.source} ({self.year}) into {self.out_dir}'
        )
        with open(team_list_file) as f:
            teams = json.load(f)

        if self.limit:
            teams = teams[:self.limit]

        schedule_dir = os.path.join(self.out_dir, self.year, 'schedules')
        pathlib.Path(schedule_dir).mkdir(parents=True, exist_ok=True)
        games_dir = os.path.join(self.out_dir, self.year, 'games')
        pathlib.Path(games_dir).mkdir(parents=True, exist_ok=True)
        schedules = []
        for team in teams:
            if self.team and self.team != team['id']:
                continue
            if self.div and self.div != team['div']:
                continue
            self.log.info(f'scraping schedule for {team["name"]}')
            schedule = self.scrape_schedule(team)
            if not schedule:
                self.log.warn(f'No schedule for {team["name"]}')
                continue
            schedules.append(schedule)

        self.cross_link_schedules(schedules)
        for schedule in schedules:
            file_name = os.path.join(schedule_dir,
                                     schedule['team']['id'] + '.json')
            with open(file_name, 'w') as f:
                json.dump(schedule, f, indent=2)

        for schedule in schedules:
            team = schedule['team']
            for game in schedule['games']:
                if 'details' not in game:
                    continue

                self.log.info(
                    f'scraping game details for game {team["name"]} vs {game["opponent"]["name"]} on {game["date"]}'
                )
                opponent = game['opponent']
                (home_team,
                 away_team) = (team, opponent) if game['home'] else (opponent,
                                                                     team)
                game_details = self.scrape_game_details(
                    game['details'], game['id'], team['sport'], team['source'],
                    home_team, away_team)
                if not game_details:
                    self.log.warn(
                        f'no game details for game {team["name"]} vs {game["opponent"]["name"]} on {game["date"]}'
                    )
                    continue
                with open(
                        os.path.join(games_dir, game_details['id'] + '.json'),
                        'w') as f:
                    json.dump(game_details, f, indent=2)

    def scrape_teams(self):
        for url in self.scraper.get_team_list_urls(self.year):
            html = self.fetch(url)
            try:
                yield from self.scraper.convert_team_list_html(html, url)
            except Exception as e:
                self.log.error(
                    f'Unable to convert team list html from {url}: {e}')
                traceback.print_exception(e)
                with open(os.path.join(self.out_dir, 'error.html'), 'w') as f:
                    f.write(html)

    def scrape_schedule(self, team):
        schedule = team['schedule']
        html = self.fetch(schedule)
        try:
            return self.scraper.convert_schedule_html(html, team)
        except Exception as e:
            self.log.error(
                f'Unable to convert schedule html from {schedule}: {e}')
            traceback.print_exception(e)

    def cross_link_schedules(self, schedules):
        self.scraper.cross_link_schedules(schedules)

    def scrape_game_details(self, location, game_id, sport, source, home_team,
                            away_team):
        html = self.fetch(location)
        try:
            return self.scraper.convert_game_details_html(
                html, location, game_id, sport, source, home_team, away_team)
        except Exception as e:
            self.log.error(
                f'Unable to convert game details html from {location}:')
            traceback.print_exception(e)

    def fetch(self, location):
        response = self.cache.get(location['url'],
                                  params=location.get('params'),
                                  headers={'user-agent': USER_AGENT})
        if response.status_code != 200:
            self.log.warn(
                f'Issue fetching {location["url"]}, status code: {response.status_code}'
            )
            return None
        return response.text

    def get_team_list_filename(self):
        return os.path.join(self.out_dir, self.year,
                            f'{self.source}-teams.json')
