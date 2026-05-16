# Project Status

Kwacha! has moved beyond the first milestone.

The app is now a local prototype for price tracking, basket inflation, raw data review, analytics, and early forecasting.

## Completed Areas

### Core Price Tracking

- Create, list, update, and delete items
- Create, list, update, and delete price observations
- Normalize price observations by price per unit
- Create, update, remove, and list basket items
- Calculate basket totals from latest price observations
- Handle basket items with missing price history

### CSV Export

- Export items
- Export price observations
- Export basket totals
- Export ML-ready price dataset

### CSV Import

- Import approved price observations directly
- Download approved price import template
- Import raw prices into the pending review queue
- Download raw price import template

### Raw Price Review Queue

- Create raw price rows
- Edit pending raw rows
- Approve pending rows into real price observations
- Reject pending rows
- Delete raw rows
- Bulk approve pending rows
- Bulk reject pending rows
- View pending, approved, and rejected rows
- View raw review stats
- Detect duplicate price observations before approval

### Analytics

- Dashboard summary counts
- Price trends
- Shop comparison
- Basket inflation
- Public indicator trends

### Public Indicators

- Store exchange rate, fuel price, and inflation indicator records
- View recent indicators
- Track indicator trends

### Forecasting

- Moving-average item price prediction
- Moving-average basket total prediction
- Local scikit-learn price model training
- ML item price prediction
- Baseline vs ML comparison endpoint
- Price model status endpoint
- Price model reset endpoint
- Model training-run history

### Testing

Backend API tests are organized by domain:

- items
- prices
- basket
- exports
- imports
- analytics
- indicators
- predictions
- ML exports
- model training
- raw collections
- raw imports

## Current Limitations

- SQLite schema changes currently require deleting the local database during development.
- There are no Alembic migrations yet.
- Authentication is not implemented.
- The frontend is still a single-page dashboard.
- Raw review editing currently uses simple prompt-based editing.
- ML model training is local and experimental.
- Forecasting quality depends heavily on collected price history.
- Public indicators are manually entered.

## Recommended Next Steps

### Documentation

- Update API reference
- Document data flow
- Document raw review workflow
- Document prediction workflow
- Document development setup

### Backend

- Add Alembic migrations
- Add database seed script
- Add stronger duplicate matching rules
- Add pagination for larger datasets
- Add better validation schemas for raw imports

### Frontend

- Replace prompt-based editing with proper modals/forms
- Split App.tsx into feature components
- Add route-based navigation
- Add loading states per section
- Add better empty states

### Data/ML

- Add model evaluation export
- Add train/test split documentation
- Add baseline vs ML performance comparison
- Add richer time-based features
