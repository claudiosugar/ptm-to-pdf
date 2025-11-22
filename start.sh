#!/bin/bash
# Startup script for Render
# This ensures PORT is properly set

PORT=${PORT:-8080}
# Increased timeout for PDF generation, reduced workers for memory efficiency
exec gunicorn src.main:app --bind 0.0.0.0:$PORT --workers 1 --timeout 600 --graceful-timeout 30

