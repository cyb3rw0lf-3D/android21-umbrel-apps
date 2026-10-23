#!/bin/bash
# verify-cores.sh <dir>: every non-optional core in cores.lock must exist and match its sha256 ("-" = not recorded yet = fail).
DIR=${1:?usage: verify-cores.sh <dir>}
HERE=$(cd "$(dirname "$0")" && pwd)
bad=0
while read -r name repo commit sha dir mk opt; do
  case "$name" in ''|'#'*) continue;; esac
  f="$DIR/${name}_libretro.so"
  if [ ! -f "$f" ]; then [ "$opt" = optional ] || { echo "MISSING $name"; bad=1; }; continue; fi
  [ "$sha" = "-" ] && { echo "NO CHECKSUM RECORDED $name"; bad=1; continue; }
  [ "$(sha256sum "$f" | cut -d' ' -f1)" = "$sha" ] || { echo "MISMATCH $name"; bad=1; }
done < "$HERE/cores.lock"
exit $bad
