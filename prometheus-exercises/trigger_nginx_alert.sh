#!/usr/bin/env bash
HOST=$1
COUNT=${2:-600}
for i in $(seq 1 $COUNT); do
  curl -s -o /dev/null http://$HOST/path-that-doesnt-exist
  sleep 0.2
done