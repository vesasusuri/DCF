# DCF

Full-stack DCF application with a React + Vite frontend, FastAPI backend, and Supabase database.

## Stack

- **Frontend:** React 19 + Vite + TypeScript
- **Backend:** Python FastAPI
- **Database:** Supabase (PostgreSQL)

## Project structure

```
DCF/
├── frontend/          # React + Vite app
├── backend/           # FastAPI API
├── supabase/          # SQL schema
├── .env               # Local environment variables (not committed)
└── .env.example       # Environment variable template
```

## Prerequisites

- Node.js 20+
- Python 3.12+
- A [Supabase](https://supabase.com) project

## Setup

### 1. Environment variables

Copy the example env file and fill in your Supabase credentials:

```bash
cp .env.example .env
```

Also copy frontend env values (or symlink):

```bash
cp .env.example frontend/.env
```

Set these from your Supabase project settings (API):

- `SUPABASE_URL`
- `SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY`
- `VITE_SUPABASE_URL` (same as `SUPABASE_URL`)
- `VITE_SUPABASE_ANON_KEY` (same as `SUPABASE_ANON_KEY`)

### 2. Database schema

In the Supabase SQL editor, run:

```
supabase/schema.sql
```

### 3. Backend

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

### 4. Frontend

```bash
cd frontend
npm install
npm run dev
```

App: http://localhost:5173

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/` | API welcome message |
| GET | `/api/v1/health` | Health check |
| GET | `/api/v1/models` | List DCF models from Supabase |

## Development notes

- The Vite dev server proxies `/api` requests to the FastAPI backend.
- The backend uses the Supabase service role key for server-side database access.
- The frontend uses the Supabase anon key via `@supabase/supabase-js` for client-side access.
