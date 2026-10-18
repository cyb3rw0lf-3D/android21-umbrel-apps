# Pip layer only: Moonraker's source tree is bind-mounted at runtime.
FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/cyb3rw0lf-3D/android21-umbrel-apps"
RUN apt-get update && apt-get install -y --no-install-recommends gcc libffi-dev libc6-dev \
      libsodium23 libjpeg62-turbo zlib1g liblmdb0 \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
