import moment from "moment";

export function twoPlaces(rating: number): string {
    return (Math.round(rating * 100) / 100.0).toString();
}

export function datetime(date: string): string {
    return moment(date).format('M/D ha');
}

export function date(date: string): string {
    return moment(date).format('M/D');
}