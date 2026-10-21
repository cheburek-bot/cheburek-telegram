FROM ghcr.io/astral-sh/uv:alpine
WORKDIR /usr/src/app

COPY . .

RUN uv sync

CMD [ "uv", "run", "main.py" ]
