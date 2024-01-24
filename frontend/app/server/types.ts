type RankedTeam = Team & TeamRating & HasRanking;

export interface HasRanking {
    rank: number;
}

export interface Team {
    name: string;
    id: string;
    div: string;
    sport: string;
    source: string;
    schedule: Location;
}

export interface Location {
    url: string;
}

export interface TeamSummary {
    id: string;
    name: string;
}

export interface TeamRating {
    team: string;
    offense: number;
    defense: number;
    overall: number;
}

export interface PlayerRating {
    id: string;
    name: string;
    team: TeamSummary;
    points: number;
    goals: number;
    assists: number;
}

export type RankedPlayer = PlayerRating & HasRanking;

export interface TeamMap {
    [id: string]: Team;
}

export interface RatingMap {
    [id: string]: TeamRating;
}

export interface PlayerRatingMap {
    [id: string]: PlayerRating;
}

export interface RankedPlayerMap {
    [id: string]: RankedPlayer
}

export interface TeamSchedule {
    team: Team;
    games: ScheduleGame[]
}

export interface ScheduleGame {
    id: string;
    opponent: TeamSummary;
    home: boolean;
    date: string;
    details: GameDetailsLink;
    result: GameResult;
}

export interface GameDetailsLink {
    url: string;
}

export interface GameResult {
    points_for: number;
    points_against: number;
}

export interface RankedTeamMap {
    [id: string]: RankedTeam;
}

export interface PlayerStats {
    id: string;
    name: string;
    external_link: string;
    team: TeamSummary;
    stats: StatLine[]
}

export interface StatLine {
    game_id: string;
    date: string;
    opponent: TeamSummary;
    g: number;
    a: number;
    gb: number;
}

export interface Game {
    id: string;
    date: string;
    external_link: string;
    home_team: TeamSummary;
    away_team: TeamSummary;
    result: GameResult;
    away_stats: GameStatLine[];
    home_stats: GameStatLine[];
}

export interface GameResult {
    home_score: number;
    away_score: number;
}

export interface GameStatLine {
    number: number;
    player: PlayerSummary;
    position: string;
    face_offs: FaceOffResults;
    gb: number;
    g: number;
    a: number;
}

export interface PlayerSummary {
    id: string;
    name: string;
}

export interface FaceOffResults {
    won: number;
    lost: number;
}

export interface Year {
    id: string;
    unavailable?: string[];
}

export interface Division {
    name: string;
    id: string;
    sport: string;
    source: string;
    div: string;
}