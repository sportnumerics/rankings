import moment from "moment";

export function twoPlaces(rating?: number): string {
    return rating ? (Math.round(rating * 100) / 100.0).toString() : '--';
}

export function datetime(date: string): string {
    const m = moment(date);
    if (date.includes('T')) {
        return m.format('M/D ha');
    } else {
        return m.format('M/D');
    }
}

export function longDatetime(date: string): string {
    const m = moment(date);
    if (date.includes('T')) {
        return m.format('MMMM Do, h:mma');
    } else {
        return m.format('MMMM Do');
    }
}

export function date(date: string): string {
    return moment(date).format('M/D');
}