# The official Shadow Linux app on the Selkies web desktop, plus a small start page (server.py) on port 8213.
FROM ghcr.io/linuxserver/baseimage-selkies:ubuntunoble
ARG SHADOW_DEB=https://update.shadow.tech/launcher/prod/linux/x86_64/shadow-amd64.deb
RUN apt-get update \
 && curl -fsSL -o /tmp/shadow.deb "$SHADOW_DEB" \
 && apt-get install -y --no-install-recommends /tmp/shadow.deb python3 procps \
 && rm -rf /tmp/shadow.deb /var/lib/apt/lists/*
COPY starter.py server.py /app/
COPY root/ /
