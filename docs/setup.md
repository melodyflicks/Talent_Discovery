# Setup

Copy `.env.example` to `.env`. Start the frontend with `npm install && npm run dev` inside `frontend`. Create a Python virtual environment, install `backend/requirements.txt`, and run `uvicorn app.main:app --reload` from `backend`. Use a local PostgreSQL instance with pgvector when persistence work starts.
