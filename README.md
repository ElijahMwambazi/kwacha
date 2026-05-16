# Kwacha!

Snap prices. Track change.

Kwacha! is a local price-tracking, cost-of-living, and personal inflation dashboard for Zambia.

It helps users capture everyday price snapshots, review raw collected prices, define a personal basket of goods, compare prices across shops, calculate personal basket inflation, export datasets, and experiment with simple price forecasting.

## Current Status

Kwacha! is in active local prototype development.

The project currently supports:

- Item management
- Price observation management
- Basket management
- Basket total calculation
- CSV exports
- CSV imports
- Raw price review queue
- Raw price approval/rejection workflow
- Bulk raw price review actions
- Duplicate detection for raw price approval
- Price trend analytics
- Shop comparison analytics
- Basket inflation tracking
- Public indicator tracking
- Indicator trend analytics
- ML-ready dataset export
- Moving-average forecast baseline
- Local scikit-learn model training
- Baseline vs ML prediction comparison
- Price model status/reset
- Model training-run history

## Project Goals

- Track everyday prices
- Normalize prices by unit
- Compare shops and locations
- Maintain a review queue for raw collected prices
- Calculate basket cost over time
- Track personal basket inflation
- Compare local price changes with public indicators
- Export clean datasets for analysis and model training
- Train basic forecasting models
- Serve simple predictions inside a local dashboard

## Tech Stack

### Frontend

- React
- TypeScript
- Vite
- Tailwind CSS
- Recharts

### Backend

- FastAPI
- SQLModel
- SQLite
- pandas
- scikit-learn
- joblib
- pytest

## Project Structure

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

## Main Workflows

### 1. Direct Price Tracking

A user can:

1. Create an item.
2. Add a price observation for that item.
3. Add the item to a basket.
4. View the current basket total.
5. Export item, price, or basket data as CSV.

### 2. Raw Price Review Workflow

A user can:

1. Add raw price rows manually.
2. Import raw price rows from CSV.
3. Review pending raw rows.
4. Edit raw rows before approval.
5. Approve rows into real price observations.
6. Reject rows that are incorrect.
7. Bulk approve or bulk reject pending rows.
8. Inspect pending, approved, and rejected review history.

This workflow prevents questionable imported or scraped data from immediately entering the approved price dataset.

### 3. Analytics Workflow

The dashboard can show:

- Price trends
- Shop comparison
- Basket inflation
- Public indicator trends
- Recent indicator readings
- Raw review queue stats

### 4. Forecasting Workflow

The backend supports two forecasting paths:

1. A simple moving-average baseline.
2. A trained local scikit-learn model.

The app can compare baseline and ML predictions side by side.

## Backend Setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs at:

```txt
http://127.0.0.1:8000
```

API docs:

```txt
http://127.0.0.1:8000/docs
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

```txt
http://localhost:5173
```

## Testing

```bash
cd backend
pytest
```

## Useful Exports

- `/export/items.csv`
- `/export/prices.csv`
- `/export/basket.csv`
- `/export/ml-prices.csv`

## Useful Imports

- `/imports/prices.csv`
- `/imports/raw-prices.csv`
- `/imports/prices-template.csv`
- `/imports/raw-prices-template.csv`

## Current Development Direction

The project is moving from a basic price tracker into a local cost-of-living intelligence tool.

The next documentation priorities are:

- API reference
- Data flow documentation
- Raw review workflow documentation
- Prediction and model training documentation
- Development setup notes
