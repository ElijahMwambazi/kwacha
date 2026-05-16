# Development Guide

This document explains how to run, test, and work on Kwacha! locally.

Kwacha! is currently a local-first prototype with:

- FastAPI backend
- SQLite database
- SQLModel ORM
- React + TypeScript frontend
- Vite dev server
- Tailwind CSS
- pandas/scikit-learn model experiments

## Repository Layout

```txt
kwacha/
  backend/
    app/
      ml/
      models/
      routes/
      database.py
      main.py
    tests/
    data/
    requirements.txt
    pyproject.toml

  frontend/
    src/
      api/
      types/
      App.tsx
      index.css
    package.json

  docs/
```

## Backend Setup

From the project root:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn app.main:app --reload
```

The backend should run at:

```txt
http://127.0.0.1:8000
```

Open API docs:

```txt
http://127.0.0.1:8000/docs
```

## Frontend Setup

From the project root:

```bash
cd frontend
npm install
npm run dev
```

The frontend should run at:

```txt
http://localhost:5173
```

## Running Both Apps

Use two terminals.

Terminal 1:

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Terminal 2:

```bash
cd frontend
npm run dev
```

## Backend Tests

Run all backend tests:

```bash
cd backend
pytest
```

Run one test file:

```bash
pytest tests/test_raw_collections_api.py
```

Run one test:

```bash
pytest tests/test_raw_collections_api.py::test_create_approve_raw_collection_creates_item_and_price
```

## Frontend Build Check

Run:

```bash
cd frontend
npm run build
```

This checks TypeScript and creates a production build.

## Current Quality Gate

Before committing, run:

```bash
cd backend
pytest
```

Then:

```bash
cd frontend
npm run build
```

Recommended commit only after both pass.

## Local Database

The backend uses SQLite.

The local database is stored under:

```txt
backend/data/
```

The app creates tables on startup.

## Resetting the Local Database

During early development, model/schema changes can break the existing SQLite database because `SQLModel.metadata.create_all()` creates missing tables but does not alter existing tables.

If routes fail after model changes, reset the local database:

```bash
cd backend
rm -f data/kwacha.db
uvicorn app.main:app --reload
```

Use this only for local development.

Later, Alembic migrations should replace manual database deletion.

## Common Backend Commands

Start backend:

```bash
uvicorn app.main:app --reload
```

Check import:

```bash
python -c "import app.main; print('ok')"
```

Run tests:

```bash
pytest
```

Inspect SQLite tables:

```bash
sqlite3 data/kwacha.db ".tables"
```

Inspect one table:

```bash
sqlite3 data/kwacha.db ".schema rawcollection"
```

## Common Frontend Commands

Install dependencies:

```bash
npm install
```

Start dev server:

```bash
npm run dev
```

Build:

```bash
npm run build
```

Preview production build:

```bash
npm run preview
```

## Environment Notes

The frontend expects the backend to be available at:

```txt
http://localhost:8000
```

or:

```txt
http://127.0.0.1:8000
```

If needed, use:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Then restart the frontend dev server.

## CORS Notes

The backend currently allows:

```txt
http://localhost:5173
http://127.0.0.1:5173
```

If the frontend shows a CORS error with `Status code: (null)`, the backend is usually not reachable.

Check:

```bash
curl http://127.0.0.1:8000/items
```

If that fails, the issue is not CORS. The backend is stopped, crashed, or running on a different port.

If the frontend shows a CORS error with `Status code: 500`, the backend likely crashed while handling the request. Check the backend terminal traceback.

## Common Errors

### `ModuleNotFoundError: No module named 'app'`

Run commands from the `backend/` directory.

Also confirm this exists in `backend/pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["."]
testpaths = ["tests"]
```

### `ModuleNotFoundError: No module named 'pp'`

This means the wrong uvicorn import path was used.

Wrong:

```bash
uvicorn pp.main:app --reload
```

Correct:

```bash
uvicorn app.main:app --reload
```

### `Import "fastapi" could not be resolved`

The virtual environment is not selected or dependencies are not installed.

Fix:

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
```

Then select the backend virtual environment in the editor.

### Vite cannot resolve `react-is`

Install dependencies again:

```bash
cd frontend
npm install
```

If needed:

```bash
npm install react-is
```

### TypeScript complains about `.at()`

Avoid `.at()` or use a newer TypeScript lib target.

Safer code:

```ts
const latest = rows[rows.length - 1];
```

### Unknown Tailwind `@apply`

This project uses Tailwind CSS with Vite. If editor CSS linting complains about `@apply`, the app can still build. If build fails, check Tailwind/Vite configuration.

### FastAPI route returns 422 for `/bulk/approve`

Route order matters.

Static routes must come before dynamic routes.

Correct order:

```txt
@router.get("/stats")
@router.post("/bulk/approve")
@router.post("/bulk/reject")
@router.patch("/{raw_collection_id}")
@router.post("/{raw_collection_id}/approve")
@router.post("/{raw_collection_id}/reject")
@router.delete("/{raw_collection_id}")
```

If `/bulk/approve` appears below `/{raw_collection_id}`, FastAPI may parse `bulk` as an integer ID and return 422.

## Current Backend Route Groups

The backend mounts these route groups:

```txt
/health
/items
/prices
/basket
/analytics
/export
/imports
/indicators
/predictions
/raw-collections
```

## Testing Organization

Backend tests are organized by feature area.

Examples:

```txt
tests/test_items_api.py
tests/test_prices_api.py
tests/test_basket_api.py
tests/test_exports_api.py
tests/test_imports_api.py
tests/test_analytics_api.py
tests/test_indicators_api.py
tests/test_predictions_api.py
tests/test_raw_collections_api.py
```

Avoid broad milestone names like:

```txt
test_phase1_api.py
```

Prefer domain-specific test files.

## Development Workflow

Recommended workflow:

```txt
1. Confirm current tests pass.
2. Make a small backend or frontend change.
3. Add/update tests.
4. Run pytest.
5. Run npm run build.
6. Update docs if behavior changed.
7. Commit.
```

## Commit Message Style

Use concise conventional-style messages.

Examples:

```txt
feat(raw): add duplicate detection for approvals
feat(imports): add raw price import template
feat(predictions): compare baseline and ML price forecasts
docs: update API reference
test: split API tests by feature area
fix(raw): order bulk routes before dynamic routes
```

## Current Implementation Notes

### Raw Collections

Raw collections are the preferred path for uncertain data.

Use them for:

- CSV imports
- manually collected prices
- future scraper data
- future crowdsourced prices

Only approved raw rows become price observations.

### Price Observations

Price observations are trusted data.

They power:

- basket totals
- analytics
- exports
- predictions
- model training

### Public Indicators

Indicators are manually entered for now.

They are used by:

- indicator trend charts
- ML export
- ML model features

### Predictions

The moving-average prediction works without training.

The ML prediction requires:

```txt
POST /predictions/train-price-model
```

A trained model is stored locally with `joblib`.

## Known Technical Debt

### Backend

- Add Alembic migrations.
- Replace deprecated `@app.on_event("startup")` with lifespan.
- Replace `datetime.utcnow()` with timezone-aware UTC timestamps.
- Add pagination.
- Add stronger validation schemas.
- Add service layer for raw approval logic.
- Remove duplicate route definitions if they appear during manual edits.

### Frontend

- Split `App.tsx` into feature components.
- Replace prompt-based editing with a real modal/form.
- Add route-based navigation.
- Add granular loading states.
- Add better error display.
- Add reusable table/card components.

### Data/ML

- Improve duplicate detection.
- Add item aliases.
- Add model evaluation reports.
- Add feature documentation.
- Add seed/sample data.
- Add better model comparison metrics.

## Before Asking for Help

When reporting an issue, include:

```txt
1. Command run
2. Full error output
3. Backend or frontend?
4. File changed last
5. pytest or npm build result
```

For backend errors, the most useful output is the traceback from the terminal running:

```bash
uvicorn app.main:app --reload
```

For frontend errors, include the browser console message and the terminal output from:

```bash
npm run dev
```
