import 'server-only';
import { GetObjectCommand, S3Client } from "@aws-sdk/client-s3";
import { promises } from "fs";
import { join } from "path";

interface Source {
    get(key: string): Promise<string>
}

class S3Source implements Source {
    readonly client = new S3Client({});
    readonly bucket = process.env.DATA_BUCKET;

    async get(key: string) {
        const response = await this.client.send(new GetObjectCommand({
            Bucket: this.bucket,
            Key: key
        }))
        if (!response.Body) {
            throw new NotFoundError();
        }
        const body = await response.Body?.transformToString()
        return body;
    }
}

class LocalFileSource implements Source {
    readonly basePath = process.env.DATA_PATH || '';

    async get(key: string) {
        return await promises.readFile(join(this.basePath, key), 'utf8');
    }
}

export class NotFoundError extends Error {

}

class SourceLoader implements Source {
    source: Source | undefined;

    async get(key: string) {
        if (!this.source) {
            this.source = getSource();
        }
        return this.source.get(key);
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