#!/bin/bash
# Startup script for Render
# This ensures PORT is properly set

PORT=${PORT:-8080}
exec gunicorn src.main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120

