FROM python:3.12-slim

WORKDIR /app

RUN pip install poetry --quiet

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-root --no-directory

COPY apolo_11/ apolo_11/
COPY main.py README.md ./

RUN poetry install --no-interaction

ENTRYPOINT ["poetry", "run", "apolo"]
CMD ["--dashboard", "--generator_interval", "3", "--reporter_interval", "10"]
