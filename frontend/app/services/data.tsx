
const BASE_URL = process.env.NEXT_PUBLIC_BASE_URL;

export async function getYears(): Promise<Year[]> {
    const response = await fetch(`${BASE_URL}/years.json`);
    return response.json();
}

export async function getDivs(): Promise<Division[]> {
    const response = await fetch(`${BASE_URL}/divs.json`);
    return response.json();
}

export async function getDiv(div: string): Promise<Division | null> {
    const divs = await getDivs();
    return divs.find(d => d.id === div) ?? null;
}

export async function getTeams({ year, div }: { year: string, div: string }): Promise<TeamMap | null> {
    const divisions = await getDivs();
    const division = divisions.find(division => division.id === div);
    if (!division) {
        console.error(`No division ${div}`)
        return null;
    }
    const response = await fetch(`${BASE_URL}/data/${year}/${division.source}-teams.json`);
    if (!response.ok) {
        console.error(`/data/${year}/${division.source}-teams not available`);
        return null;
    }
    const teams: Team[] = await response.json();
    return Object.fromEntries(teams.map(team => [team.id, team]));
}

export async function getRankedTeamsByDiv({ year, div }: { year: string, div: string }): Promise<RankedTeamMap | null> {
    const teamsPromise = getTeams({year, div});
    const ratingsPromise = getRatings({year});
    const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
    if (!teams) {
        console.error(`No teams for ${year} ${div}`)
        return null;
    }
    if (!ratings) {
        console.error(`No teams ratings for ${year} ${div}`);
        return null;
    }
    const teamRatings = Object.values(teams)
        .filter(team => team.div === div)
        .map(team => ({...team, ...ratings[team.id]}));
    teamRatings.sort((a, b) => b.overall - a.overall);
    return Object.fromEntries(teamRatings.map((team, i) => [team.id, {...team, rank: i + 1}]));
}

export async function getTeamSchedule({ year, team }: { year: string, team: string }): Promise<TeamSchedule | null> {
    const response = await fetch(`${BASE_URL}/data/${year}/schedules/${team}.json`);
    if (!response.ok) {
        return null;
    }
    return await response.json();
}

export async function getRatings({ year }: { year: string}): Promise<RatingMap | null> {
    const response = await fetch(`${BASE_URL}/data/${year}/team-ratings.json`);
    if (!response.ok) {
        return null;
    }
    const ratings: TeamRating[] = await response.json();
    return Object.fromEntries(ratings.map(rating => [rating.team, rating]));
}

export async function getPlayerRatings({ year }: {year: string}): Promise<PlayerRatingMap | null> {
    const response = await fetch(`${BASE_URL}/data/${year}/player-ratings.json`);
    if (!response.ok) {
        return null;
    }
    const ratings: PlayerRating[] = await response.json();
    return Object.fromEntries(ratings.map(rating => [rating.id, rating]));
}

export async function getRankedPlayersByDiv({ year, div }: { year: string, div: string }): Promise<RankedPlayerMap | null> {
    const teamsPromise = getTeams({year, div});
    const ratingsPromise = getPlayerRatings({ year });
    const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
    if (!teams || !ratings) {
        return null;
    }
    const playerRatings = Object.values(ratings)
        .filter(player => teams[player.team.id]?.div === div);
    playerRatings.sort((a, b) => b.points - a.points);
    return Object.fromEntries(playerRatings.map((player, i) => [player.id, {...player, rank: i + 1}]));
}

export async function getRankedPlayersByTeam({ year, team }: { year: string, team: string }): Promise<RankedPlayerMap | null> {
    const ratings = await getPlayerRatings({ year });
    if (!ratings) {
        return null;
    }
    const players = Object.values(ratings)
        .filter(player => player.team.id === team);
    players.sort((a, b) => b.points - a.points);
    return Object.fromEntries(players.map((player, i) => [player.id, {...player, rank: i + 1}]));
}

export async function getPlayerStats({ year, player }: { year: string, player: string }): Promise<PlayerStats | null> {
    const response = await fetch(`${BASE_URL}/data/${year}/players/${player}.json`);
    if (!response.ok) {
        return null;
    }
    return await response.json();
}

export async function getGame({ year, game }: { year: string, game: string }): Promise<Game | null> {
    const response = await fetch(`${BASE_URL}/data/${year}/games/${game}.json`);
    if (!response.ok) {
        return null;
    }
    return await response.json();
}

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

type RankedPlayer = PlayerRating & HasRanking;

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
    unavailable: string[];
}

export interface Division {
    name: string;
    id: string;
    sport: string;
    source: string;
    div: string;
}