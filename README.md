# FastAPI Notes App

A minimal REST API for managing personal notes using FastAPI.

## Features

- Create, read, update, and delete notes (CRUD)
- Basic HTTP authentication
- PostgreSQL support via SQLAlchemy
- FastAPI + Uvicorn dev server

## Run Instructions

```bash
uv venv
source .venv/bin/activate
uv pip install fastapi uvicorn
uv pip install fastapi uvicorn sqlalchemy psycopg2-binary
uvicorn notess.main:app --reload

Username: admin
Password: password

curl -u admin:password http://127.0.0.1:8000/notes/

curl -X POST "http://127.0.0.1:8000/notes/" \
-u admin:password \
-H "Content-Type: application/json" \
-d '{"title": "Note 1", "content": "First note content"}'

curl -X GET "http://127.0.0.1:8000/notes/?skip=0&limit=10&search=Note" \
-u admin:password

curl -X GET "http://127.0.0.1:8000/notes/1" \
-u admin:password

curl -X PUT "http://127.0.0.1:8000/notes/1" \
-u admin:password \
-H "Content-Type: application/json" \
-d '{"title": "Updated title", "content": "Updated content"}'

curl -X DELETE "http://127.0.0.1:8000/notes/1" \
-u admin:password

