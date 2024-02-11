
export default interface Data<T> {
    body: T
    lastModified?: Date

    map: <R>(mapper: (i: T) => R) => Data<R>
}

export function create<T>(body: T, lastModified?: Date) {
    return new DataInstance(body, lastModified);
}

class DataInstance<T> implements Data<T> {
    body: T;
    lastModified?: Date;

    constructor(body: T, lastModified?: Date) {
        this.body = body;
        this.lastModified = lastModified;
    }

    map<R>(mapper: (i: T) => R): Data<R> {
        return new DataInstance(mapper(this.body), this.lastModified);
    }
}
