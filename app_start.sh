#!/bin/bash
set -e

echo "Starting application..."
uvicorn src.main:app \
        --host "$APP_HOST" \
        --port "$APP_PORT" \
        --log-level "$APP_LOG_LEVEL" \
        --reload