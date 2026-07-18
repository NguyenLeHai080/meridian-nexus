FROM python:3.13-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --requirement requirements.txt

RUN useradd --create-home --uid 10001 northstar

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
