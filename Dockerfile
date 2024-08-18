FROM python:3.10-slim-buster

ENV PYTHONUNBUFFERED 1

# Install ffmpeg
RUN apt update && apt install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Install python requirements
COPY requirements.txt /
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app/
