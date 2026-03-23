#!/bin/bash

echo "Running database migrations..."
if alembic upgrade head 2>&1; then
    echo "Migrations completed successfully"
else
    echo "WARNING: Migrations failed (will retry on next deploy)"
fi

echo "Starting API server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
