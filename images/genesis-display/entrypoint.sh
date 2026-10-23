#!/bin/sh
# Render the RetroArch config, expose the Debian cores next to the source-built ones in /cores, then run RetroArch's own
# menu (the guaranteed floor). The Task 6 launcher choice and the supervisor loop are wired in after the hardware spike.
set -e
export AUDIO_DRIVER=${AUDIO_DRIVER:-alsa} AUDIO_DEVICE=${AUDIO_DEVICE:-default}
mkdir -p /data/saves /data/states /data/bios /data/config /cores
for c in nestopia mgba desmume; do ln -sf /usr/lib/x86_64-linux-gnu/libretro/${c}_libretro.so /cores/${c}_libretro.so; done
envsubst < /app/retroarch.cfg.tmpl > /data/config/retroarch.cfg
exec nice -n 5 retroarch --config /data/config/retroarch.cfg
