
export interface Result<T> {
    value?: T;
    error?: any;
    loading: boolean;
}


export function loading<T>(): Result<T> {
    return { loading: true };
}

export function success<T>(value: T) {
    return { value, loading: false };
}

export function error<T>(error: any) {
    return { error, loading: false };
}