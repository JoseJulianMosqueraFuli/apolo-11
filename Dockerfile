FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry --quiet

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-root --no-directory

COPY apolo_11/ apolo_11/
COPY main.py README.md ./

RUN poetry install --no-interaction

RUN addgroup --system apolo && adduser --system --ingroup apolo apolo

RUN mkdir -p /data/results && chown -R apolo:apolo /app /data/results

USER apolo

ENTRYPOINT ["/app/.venv/bin/apolo"]
CMD ["--dashboard", "--generator_interval", "3", "--reporter_interval", "10"]
