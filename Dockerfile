FROM ghcr.io/astral-sh/uv:alpine
WORKDIR /usr/src/app

COPY . .

RUN uv sync --locked

CMD [ "uv", "run", "main.py" ]
