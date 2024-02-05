#!/usr/bin/env bash

if [ -z "$1" ]; then
    echo "Usage: $0 <year> [<source>] [<target>]"
    exit 1
fi

year=${1}
source=${2:-prod}
target=${3:-dev}

aws s3 sync s3://sportnumerics-rankings-bucket-$source/data/$year s3://sportnumerics-rankings-bucket-$target/data/$year