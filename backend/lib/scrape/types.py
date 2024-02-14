from dataclasses import dataclass
from dataclasses_json import DataClassJsonMixin
from collections.abc import Iterator
from typing import Optional, Protocol


@dataclass
class Location(DataClassJsonMixin):
    url: str


@dataclass
class Team(DataClassJsonMixin):
    name: str
    schedule: Location
    year: str
    id: str
    div: str
    sport: str
    source: str
    roster: Location | None = None
    alt_id: str | None = None


@dataclass
class TeamSummary(DataClassJsonMixin):
    name: str
    id: str | None = None
    alt_id: str | None = None


@dataclass
class ScheduleGameResult(DataClassJsonMixin):
    points_for: int
    points_against: int


@dataclass
class ScheduleGame(DataClassJsonMixin):
    date: str
    opponent: TeamSummary
    sport: str
    source: str
    home: bool
    result: ScheduleGameResult | None = None
    id: str | None = None
    details: Location | None = None


@dataclass
class GameResult(DataClassJsonMixin):
    home_score: int
    away_score: int


@dataclass
class FaceOffResults(DataClassJsonMixin):
    won: int
    lost: int


@dataclass
class PlayerSummary(DataClassJsonMixin):
    id: str
    name: str
    external_link: str


@dataclass
class GameStatLine(DataClassJsonMixin):
    player: PlayerSummary
    number: int | None = None
    position: str | None = None
    face_offs: FaceOffResults | None = None
    gb: int = 0
    g: int = 0
    a: int = 0
    s: int = 0
    ga: int = 0


@dataclass
class Game(DataClassJsonMixin):
    id: str
    external_link: str
    date: str
    home_team: TeamSummary
    away_team: TeamSummary
    result: GameResult
    home_stats: list[GameStatLine]
    away_stats: list[GameStatLine]


@dataclass
class Coach(DataClassJsonMixin):
    name: str
    id: str
    external_link: str


@dataclass
class Conference(DataClassJsonMixin):
    name: str
    id: str
    external_link: str


@dataclass
class RosterPlayer(DataClassJsonMixin):
    number: int
    player: PlayerSummary
    class_year: str
    eligibility: str
    position: str
    height: str
    weight: str
    high_school: str | None = None
    hometown: str | None = None


@dataclass
class Roster(DataClassJsonMixin):
    coach: Coach
    conference: Conference
    players: list[RosterPlayer]


@dataclass
class TeamDetail(DataClassJsonMixin):
    team: Team
    games: list[ScheduleGame]
    roster: Roster = None


class Scraper(Protocol):

    def get_team_list_urls(self, year: str) -> Iterator[Location]:
        """Get the team list URLs for this source"""

    def convert_team_list_html(self, html: str, year: str,
                               location: Location) -> Iterator[Team]:
        """Convert the team list html into """

    def convert_schedule_html(self, html: str,
                              team: Team) -> Iterator[ScheduleGame]:
        """Convert schedule html into a schedule of games"""

    def cross_link_schedules(self, schedules: list[TeamDetail]):
        """Cross link schedules adding additional IDs if necessary"""

    def convert_game_details_html(self, html: str, location: Location,
                                  game_id: str, sport: str, source: str,
                                  home_team: Team, away_team: Team) -> Game:
        """Convert game details html into game"""

    def convert_roster(self, html: str, team: TeamSummary) -> Roster:
        """Convert roster html into roster"""

    def get_limiter_session_args(self) -> dict[str, int]:
        """Get additional arguments for LimiterSession if rate limiting is needed"""
