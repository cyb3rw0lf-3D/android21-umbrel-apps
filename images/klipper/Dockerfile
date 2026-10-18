# Pip layer only: Klipper's own source tree is bind-mounted at runtime (the user's tree, custom extras included).
# gcc/libffi: klippy compiles its c_helper.so on first start.
FROM python:3.12-slim
LABEL org.opencontainers.image.source="https://github.com/cyb3rw0lf-3D/android21-umbrel-apps"
RUN apt-get update && apt-get install -y --no-install-recommends gcc libffi-dev libc6-dev \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt
