@echo off
cd /d %~dp0
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate
pip install -r requirements.txt
if not exist .env (
    copy .env.example .env
    echo.
    echo .env created from .env.example - set DB_PASSWORD in .env, then run run.bat again.
    pause
    exit /b
)
alembic upgrade head
uvicorn app.main:app --reload
