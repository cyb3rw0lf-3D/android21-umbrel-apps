FROM python:3.12-slim
COPY gate.py server.py /app/
WORKDIR /app
USER 1000
CMD ["python3", "-u", "server.py"]
