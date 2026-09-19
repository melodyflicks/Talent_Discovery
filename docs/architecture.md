# Architecture

The UI calls FastAPI under `/api/v1`. Domain services will coordinate SQLAlchemy persistence, isolated AI modules, and optional adapter integrations. PostgreSQL with pgvector is the intended production-like local datastore; JSON catalogs make the scaffold runnable without external APIs.
