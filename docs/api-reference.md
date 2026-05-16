# API Reference

This document summarizes the current local FastAPI surface for Kwacha!.

Base URL during local development:

```txt
http://127.0.0.1:8000
```

Interactive API docs:

```txt
http://127.0.0.1:8000/docs
```

## Notes

- The API is currently designed for local prototype development.
- Authentication is not implemented yet.
- SQLite is used as the local database.
- Most write endpoints expect JSON unless the endpoint explicitly accepts CSV upload.
- CSV upload endpoints use multipart form data with a `file` field.
- CSV download endpoints return `text/csv`.

## Health

| Method | Path      | Purpose               |
| ------ | --------- | --------------------- |
| GET    | `/health` | Check backend health. |

## Items

Items represent products being tracked, such as mealie meal, rice, sugar, bread, fuel, or cooking oil.

| Method | Path               | Purpose                                       |
| ------ | ------------------ | --------------------------------------------- |
| POST   | `/items`           | Create an item.                               |
| GET    | `/items`           | List items ordered by name.                   |
| GET    | `/items/{item_id}` | Get a single item.                            |
| PATCH  | `/items/{item_id}` | Update an item.                               |
| DELETE | `/items/{item_id}` | Delete an item and related basket/price rows. |

### Create item example

```json
{
  "name": "Mealie Meal",
  "category": "Food",
  "brand": "Breakfast",
  "default_unit": "kg"
}
```

## Price Observations

Price observations are approved price records for a known item.

| Method | Path                        | Purpose                               |
| ------ | --------------------------- | ------------------------------------- |
| POST   | `/prices`                   | Create a price observation.           |
| GET    | `/prices`                   | List price observations.              |
| GET    | `/prices?item_id={item_id}` | List price observations for one item. |
| GET    | `/prices/{price_id}`        | Get a single price observation.       |
| PATCH  | `/prices/{price_id}`        | Update a price observation.           |
| DELETE | `/prices/{price_id}`        | Delete a price observation.           |

### Create price observation example

```json
{
  "item_id": 1,
  "shop_name": "Shoprite",
  "location": "Lusaka",
  "price": 250,
  "quantity": 25,
  "unit": "kg",
  "observed_at": "2026-05-13T08:00:00"
}
```

The backend calculates:

```txt
price_per_unit = price / quantity
```

## Basket

Basket rows define the user's personal basket of goods.

| Method | Path                       | Purpose                                                                    |
| ------ | -------------------------- | -------------------------------------------------------------------------- |
| POST   | `/basket`                  | Add an item to the basket. If it already exists, update its quantity/unit. |
| GET    | `/basket`                  | List basket rows.                                                          |
| PATCH  | `/basket/{basket_item_id}` | Update basket item quantity/unit.                                          |
| DELETE | `/basket/{basket_item_id}` | Remove a basket item.                                                      |
| GET    | `/basket/total`            | Calculate current basket total using latest price observations.            |

### Add basket item example

```json
{
  "item_id": 1,
  "quantity": 3,
  "unit": "kg"
}
```

### Basket total response shape

```json
{
  "currency": "ZMW",
  "total": 72,
  "items": [
    {
      "basket_item_id": 1,
      "item_id": 1,
      "item_name": "Rice",
      "quantity": 3,
      "unit": "kg",
      "latest_price": 120,
      "price_per_unit": 24,
      "shop_name": "Shop B",
      "location": "Lusaka",
      "observed_at": "2026-01-02T08:00:00",
      "line_total": 72,
      "status": "priced"
    }
  ]
}
```

If a basket item has no price history, its status is:

```txt
missing_price
```

## Raw Collections

Raw collections are unapproved price rows. They are useful for manual entry, CSV imports, scraped data, or any source that should be reviewed before becoming approved price history.

| Method | Path                                           | Purpose                                       |
| ------ | ---------------------------------------------- | --------------------------------------------- |
| POST   | `/raw-collections`                             | Create a raw price row.                       |
| GET    | `/raw-collections`                             | List all raw price rows.                      |
| GET    | `/raw-collections?status=pending`              | List pending raw rows.                        |
| GET    | `/raw-collections?status=approved`             | List approved raw rows.                       |
| GET    | `/raw-collections?status=rejected`             | List rejected raw rows.                       |
| GET    | `/raw-collections/stats`                       | Get raw review queue counts.                  |
| POST   | `/raw-collections/bulk/approve`                | Approve all pending rows.                     |
| POST   | `/raw-collections/bulk/reject`                 | Reject all pending rows.                      |
| PATCH  | `/raw-collections/{raw_collection_id}`         | Edit a pending raw row.                       |
| POST   | `/raw-collections/{raw_collection_id}/approve` | Approve one raw row into a price observation. |
| POST   | `/raw-collections/{raw_collection_id}/reject`  | Reject one pending raw row.                   |
| DELETE | `/raw-collections/{raw_collection_id}`         | Delete a raw row.                             |

### Create raw collection example

```json
{
  "item_name": "Rice",
  "category": "Food",
  "brand": "Local",
  "shop_name": "Shop A",
  "location": "Lusaka",
  "price": 100,
  "quantity": 5,
  "unit": "kg",
  "source": "manual",
  "notes": "Needs review",
  "collected_at": "2026-01-15T08:00:00"
}
```

### Raw collection statuses

```txt
pending
approved
rejected
```

### Duplicate detection

When approving a raw row, the backend checks whether the same item, shop, location, price, quantity, unit, and collected timestamp already exist as an approved price observation.

If a duplicate is detected, approval returns a conflict and marks the raw row as rejected with a note referencing the duplicate price observation.

## Analytics

Analytics endpoints power the dashboard.

| Method | Path                                                | Purpose                                                         |
| ------ | --------------------------------------------------- | --------------------------------------------------------------- |
| GET    | `/analytics/summary`                                | Count items, price observations, basket rows, and latest price. |
| GET    | `/analytics/price-trends`                           | List price trend points.                                        |
| GET    | `/analytics/price-trends?item_id={item_id}`         | List price trend points for one item.                           |
| GET    | `/analytics/shop-comparison`                        | Compare average/min/max price per unit by shop.                 |
| GET    | `/analytics/shop-comparison?item_id={item_id}`      | Compare shops for one item.                                     |
| GET    | `/analytics/basket-inflation`                       | Calculate month-by-month basket cost changes.                   |
| GET    | `/analytics/indicator-trends`                       | List public indicator trend points.                             |
| GET    | `/analytics/indicator-trends?name={indicator_name}` | List trend points for one indicator.                            |

## Public Indicators

Public indicators are external signals that can be tracked manually and later used as ML features.

Examples:

```txt
exchange_rate_usd_zmw
fuel_price_petrol
fuel_price_diesel
official_inflation
```

| Method | Path                         | Purpose                          |
| ------ | ---------------------------- | -------------------------------- |
| POST   | `/indicators`                | Create an indicator reading.     |
| GET    | `/indicators`                | List indicator readings.         |
| GET    | `/indicators?name={name}`    | List readings for one indicator. |
| GET    | `/indicators/{indicator_id}` | Get one indicator reading.       |
| PATCH  | `/indicators/{indicator_id}` | Update an indicator reading.     |
| DELETE | `/indicators/{indicator_id}` | Delete an indicator reading.     |

### Create indicator example

```json
{
  "name": "exchange_rate_usd_zmw",
  "value": 25.5,
  "unit": "ZMW",
  "source": "BOZ",
  "observed_at": "2026-05-13T08:00:00"
}
```

## CSV Exports

| Method | Path                    | Output file                     |
| ------ | ----------------------- | ------------------------------- |
| GET    | `/export/items.csv`     | `kwacha_items.csv`              |
| GET    | `/export/prices.csv`    | `kwacha_price_observations.csv` |
| GET    | `/export/basket.csv`    | `kwacha_basket.csv`             |
| GET    | `/export/ml-prices.csv` | `kwacha_ml_prices.csv`          |

### ML price export

The ML export joins price observations with item metadata and latest available public indicators.

Fields include:

- item metadata
- shop/location data
- price data
- observed year/month/day
- exchange rate
- petrol price
- diesel price
- official inflation

## CSV Imports

| Method | Path                               | Purpose                                          |
| ------ | ---------------------------------- | ------------------------------------------------ |
| GET    | `/imports`                         | List supported imports.                          |
| GET    | `/imports/prices-template.csv`     | Download direct price import template.           |
| POST   | `/imports/prices.csv`              | Import approved price observations directly.     |
| GET    | `/imports/raw-prices-template.csv` | Download raw price review queue template.        |
| POST   | `/imports/raw-prices.csv`          | Import raw price rows into pending review queue. |

### Required CSV columns

For both direct price imports and raw price imports:

```txt
item_name
shop_name
price
quantity
unit
```

### Common optional CSV columns

```txt
category
brand
location
observed_at
source
notes
```

`source` and `notes` are especially useful for raw price imports.

## Predictions

Prediction endpoints support baseline forecasting and local ML experimentation.

| Method | Path                                               | Purpose                                                 |
| ------ | -------------------------------------------------- | ------------------------------------------------------- |
| GET    | `/predictions/items/{item_id}/next-price`          | Predict next item price using moving average.           |
| GET    | `/predictions/items/{item_id}/next-price?window=3` | Predict with a chosen recent-observation window.        |
| GET    | `/predictions/basket/next-total`                   | Predict next basket total using moving average.         |
| GET    | `/predictions/basket/next-total?window=3`          | Predict basket with a chosen recent-observation window. |
| GET    | `/predictions/price-model/status`                  | Get local ML model status.                              |
| DELETE | `/predictions/price-model`                         | Delete/reset trained local ML model.                    |
| GET    | `/predictions/price-model/training-runs`           | List model training runs.                               |
| POST   | `/predictions/train-price-model`                   | Train local scikit-learn price model.                   |
| GET    | `/predictions/items/{item_id}/ml-next-price`       | Predict next item price using trained ML model.         |
| GET    | `/predictions/items/{item_id}/compare`             | Compare baseline and ML prediction for one item.        |

### Baseline item prediction

```txt
GET /predictions/items/1/next-price?window=3
```

Uses recent approved price observations and returns a moving average.

### ML item prediction

```txt
GET /predictions/items/1/ml-next-price
```

Requires a trained model.

### Compare prediction methods

```txt
GET /predictions/items/1/compare?window=3
```

Returns:

```json
{
  "item_id": 1,
  "item_name": "Rice",
  "unit": "kg",
  "baseline": {},
  "ml": {},
  "ml_error": null
}
```

If no trained model exists, `ml` is `null` and `ml_error` explains why.

## Common Error Cases

| Status | Meaning                                                                  |
| ------ | ------------------------------------------------------------------------ |
| 400    | Invalid request, invalid CSV row, invalid update, or insufficient data.  |
| 404    | Requested item, price, indicator, model, or raw row not found.           |
| 409    | Duplicate price observation detected during raw approval.                |
| 422    | Request validation failed, usually wrong type or missing required field. |

## Development Notes

- Use `/docs` for the source of truth while the API is changing quickly.
- Keep raw collection static routes such as `/raw-collections/stats` and `/raw-collections/bulk/approve` above dynamic routes such as `/raw-collections/{raw_collection_id}`.
- If route order is wrong, FastAPI may treat `bulk` or `stats` as `{raw_collection_id}` and return 422.
- During early SQLite development, schema changes may require deleting the local database.
- Later, Alembic migrations should replace manual database deletion.
