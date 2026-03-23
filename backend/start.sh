#!/bin/bash

echo "Running database migrations..."
alembic upgrade head || echo "WARNING: Migrations failed (will retry on next deploy)"

echo "Starting API server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
