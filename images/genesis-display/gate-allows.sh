#!/bin/sh
# exit 0 only if the gate answers allow:true. Unreachable or garbled = refuse (unsure = no).
curl -fsS -m 4 "${GATE_URL:-http://genesis-gate:8210/gate}" 2>/dev/null | python3 -c 'import json,sys; sys.exit(0 if json.load(sys.stdin)["allow"] is True else 1)' 2>/dev/null
