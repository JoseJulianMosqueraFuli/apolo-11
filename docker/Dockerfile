# ---------- builder ----------
# Poetry and its build-time dependencies (e.g. msgpack) live only in this stage
# and never reach the final image.
FROM python:3.12-slim AS builder

WORKDIR /app

ENV POETRY_VIRTUALENVS_IN_PROJECT=true

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./
RUN poetry install --no-interaction --no-root --no-directory

COPY apolo_11/ apolo_11/
COPY main.py README.md ./

RUN poetry install --no-interaction

# Patch build tooling seeded into the venv (CVE-2025-47273 in setuptools)
RUN /app/.venv/bin/pip install --no-cache-dir --upgrade "setuptools>=78.1.1"

# ---------- runtime ----------
# Final image ships only the application and its runtime virtualenv — no Poetry,
# no msgpack, and a patched setuptools.
FROM python:3.12-slim AS runtime

WORKDIR /app

# Patch setuptools bundled in the base image as well (belt-and-suspenders)
RUN pip install --no-cache-dir --upgrade "setuptools>=78.1.1" \
    && rm -rf /root/.cache

COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/apolo_11 /app/apolo_11
COPY --from=builder /app/main.py /app/README.md ./

# The application runs from the virtualenv and never invokes pip at runtime.
# pip ships its own *vendored* copies of setuptools/msgpack under pip/_vendor,
# which scanners flag even though they are unused. Removing pip eliminates that
# vulnerable vendored code entirely and shrinks the attack surface.
RUN rm -rf /usr/local/lib/python3.12/site-packages/pip* \
           /app/.venv/lib/python3.12/site-packages/pip*

RUN addgroup --system apolo && adduser --system --ingroup apolo apolo \
    && mkdir -p /data/results && chown -R apolo:apolo /app /data/results

USER apolo

ENTRYPOINT ["/app/.venv/bin/apolo"]
CMD ["--dashboard", "--generator_interval", "3", "--reporter_interval", "10"]
