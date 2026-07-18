FROM python:3.13-alpine@sha256:399babc8b49529dabfd9c922f2b5eea81d611e4512e3ed250d75bd2e7683f4b0 AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --requirement requirements.txt

RUN addgroup --gid 10001 northstar \
    && adduser --disabled-password --uid 10001 --ingroup northstar northstar

FROM base AS development
COPY requirements-dev.txt ./
RUN pip install --requirement requirements-dev.txt
COPY --chown=northstar:northstar northstar ./northstar
COPY --chown=northstar:northstar migrations ./migrations
COPY --chown=northstar:northstar pyproject.toml ./
USER northstar

FROM base AS production
COPY --chown=northstar:northstar northstar ./northstar
COPY --chown=northstar:northstar migrations ./migrations
COPY --chown=northstar:northstar pyproject.toml ./
USER northstar

EXPOSE 8000

CMD ["uvicorn", "northstar.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-server-header"]
