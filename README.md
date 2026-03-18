# Address Book API (FastAPI + SQLite)

Production-ready FastAPI project with:
- SQLite + SQLAlchemy ORM
- Alembic migrations
- Pydantic request/response validation
- CRUD, pagination, and nearby filtering (Haversine)
- Structured JSON logging + global exception handling
- Pytest unit tests

## Prerequisites
- Python 3.10+
- `pip`

## Setup
1. Install dependencies:
   ```bash
   python -m pip install -r requirements.txt
   ```
2. Configure environment:
   - Update `./.env` (already included).
   - Example values:
     - `DB_URL=sqlite:///./address_book.db`
     - `LOG_LEVEL=INFO`

## Database migrations (Alembic)
Initialize / apply the database schema:
```bash
alembic upgrade head
```

The initial migration creates the `addresses` table.

## Run the server
```bash
uvicorn app.main:app --reload
```

Health check:
```bash
GET /health
```

Server base URL:
- `http://127.0.0.1:8000`

## API Endpoints
CRUD:
- `POST /addresses` (create)
- `GET /addresses?limit=...&offset=...` (list with pagination)
- `GET /addresses/{id}` (get one)
- `PUT /addresses/{id}` (update)
- `DELETE /addresses/{id}` (delete)

Nearby filtering:
- `GET /addresses/nearby?lat=...&lon=...&distance=...`
- `distance` is in kilometers
- Filters via Haversine distance formula

Validation:
- `latitude` must be between `-90` and `90`
- `longitude` must be between `-180` and `180`

## Run tests
```bash
pytest -q
```

Tests cover:
- Create address
- List addresses (pagination)
- Get/update/delete flows
- Nearby filtering behavior

## Project Structure
```txt
app/
  main.py
  core/
    config.py
    logger.py
    exceptions.py
  db/
    base.py
    session.py
  models/
    address.py
  schemas/
    address.py
  crud/
    address.py
  api/
    routes/
      addresses.py
  utils/
    distance.py
tests/
  conftest.py
  test_addresses.py
alembic/
  env.py
  versions/
    0001_create_addresses_table.py
```

