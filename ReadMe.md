# Petstore API

A simple REST API built with Flask and flask-restx, with a pytest test suite and GitHub Actions CI.

## Project Structure

```
pytest-api-example/
├── .github/
│   └── workflows/
│       └── pytest.yml       # GitHub Actions CI workflow
├── app.py                   # Flask API
├── api_helpers.py           # HTTP helper functions for tests
├── schemas.py               # JSON schemas for response validation
├── test_pet.py              # Tests for /pets endpoints
├── test_store.py            # Tests for /store endpoints
└── requirements.txt         # Project dependencies
```

## Setup

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # Mac/Linux
venv\Scripts\activate           # Windows

# Install dependencies
pip install -r requirements.txt
```

## Running the API

```bash
python app.py
```

API will be available at `http://127.0.0.1:5000`  
Swagger docs at `http://127.0.0.1:5000`

## Running Tests

```bash
# Run all tests
pytest test_pet.py test_store.py -v

# Run pet tests only
pytest test_pet.py -v

# Run store tests only
pytest test_store.py -v
```

## CI/CD

GitHub Actions workflow runs automatically on every push.  
Results are visible under the **Actions** tab in the repository.

## Known Bugs

| # | Location | Description |
|---|---|---|
| 1 | `schemas.py` line 9 | `name` typed as `integer` instead of `string` |
| 2 | `app.py` line 101 | Missing f-string in `findByStatus` abort message |
| 3 | `app.py` | `POST /pets` missing `validate=True` — accepts invalid enum values |
| 4 | `app.py` | `POST /pets` allows client-supplied IDs |
| 5 | `app.py` | No `DELETE` endpoints — fixed by adding DELETE to `app.py` and `api_helpers.py` |
| 6 | `app.py` | `PATCH /order` mutates state before validating status |
| 7 | `app.py` | `findByStatus` returns misleading error when status param is missing |