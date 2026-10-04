#!/bin/bash
# queue_worker.sh - runs build jobs one after another (render jobs share the 4 CPU cores).
# Jobs are files in $Q/*.job (one shell command each), run in name order, then moved to $Q/done/.
Q=${1:-/tmp/wo_queue}
mkdir -p "$Q/done"
cd "$(dirname "$0")/.."
while true; do
  job=$(ls "$Q"/*.job 2>/dev/null | head -1)
  if [ -z "$job" ]; then
    [ -f "$Q/stop" ] && exit 0
    sleep 3; continue
  fi
  name=$(basename "$job" .job)
  echo "=== $(date +%H:%M:%S) start $name" >> "$Q/worker.log"
  bash "$job" > "$Q/done/$name.log" 2>&1
  echo "=== $(date +%H:%M:%S) end $name (exit $?)" >> "$Q/worker.log"
  mv "$job" "$Q/done/"
done
