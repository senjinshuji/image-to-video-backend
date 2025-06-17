#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Start the FastAPI application
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000