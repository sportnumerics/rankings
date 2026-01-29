import { NextResponse } from 'next/server';
import { S3Client, ListObjectsV2Command } from '@aws-sdk/client-s3';

export const dynamic = 'force-dynamic';

export async function GET() {
  const health = {
    ok: true,
    timestamp: new Date().toISOString(),
    gitSha: process.env.GIT_SHA || process.env.VERCEL_GIT_COMMIT_SHA || 'unknown',
    buildTime: process.env.BUILD_TIME || 'unknown',
    environment: process.env.NODE_ENV || 'unknown',
  };

  // Optional: check S3 connectivity
  if (process.env.DATA_BUCKET) {
    try {
      const client = new S3Client({});
      const prefix = process.env.DATA_BUCKET_PREFIX || 'data';
      
      await client.send(new ListObjectsV2Command({
        Bucket: process.env.DATA_BUCKET,
        Prefix: prefix,
        MaxKeys: 1,
      }));
      
      Object.assign(health, {
        s3: {
          bucket: process.env.DATA_BUCKET,
          accessible: true,
        },
      });
    } catch (error) {
      Object.assign(health, {
        s3: {
          bucket: process.env.DATA_BUCKET,
          accessible: false,
          error: error instanceof Error ? error.message : 'Unknown error',
        },
        ok: false,
      });
    }
  }

  return NextResponse.json(health, {
    status: health.ok ? 200 : 503,
  });
}
