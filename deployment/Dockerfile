FROM python:3.14-slim-bookworm

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN groupadd -g 1000 appuser && \
    useradd -m -u 1000 -g appuser appuser

ENV WORKDIR=/app \
    UV_CACHE_DIR=/home/appuser/.cache/uv \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

WORKDIR $WORKDIR

RUN chown appuser:appuser $WORKDIR

USER appuser

COPY --chown=appuser:appuser pyproject.toml uv.lock ./

RUN uv sync --frozen --no-install-project --no-dev

COPY --chown=appuser:appuser . .

COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
