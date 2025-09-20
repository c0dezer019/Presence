FROM python:3.13.7-slim AS base

ENV PYTHONUNBUFFERED=1 \
    LANG=C.UTF-8 \
    PIP_NO_CACHE_DIR=1 \
    PIPENV_VENV_IN_PROJECT=1

WORKDIR /app

RUN pip install --upgrade pip \
    && pip install pipenv

FROM base AS deps

COPY Pipfile Pipfile.lock ./

RUN pipenv install --deploy --ignore-Pipfile

FROM base AS runtime

COPY --from=deps /app/.venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY . .

CMD ["pipenv", "run", "python", "main.py"]
