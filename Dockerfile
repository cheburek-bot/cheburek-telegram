FROM ghcr.io/astral-sh/uv:alpine
WORKDIR /usr/src/app

COPY . .

RUN uv sync

RUN apk update && apk add --no-cache ffmpeg

CMD [ "uv", "run", "main.py" ]
