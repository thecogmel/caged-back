FROM python:3.13-alpine

ENV PATH="/app/.venv/bin:$PATH"

COPY --from=ghcr.io/astral-sh/uv:0.9.17 /uv /uvx /bin/

WORKDIR /usr/app

COPY . .
RUN uv sync --locked

CMD [ "uv", "run", "src/manage.py", "runserver", "0.0.0.0:8000" ]
EXPOSE 8000