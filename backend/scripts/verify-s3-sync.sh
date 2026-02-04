#!/bin/bash
set -euo pipefail

# Verify that files were synced to S3 correctly.
# Usage: ./verify-s3-sync.sh <year> <s3_bucket_url>

YEAR="${1:?Usage: $0 <year> <s3_bucket_url>}"
S3_BUCKET_URL="${2:?Usage: $0 <year> <s3_bucket_url>}"

echo "Verifying files were synced to ${S3_BUCKET_URL}..."

# Check if year directory exists in S3
if ! aws s3 ls "${S3_BUCKET_URL}/${YEAR}/" > /dev/null 2>&1; then
  echo "ERROR: Year directory not found in S3"
  exit 1
fi
echo "  Found ${YEAR}/ directory"

# Check for team list
if ! aws s3 ls "${S3_BUCKET_URL}/${YEAR}/mcla-teams.json" > /dev/null 2>&1; then
  echo "ERROR: mcla-teams.json not found in S3"
  exit 1
fi
echo "  Found mcla-teams.json"

# Check for team ratings
if ! aws s3 ls "${S3_BUCKET_URL}/${YEAR}/team-ratings.json" > /dev/null 2>&1; then
  echo "ERROR: team-ratings.json not found in S3"
  exit 1
fi
echo "  Found team-ratings.json"

echo "Files successfully synced to S3"
