#!/bin/bash
# Start API Server

cd "$(dirname "$0")"
source ../../venv/bin/activate
python -m backend.api_server
