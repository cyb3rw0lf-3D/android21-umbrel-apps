# The official Shadow Linux app on the Selkies web desktop, plus a small start page (server.py) on port 8213.
FROM ghcr.io/linuxserver/baseimage-selkies:ubuntunoble
ARG SHADOW_DEB=https://update.shadow.tech/launcher/prod/linux/x86_64/shadow-amd64.deb
# Shadow signs in through a web browser and comes back through a tech.shadow:// link, so this needs a browser
# (Mozilla's own Firefox package; Ubuntu's is a snap) and xdg-utils to route that link back to the app.
RUN install -d -m 0755 /etc/apt/keyrings \
 && curl -fsSL https://packages.mozilla.org/apt/repo-signing-key.gpg -o /etc/apt/keyrings/packages.mozilla.org.asc \
 && echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" > /etc/apt/sources.list.d/mozilla.list \
 && printf 'Package: *\nPin: origin packages.mozilla.org\nPin-Priority: 1000\n' > /etc/apt/preferences.d/mozilla \
 && apt-get update \
 && curl -fsSL -o /tmp/shadow.deb "$SHADOW_DEB" \
 && apt-get install -y --no-install-recommends /tmp/shadow.deb python3 procps firefox xdg-utils desktop-file-utils \
 && update-desktop-database /usr/share/applications \
 && rm -rf /tmp/shadow.deb /var/lib/apt/lists/*
COPY starter.py server.py /app/
COPY root/ /
