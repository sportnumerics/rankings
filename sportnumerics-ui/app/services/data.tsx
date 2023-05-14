
export async function getTeams({ year, source }: { year: string, source: string }): Promise<TeamMap> {
    const response = await fetch(`${process.env.BASE_URL}/${year}/${source}-teams.json`);
    const teams: Team[] = await response.json();
    return Object.fromEntries(teams.map(team => [team.id, team]));
}

export async function getRankedTeamsByDiv({ year, source, div }: { year: string, source: string, div: string }): Promise<RankedTeamMap> {
    const teamsPromise = getTeams({year, source});
    const ratingsPromise = getRatings({year});
    const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
    const teamRatings = Object.values(teams)
        .filter(team => team.source === source && team.div === div)
        .map(team => ({...team, ...ratings[team.id]}));
    teamRatings.sort((a, b) => b.overall - a.overall);
    return Object.fromEntries(teamRatings.map((team, i) => [team.id, {...team, rank: i + 1}]));
}

export async function getTeamSchedule({ year, id }: { year: string, id: string }): Promise<TeamSchedule> {
    const response = await fetch(`${process.env.BASE_URL}/${year}/schedules/${id}.json`);
    return await response.json();
}

export async function getRatings({ year }: { year: string}): Promise<RatingMap> {
    const response = await fetch(`${process.env.BASE_URL}/${year}/team-ratings.json`);
    const ratings: TeamRating[] = await response.json();
    return Object.fromEntries(ratings.map(rating => [rating.team, rating]));
}

export async function getPlayerRatings({ year }: {year: string}): Promise<PlayerRatingMap> {
    const response = await fetch(`${process.env.BASE_URL}/${year}/player-ratings.json`);
    const ratings: PlayerRating[] = await response.json();
    return Object.fromEntries(ratings.map(rating => [rating.id, rating]));
}

export async function getRankedPlayersByDiv({ year, source, div }: { year: string, source: string, div: string }): Promise<RankedPlayerMap> {
    const teamsPromise = getTeams({year, source});
    const ratingsPromise = getPlayerRatings({ year });
    const [teams, ratings] = await Promise.all([teamsPromise, ratingsPromise]);
    const playerRatings = Object.values(ratings)
        .filter(player => {
            const team = teams[player.team.id];
            return team.source === source && team.div === div;
        });
    playerRatings.sort((a, b) => b.points - a.points);
    return Object.fromEntries(playerRatings.map((player, i) => [player.id, {...player, rank: i + 1}]));
}

export async function getRankedPlayersByTeam({ year, team }: { year: string, team: string }): Promise<RankedPlayerMap> {
    const ratings = await getPlayerRatings({ year });
    const players = Object.values(ratings)
        .filter(player => player.team.id === team);
    players.sort((a, b) => b.points - a.points);
    return Object.fromEntries(players.map((player, i) => [player.id, {...player, rank: i + 1}]));
}

export async function getPlayerStats({ year, id }: { year: string, id: string }): Promise<PlayerStats> {
    const response = await fetch(`${process.env.BASE_URL}/${year}/players/${id}.json`);
    return await response.json();
}

export async function getGame({ year, id }: { year: string, id: string }): Promise<Game> {
    const response = await fetch(`${process.env.BASE_URL}/${year}/games/${id}.json`);
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