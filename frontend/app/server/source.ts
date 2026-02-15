import { cache } from 'react';
import 'server-only';
import { GetObjectCommand, ListObjectsV2Command, S3Client } from "@aws-sdk/client-s3";
import { promises } from "fs";
import { join } from "path";
import Data, { create } from './Data';

interface Source {
    get(key: string): Promise<Data<any>>
    list(key: string): Promise<string[]>
}


class S3Source implements Source {
    readonly client = new S3Client({});
    readonly bucket = process.env.DATA_BUCKET;
    readonly prefix = process.env.DATA_BUCKET_PREFIX || 'data';

    async get(key: string) {
        try {
            const response = await this.client.send(new GetObjectCommand({
                Bucket: this.bucket,
                Key: `${this.prefix}/${key}`
            }))
            if (!response.Body) {
                throw new NotFoundError();
            }
            return create(
                JSON.parse(await response.Body?.transformToString()),
                response.LastModified
            );
        } catch (err: any) {
            if (err.name === 'NoSuchKey' || err.$metadata?.httpStatusCode === 404) {
                throw new NotFoundError();
            }
            throw err;
        }
    }

    async list(key: string): Promise<string[]> {
        const response = await this.client.send(new ListObjectsV2Command({
            Bucket: this.bucket,
            Prefix: `${this.prefix}/${key}`,
            Delimiter: '/'
        }))
        if (!response.CommonPrefixes) {
            throw new NotFoundError();
        }
        const prefix = new RegExp(`^${this.prefix}/${key}`);
        const suffix = /\/$/
        const keys = response.CommonPrefixes.map(obj => obj.Prefix?.replace(prefix, '').replace(suffix, '')) as string[];
        return keys;
    }
}

class LocalFileSource implements Source {
    readonly basePath = process.env.DATA_PATH || '';

    async get(key: string) {
        try {
            const filename = join(this.basePath, key);
            const [stats, file] = await Promise.all([promises.stat(filename), promises.readFile(filename, 'utf8')]);
            return create(
                JSON.parse(file),
                stats.mtime
            );
        } catch (err: any) {
            if (err.code === 'ENOENT') {
                throw new NotFoundError();
            }
            throw err;
        }
    }

    async list(key: string) {
        return await promises.readdir(join(this.basePath, key));
    }
}

class CachedSource implements Source {
    readonly origin: Source;
    readonly ttl: number;
    objectCache: (key: string) => Promise<Data<any>>;
    listCache: (key: string) => Promise<string[]>;

    constructor(origin: Source, ttl: number) {
        this.origin = origin;
        this.ttl = ttl;
        this.objectCache = cache(k => origin.get(k))
        this.listCache = cache(k => origin.list(k));
    }

    async get(key: string) {
        return this.objectCache(key);
    }

    async list(key: string) {
        return this.listCache(key);
    }
}

export class NotFoundError extends Error {

}

function getSource(): Source {
    if (process.env.DATA_BUCKET) {
        return new S3Source();
    } else if (process.env.DATA_PATH) {
        return new LocalFileSource();
    } else {
        throw new Error('No data source provided, set DATA_BUCKET or DATA_PATH environment variables');
    }
}

const source = new CachedSource(getSource(), 600);

export default source;