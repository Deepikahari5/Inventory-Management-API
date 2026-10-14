#!/usr/bin/env bash
cd "$(dirname "$0")"
[ -d venv ] || python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
if [ ! -f .env ]; then
  cp .env.example .env
  echo ".env created from .env.example - set DB_PASSWORD in .env, then run ./run.sh again."
  exit 0
fi
alembic upgrade head
uvicorn app.main:app --reload
