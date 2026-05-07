# Data Dictionary

## items

Represents a tracked product or service.

| Field | Meaning |
|---|---|
| id | Unique item ID |
| name | Item name, e.g. Mealie meal |
| category | Food, transport, utilities, hygiene, etc. |
| default_unit | Preferred normalized unit, e.g. kg, litre, unit |
| created_at | Date item was created |

## price_observations

Represents a single observed price.

| Field | Meaning |
|---|---|
| id | Unique observation ID |
| item_id | Related item |
| brand | Product brand |
| shop | Shop or source |
| location | Physical or online location |
| price | Observed price in ZMW |
| quantity | Product quantity |
| unit | Original unit |
| price_per_unit | Normalized price per unit |
| observed_at | Date price was observed |
| source | manual, csv, scrape, ocr, official |
| confidence | Confidence score |
| notes | Optional notes |

## basket_items

Represents the user's personal basket.

| Field | Meaning |
|---|---|
| item_id | Basket item |
| basket_quantity | Quantity used in basket |
| basket_unit | Unit used in basket |
| weight | Optional weighting factor |
