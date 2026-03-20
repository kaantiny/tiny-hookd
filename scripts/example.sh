#!/bin/bash
# Example webhook script - receives JSON payload via stdin

# Read the payload
PAYLOAD=$(cat)

echo "Received webhook at $(date)"
echo "Payload: $PAYLOAD"

# Example: echo back with some processing
echo '{"status": "ok", "received": '$(echo "$PAYLOAD" | wc -c)' "bytes"}'
