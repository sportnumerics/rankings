import 'server-only';
import { GetObjectCommand, ListObjectsV2Command, S3Client } from "@aws-sdk/client-s3";
import { promises } from "fs";
import { join } from "path";

interface Source {
    get(key: string): Promise<string>
    list(key: string): Promise<string[]>
}

class S3Source implements Source {
    readonly client = new S3Client({});
    readonly bucket = process.env.DATA_BUCKET;
    readonly prefix = process.env.DATA_BUCKET_PREFIX || 'data';

    async get(key: string) {
        const response = await this.client.send(new GetObjectCommand({
            Bucket: this.bucket,
            Key: `${this.prefix}/${key}`
        }))
        if (!response.Body) {
            throw new NotFoundError();
        }
        const body = await response.Body?.transformToString()
        return body;
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
        return await promises.readFile(join(this.basePath, key), 'utf8');
    }

    async list(key: string) {
        return await promises.readdir(join(this.basePath, key));
    }
}

export class NotFoundError extends Error {

}

class SourceLoader implements Source {
    source: Source | undefined;

    async get(key: string) {
        return this.cachedSource().get(key);
    }

    async list(key: string) {
        return this.cachedSource().list(key);
    }

    cachedSource() {
        if (!this.source) {
            this.source = getSource();
        }
        return this.source;
    }
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

const source = new SourceLoader();

export default source;