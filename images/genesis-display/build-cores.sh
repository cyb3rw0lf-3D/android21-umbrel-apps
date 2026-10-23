#!/bin/bash
# build-cores.sh <outdir>: build the libretro cores in cores.lock from their pinned commits into <outdir>.
# Low priority (nice 19, one job), refuses to start while the printer rule says no, and stops mid-build if it flips.
set -u
OUT=${1:?usage: build-cores.sh <outdir>}
HERE=$(cd "$(dirname "$0")" && pwd)
WORK=${WORK:-$OUT/.build}
"$HERE/gate-allows.sh" || { echo "gate says no (printing, or printer state unreadable): not building" >&2; exit 3; }
mkdir -p "$OUT" "$WORK"
fail=0
while read -r name repo commit sha dir mk opt; do
  case "$name" in ''|'#'*) continue;; esac
  [ -f "$OUT/${name}_libretro.so" ] && [ "$sha" != "-" ] && [ "$(sha256sum "$OUT/${name}_libretro.so" | cut -d' ' -f1)" = "$sha" ] && { echo "$name: already built"; continue; }
  src="$WORK/$name"; rm -rf "$src"; mkdir -p "$src"
  ( cd "$src" && git init -q && git remote add origin "https://github.com/$repo" && git fetch -q --depth 1 origin "$commit" && git checkout -q FETCH_HEAD ) \
    || { echo "$name: fetch failed" >&2; fail=1; continue; }
  ( cd "$src/$dir" && exec nice -n 19 make -j1 -f "$mk" ) > "$WORK/$name.log" 2>&1 &
  pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    sleep 10
    "$HERE/gate-allows.sh" || { kill -TERM "$pid" 2>/dev/null; pkill -TERM -P "$pid" 2>/dev/null; echo "gate flipped: build stopped" >&2; exit 3; }
  done
  wait "$pid" || { echo "$name: build failed (see $WORK/$name.log)" >&2; [ "$opt" = optional ] || fail=1; continue; }
  so=$(find "$src" -name "${name}_libretro.so" | head -1)
  [ -n "$so" ] && cp "$so" "$OUT/" && echo "$name $(sha256sum "$OUT/${name}_libretro.so" | cut -d' ' -f1)" || { echo "$name: no .so produced" >&2; fail=1; }
done < "$HERE/cores.lock"
exit $fail
