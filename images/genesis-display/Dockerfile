FROM debian:13-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
      retroarch libretro-nestopia libretro-mgba libretro-desmume libgl1-mesa-dri libegl1 libgbm1 libdrm2 libasound2t64 \
      alsa-utils udev gettext-base ca-certificates git curl python3 make g++ \
    && rm -rf /var/lib/apt/lists/*
# Controller profiles (Debian ships none), pinned commit from the 2026-10-19 spike.
RUN git init -q /opt/ac && cd /opt/ac && git remote add o https://github.com/libretro/retroarch-joypad-autoconfig \
 && git fetch -q --depth 1 o 7f94f847057c0829d4e18df27e50930728507f83 && git checkout -q FETCH_HEAD \
 && mkdir -p /opt/autoconfig && cp -r udev /opt/autoconfig/ && rm -rf /opt/ac
COPY *.py *.json *.lock *.sh retroarch.cfg.tmpl /app/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh /app/*.sh
ENTRYPOINT ["/entrypoint.sh"]
