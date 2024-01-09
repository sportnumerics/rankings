import moment from "moment";

export function twoPlaces(rating?: number): string {
    return rating ? (Math.round(rating * 100) / 100.0).toString() : '';
}

export function datetime(date: string): string {
    return moment(date).format('M/D ha');
}

export function longDatetime(date: string): string {
    return moment(date).format('MMMM Do, h:mma');
}

export function date(date: string): string {
    return moment(date).format('M/D');
}