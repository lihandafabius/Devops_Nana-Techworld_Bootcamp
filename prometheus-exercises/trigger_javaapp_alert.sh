#!/usr/bin/env bash
# Triggers the JavaAppTooManyRequests alert by sending parallel requests to /get-data.
#
# Usage:   ./trigger-java-load.sh <ingress-hostname> [total-requests] [parallel]
# Example: ./trigger-java-load.sh my-alb.elb.amazonaws.com 6000 20
#
# The alert fires when sum(rate(java_app_http_requests_total[1m])) > 10
# for 1 minute. If the rate stays below 10, raise [parallel] (e.g. 50).

HOST=$1
TOTAL=${2:-6000}
PARALLEL=${3:-20}

if [ -z "$HOST" ]; then
  echo "Usage: $0 <ingress-hostname> [total-requests] [parallel]"
  exit 1
fi

echo "Sending $TOTAL requests to http://$HOST/get-data ($PARALLEL in parallel)..."
seq 1 "$TOTAL" | xargs -P "$PARALLEL" -I{} curl -s -o /dev/null "http://$HOST/get-data"
echo "Done."