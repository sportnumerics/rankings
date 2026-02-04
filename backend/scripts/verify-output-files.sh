#!/bin/bash
set -euo pipefail

# Verify that the backend pipeline produced the expected output files.
# Usage: ./verify-output-files.sh <year> [output_dir] [max_schedules]

YEAR="${1:?Usage: $0 <year> [output_dir] [max_schedules]}"
OUTPUT_DIR="${2:-out}"
MAX_SCHEDULES="${3:-}"

echo "Checking for required output files in ${OUTPUT_DIR}/${YEAR}..."

# Check team list exists
if [ ! -f "${OUTPUT_DIR}/${YEAR}/mcla-teams.json" ]; then
  echo "ERROR: mcla-teams.json not found"
  exit 1
fi
echo "  Found mcla-teams.json"

# Check schedules directory exists
if [ ! -d "${OUTPUT_DIR}/${YEAR}/schedules" ]; then
  echo "ERROR: schedules directory not found"
  exit 1
fi

# Count schedule files
schedule_count=$(find "${OUTPUT_DIR}/${YEAR}/schedules" -name "*.json" -type f 2>/dev/null | wc -l)
echo "  Found ${schedule_count} schedule files"

if [ "$schedule_count" -eq 0 ]; then
  echo "ERROR: No schedule files found"
  exit 1
fi

if [ -n "$MAX_SCHEDULES" ] && [ "$schedule_count" -gt "$MAX_SCHEDULES" ]; then
  echo "WARNING: Expected max ${MAX_SCHEDULES} schedule files, found ${schedule_count}"
fi

# Check team ratings exist
if [ ! -f "${OUTPUT_DIR}/${YEAR}/team-ratings.json" ]; then
  echo "ERROR: team-ratings.json not found"
  exit 1
fi
echo "  Found team-ratings.json"

echo "All required output files exist"
