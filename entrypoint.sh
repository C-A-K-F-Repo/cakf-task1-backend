#!/bin/bash
set -e

# Run database migrations
alembic merge heads
uv run alembic upgrade head

# Start the application with any passed arguments
exec uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
