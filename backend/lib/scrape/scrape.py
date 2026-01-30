import datetime

import dateutil
import dateutil.parser
from lib.scrape import mcla
from . import ncaa, mcla
from ..shared import shared
from ..shared.types import Game, ScrapeArgs, Scraper, Team, TeamDetail, Location
from collections.abc import Iterator
from requests_cache import CacheMixin, CachedSession
from requests_ratelimiter import LimiterSession
from datetime import UTC, timedelta, tzinfo
import os
import pathlib
import logging
import traceback

USER_AGENT = 'sportnumerics-scraper/1.0 (https://sportnumerics.com)'


def scrape_team_list(args: ScrapeArgs):
    for year in shared.years(args.year):
        runner = ScrapeRunner(source=args.source,
                              year=year,
                              out_dir=args.out_dir)

        runner.scrape_and_write_team_lists()


def scrape_schedules(args: ScrapeArgs):
    for year in shared.years(args.year):
        runner = ScrapeRunner(source=args.source,
                              year=year,
                              out_dir=args.out_dir,
                              team=args.team,
                              div=args.div,
                              limit=args.limit)

        if hasattr(args, 'team_list_file') and args.team_list_file:
            team_list_json_file = args.team_list_file
        else:
            runner.scrape_and_write_team_lists()
            team_list_json_file = None

        runner.scrape_and_write_schedules(team_list_json_file)


class LimitedCachedSession(CacheMixin, LimiterSession):
    pass


class ScrapeRunner():
    scraper: Scraper

    def __init__(self,
                 source: str,
                 year: str,
                 out_dir: str,
                 team: str = None,
                 div: str = None,
                 limit: int = None):
        if source == 'ncaa':
            self.scraper = ncaa.Ncaa()
        elif source == 'mcla':
            self.scraper = mcla.Mcla()
        elif source == 'mcla2':
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
        teams = list(self.scrape_teams())

        # Ensure output directory exists
        year_dir = os.path.join(self.out_dir, self.year)
        pathlib.Path(year_dir).mkdir(parents=True, exist_ok=True)

        shared.dump_parquet(sorted(teams, key=lambda t: t.id),
                            shared.parquet_path(self.out_dir, self.year,
                                                'teams',
                                                f'{self.source}.parquet'),
                            sort_order=[('id', 'ascending')])

        with open(
                os.path.join(self.out_dir, self.year,
                             f'{self.source}-teams.json'), 'w') as f:
            shared.dump(teams, f, many=True)

    def scrape_and_write_schedules(self, team_list_json_file: str | None):
        self.log.info(
            f'scraping schedules for {self.source} ({self.year}) into {self.out_dir}'
        )

        if team_list_json_file:
            with open(team_list_json_file) as f:
                teams = shared.load_many(Team, f)
        else:
            teams_path = shared.parquet_path(self.out_dir, self.year, 'teams',
                                            f'{self.source}.parquet')
            if not os.path.exists(teams_path):
                self.log.warning(
                    f'Teams file not found at {teams_path}, skipping schedule scraping. '
                    f'This usually means no teams were scraped for {self.source} {self.year}.'
                )
                return
            teams = shared.load_parquet(Team, teams_path)

        if self.limit:
            teams = list(teams)[:self.limit]

        schedule_dir = os.path.join(self.out_dir, self.year, 'schedules')
        pathlib.Path(schedule_dir).mkdir(parents=True, exist_ok=True)
        games_dir = os.path.join(self.out_dir, self.year, 'games')
        pathlib.Path(games_dir).mkdir(parents=True, exist_ok=True)
        schedules: list[TeamDetail] = []
        for team in teams:
            if self.team and self.team != team.id:
                continue
            if self.div and self.div != team.div:
                continue
            self.log.info(f'scraping schedule for {team.name}')
            games = self.scrape_schedule(team)
            if not games:
                self.log.warning(f'No schedule for {team.name}')
                continue
            roster = self.scrape_roster(team)
            schedules.append(TeamDetail(team=team, games=games, roster=roster))

        self.cross_link_schedules(schedules)

        for schedule in schedules:
            file_name = os.path.join(schedule_dir, schedule.team.id + '.json')
            with open(file_name, 'w') as f:
                shared.dump(schedule, f)

        shared.dump_parquet(sorted(schedules, key=lambda s: s.team.id),
                            shared.parquet_path(self.out_dir, self.year,
                                                'schedules',
                                                f'{self.source}.parquet'),
                            sort_order=[('team.id', 'ascending')])

        all_games = {}
        for schedule in schedules:
            team = schedule.team
            for game in schedule.games:
                if not game.details:
                    continue

                if game.id in all_games:
                    self.log.info(
                        f'already fetched game details for game {team.name} vs {game.opponent.name} on {game.date}'
                    )
                    continue

                if dateutil.parser.isoparse(
                        game.date).date() > datetime.date.today():
                    continue

                self.log.info(
                    f'scraping game details for game {team.name} vs {game.opponent.name} on {game.date}'
                )
                opponent = game.opponent
                (home_team,
                 away_team) = (team, opponent) if game.home else (opponent,
                                                                  team)
                game_details = self.scrape_game_details(
                    game.details, game.id, team.sport, team.source, home_team,
                    away_team)
                if not game_details:
                    self.log.warning(
                        f'no game details for game {team.name} vs {game.opponent.name} on {game.date}'
                    )
                    continue
                all_games[game_details.id] = game_details
                with open(os.path.join(games_dir, game_details.id + '.json'),
                          'w') as f:
                    shared.dump(game_details, f)

        shared.dump_parquet(sorted(all_games.values(), key=lambda g: g.id),
                            shared.parquet_path(self.out_dir, self.year,
                                                'games',
                                                f'{self.source}.parquet'),
                            sort_order=[('id', 'ascending')])

    def scrape_teams(self) -> Iterator[Team]:
        for url in self.scraper.get_team_list_urls(self.year):
            html = self.fetch(url)
            try:
                yield from self.scraper.convert_team_list_html(
                    html, self.year, url)
            except Exception as e:
                self.log.error(
                    f'Unable to convert team list html from {url}: {e}')
                traceback.print_exception(e)
                with open(os.path.join(self.out_dir, 'error.html'), 'w') as f:
                    f.write(html)

    def scrape_schedule(self, team: Team):
        schedule_location = team.schedule
        html = self.fetch(schedule_location)
        if not html:
            return
        try:
            return self.scraper.convert_schedule_html(html, team)
        except Exception as e:
            self.log.error(
                f'Unable to convert schedule html from {schedule_location}: {e}'
            )
            traceback.print_exception(e)

    def scrape_roster(self, team: Team):
        if not team.roster:
            return None
        roster_location = team.roster
        html = self.fetch(roster_location)
        try:
            return self.scraper.convert_roster(html, team)
        except Exception as e:
            self.log.error(
                f'Unable to convert roster html from {roster_location}: {e}')
            traceback.print_exception(e)

    def cross_link_schedules(self, schedules: list[TeamDetail]):
        self.scraper.cross_link_schedules(schedules)

    def scrape_game_details(self, location: Location, game_id: str, sport: str,
                            source: str, home_team: Team, away_team: Team):
        html = self.fetch(location)
        try:
            return self.scraper.convert_game_details_html(
                html, location, game_id, sport, source, home_team, away_team)
        except Exception as e:
            self.log.error(
                f'Unable to convert game details html from {location}:')
            traceback.print_exception(e)

    def fetch(self, location):
        response = self.cache.get(location.url,
                                  headers={'user-agent': USER_AGENT})
        if response.status_code != 200:
            self.log.warning(
                f'Issue fetching {location.url}, status code: {response.status_code}'
            )
            return None
        return response.text
