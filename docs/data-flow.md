# Data Flow

This document explains how data moves through Kwacha!.

Kwacha! has two main data paths:

1. Direct approved price entry.
2. Raw price review before approval.

The raw review path is preferred for imported, scraped, manually collected, or uncertain data.

## High-Level Flow

```txt
Raw price source
  -> raw collection row
  -> pending review queue
  -> edit / approve / reject
  -> approved price observation
  -> analytics
  -> exports
  -> prediction features
```

```txt
Direct user entry
  -> item
  -> approved price observation
  -> basket
  -> analytics
  -> exports
  -> prediction features
```

## Core Entities

### Item

An item is the product being tracked.

Examples:

- Mealie Meal
- Rice
- Sugar
- Bread
- Cooking Oil
- Fuel

Important fields:

```txt
id
name
category
brand
default_unit
created_at
```

Items are used by:

- price observations
- basket items
- exports
- analytics
- predictions

## Price Observation

A price observation is an approved price record.

Important fields:

```txt
id
item_id
shop_name
location
price
quantity
unit
price_per_unit
observed_at
created_at
```

The backend calculates:

```txt
price_per_unit = price / quantity
```

Price observations are used by:

- price trends
- shop comparison
- basket total
- basket inflation
- ML export
- baseline predictions
- ML model training

## Basket Item

A basket item represents the user's personal basket quantity for one item.

Important fields:

```txt
id
item_id
quantity
unit
created_at
```

The basket total uses the latest approved price observation for each basket item.

If an item has no approved price observation, it appears as:

```txt
missing_price
```

## Raw Collection

A raw collection is an unapproved price row.

Important fields:

```txt
id
item_name
category
brand
shop_name
location
price
quantity
unit
source
notes
status
collected_at
reviewed_at
created_at
```

Possible statuses:

```txt
pending
approved
rejected
```

Raw collections are useful for:

- CSV imports
- manually collected prices
- scraped prices
- mobile collection workflows
- future crowdsourcing workflows

## Direct Price Entry Flow

Use this when the data is already trusted.

```txt
Create item
  -> POST /items

Create price observation
  -> POST /prices

Add item to basket
  -> POST /basket

View basket total
  -> GET /basket/total
```

### Direct Flow Diagram

```txt
User
 |
 | creates
 v
Item
 |
 | receives
 v
Price Observation
 |
 | joins with
 v
Basket Item
 |
 | calculates
 v
Basket Total
```

## Raw Review Flow

Use this when the data should be checked before entering the approved price dataset.

```txt
Create raw row
  -> POST /raw-collections

or import raw rows
  -> POST /imports/raw-prices.csv

Review pending rows
  -> GET /raw-collections?status=pending

Edit mistakes
  -> PATCH /raw-collections/{id}

Approve valid rows
  -> POST /raw-collections/{id}/approve

Reject invalid rows
  -> POST /raw-collections/{id}/reject
```

### Raw Review Flow Diagram

```txt
CSV / manual entry / scraper
 |
 v
Raw Collection
 |
 v
Pending Review Queue
 |
 | approve
 v
Approved Price Observation
 |
 v
Analytics + Exports + Forecasting
```

```txt
Pending Review Queue
 |
 | reject
 v
Rejected Raw Collection
```

## Raw Approval Behavior

When a raw row is approved:

1. The backend checks whether an item with the raw `item_name` already exists.
2. If the item exists, the approved price uses that item.
3. If the item does not exist, a new item is created.
4. The backend checks for duplicate price observations.
5. If no duplicate exists, a price observation is created.
6. The raw row status becomes `approved`.
7. The raw row gets a `reviewed_at` timestamp.

## Duplicate Detection

Before approval, the backend checks for an existing approved price observation matching:

```txt
item
shop_name
location
price
quantity
unit
observed_at / collected_at
```

If a duplicate exists:

```txt
raw status -> rejected
notes -> duplicate_price_observation_id={id}
approval response -> 409 Conflict
```

This prevents repeated CSV imports or repeated manual entries from polluting the approved price history.

## Bulk Review Flow

Bulk approval:

```txt
POST /raw-collections/bulk/approve
```

Behavior:

- Approves all pending raw rows.
- Creates missing items.
- Creates approved price observations.
- Skips duplicates.
- Marks duplicate raw rows as rejected.
- Returns counts for approved rows, created items, created price observations, and duplicates.

Bulk rejection:

```txt
POST /raw-collections/bulk/reject
```

Behavior:

- Rejects all pending raw rows.
- Does not create items.
- Does not create price observations.

## Import Flow

Kwacha! supports two CSV import paths.

## Direct Approved Import

Endpoint:

```txt
POST /imports/prices.csv
```

Use this when rows are already trusted.

Flow:

```txt
CSV row
  -> item lookup/create
  -> approved price observation
```

Result:

```txt
approved price data immediately enters analytics and predictions
```

## Raw Review Import

Endpoint:

```txt
POST /imports/raw-prices.csv
```

Use this when rows need review.

Flow:

```txt
CSV row
  -> raw collection
  -> pending review queue
```

Result:

```txt
data does not affect analytics until approved
```

## Export Flow

Kwacha! supports normal exports and ML exports.

## Standard Exports

```txt
GET /export/items.csv
GET /export/prices.csv
GET /export/basket.csv
```

Use these for:

- manual inspection
- backups
- spreadsheet analysis
- simple reporting

## ML Export

```txt
GET /export/ml-prices.csv
```

The ML export joins approved price observations with:

- item metadata
- shop/location
- normalized price fields
- date features
- latest available public indicators

Output fields include:

```txt
price_observation_id
item_id
item_name
category
brand
shop_name
location
price
quantity
unit
price_per_unit
observed_at
observed_year
observed_month
observed_day
exchange_rate_usd_zmw
fuel_price_petrol
fuel_price_diesel
official_inflation
```

## Public Indicator Flow

Public indicators are external signals.

Examples:

```txt
exchange_rate_usd_zmw
fuel_price_petrol
fuel_price_diesel
official_inflation
```

Flow:

```txt
Manual indicator entry
  -> public indicator table
  -> indicator trends
  -> ML export
  -> ML model features
```

Indicators are matched to price observations by using the latest indicator value at or before the price observation date.

## Analytics Flow

Analytics are calculated from approved price observations and basket rows.

Raw rows do not affect analytics until approved.

```txt
Approved Price Observations
  -> price trends
  -> shop comparison
  -> basket inflation
```

```txt
Basket Items + Approved Price Observations
  -> current basket total
  -> monthly basket inflation
```

```txt
Public Indicators
  -> indicator trend charts
```

```txt
Raw Collections
  -> review queue stats
```

## Prediction Flow

Kwacha! currently supports two prediction paths.

## Baseline Prediction

Endpoint examples:

```txt
GET /predictions/items/{item_id}/next-price
GET /predictions/basket/next-total
```

Flow:

```txt
approved price history
  -> recent observations window
  -> moving average
  -> predicted next price
```

This works without model training.

## ML Prediction

Endpoint examples:

```txt
POST /predictions/train-price-model
GET /predictions/items/{item_id}/ml-next-price
```

Training flow:

```txt
approved price observations
  -> item metadata
  -> previous price feature
  -> public indicator features
  -> RandomForestRegressor
  -> joblib model
  -> model training run record
```

Prediction flow:

```txt
latest approved item price
  -> current date features
  -> latest public indicators
  -> trained model
  -> predicted next price
```

## Baseline vs ML Comparison

Endpoint:

```txt
GET /predictions/items/{item_id}/compare
```

Flow:

```txt
item_id
  -> moving average prediction
  -> ML prediction if model exists
  -> side-by-side comparison
```

If no ML model exists, the response still returns the baseline and includes an `ml_error`.

## Recommended Data Entry Policy

Use direct approved price entry only when:

- the user personally trusts the row
- the row has already been reviewed
- the row came from a controlled source

Use raw review when:

- importing CSV files
- entering collected field data
- scraping from websites
- testing future crowdsourced submissions
- uncertain about package size or unit
- duplicates are possible

## Current Limitations

- Raw duplicate detection is exact-match based.
- There is no fuzzy item matching yet.
- Public indicators are manually entered.
- Raw row editing is currently simple.
- SQLite schema changes require manual database reset during local development.
- No Alembic migrations yet.
- No authentication or user ownership yet.

## Future Improvements

- Add fuzzy duplicate detection.
- Add canonical item aliases.
- Add source reliability scores.
- Add raw row confidence score.
- Add audit log for review actions.
- Add reviewer name once authentication exists.
- Add import preview before saving rows.
- Add Alembic migrations.
- Add pagination for raw queue and price history.
- Add stronger ML feature engineering.
