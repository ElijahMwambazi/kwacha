import csv
from datetime import datetime
from io import StringIO
from typing import Any

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.database import get_session
from app.models.item import Item
from app.models.price_observation import PriceObservation

router = APIRouter(prefix="/imports", tags=["imports"])


REQUIRED_PRICE_COLUMNS = {
    "item_name",
    "shop_name",
    "price",
    "quantity",
    "unit",
}

def csv_response(content: str, filename: str) -> StreamingResponse:
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )

def parse_optional_text(value: str | None) -> str | None:
    if value is None:
        return None

    stripped = value.strip()

    return stripped or None


def parse_observed_at(value: str | None) -> datetime:
    if not value or not value.strip():
        return datetime.utcnow()

    normalized = value.strip().replace("Z", "+00:00")

    try:
        return datetime.fromisoformat(normalized)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid observed_at value: {value}",
        ) from error


def parse_positive_float(value: str | None, column_name: str) -> float:
    if value is None or not value.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required numeric value: {column_name}",
        )

    try:
        parsed = float(value)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid numeric value for {column_name}: {value}",
        ) from error

    if parsed <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{column_name} must be greater than 0",
        )

    return parsed


def get_or_create_item(
    *,
    session: Session,
    item_name: str,
    category: str | None,
    brand: str | None,
    default_unit: str,
) -> Item:
    existing_item = session.exec(select(Item).where(Item.name == item_name)).first()

    if existing_item:
        return existing_item

    item = Item(
        name=item_name,
        category=category,
        brand=brand,
        default_unit=default_unit,
    )

    session.add(item)
    session.flush()
    session.refresh(item)

    return item


@router.get("")
def list_imports():
    return {
        "supported_imports": [
            {
                "name": "price observations",
                "endpoint": "/imports/prices.csv",
                "method": "POST",
                "required_columns": sorted(REQUIRED_PRICE_COLUMNS),
                "optional_columns": [
                    "item_id",
                    "category",
                    "brand",
                    "location",
                    "observed_at",
                ],
            }
        ]
    }

@router.get("/prices-template.csv")
def download_price_import_template():
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "item_name",
            "category",
            "brand",
            "shop_name",
            "location",
            "price",
            "quantity",
            "unit",
            "observed_at",
        ]
    )

    writer.writerow(
        [
            "Mealie Meal",
            "Food",
            "Breakfast",
            "Shoprite",
            "Lusaka",
            "250",
            "25",
            "kg",
            "2026-05-13T08:00:00",
        ]
    )

    writer.writerow(
        [
            "Sugar",
            "Food",
            "",
            "Pick n Pay",
            "Lusaka",
            "55",
            "2",
            "kg",
            "2026-05-13T08:00:00",
        ]
    )

    return csv_response(output.getvalue(), "kwacha_price_import_template.csv")

@router.post("/prices.csv", status_code=status.HTTP_201_CREATED)
async def import_price_observations_csv(
    file: UploadFile = File(...),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    if not file.filename or not file.filename.endswith(".csv"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only .csv files are supported",
        )

    content = await file.read()

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV must be UTF-8 encoded",
        ) from error

    reader = csv.DictReader(StringIO(text))

    if not reader.fieldnames:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV has no header row",
        )

    fieldnames = {field.strip() for field in reader.fieldnames if field}
    missing_columns = REQUIRED_PRICE_COLUMNS - fieldnames

    if missing_columns:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing required columns: {', '.join(sorted(missing_columns))}",
        )

    rows = list(reader)
    parsed_rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    for row_number, row in enumerate(rows, start=2):
        try:
            item_name = (row.get("item_name") or "").strip()

            if not item_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="item_name is required",
                )

            shop_name = (row.get("shop_name") or "").strip()

            if not shop_name:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="shop_name is required",
                )

            price = parse_positive_float(row.get("price"), "price")
            quantity = parse_positive_float(row.get("quantity"), "quantity")
            unit = (row.get("unit") or "unit").strip() or "unit"

            item_id_value = parse_optional_text(row.get("item_id"))

            parsed_rows.append(
                {
                    "row_number": row_number,
                    "item_id_value": item_id_value,
                    "item_name": item_name,
                    "category": parse_optional_text(row.get("category")),
                    "brand": parse_optional_text(row.get("brand")),
                    "shop_name": shop_name,
                    "location": parse_optional_text(row.get("location")),
                    "price": price,
                    "quantity": quantity,
                    "unit": unit,
                    "observed_at": parse_observed_at(row.get("observed_at")),
                }
            )

        except HTTPException as error:
            errors.append(
                {
                    "row": row_number,
                    "detail": error.detail,
                }
            )
        except Exception as error:
            errors.append(
                {
                    "row": row_number,
                    "detail": str(error),
                }
            )

    if errors:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "CSV import failed. No rows were imported.",
                "errors": errors,
            },
        )

    imported_count = 0
    created_item_count = 0

    for parsed_row in parsed_rows:
        item_id_value = parsed_row["item_id_value"]

        if item_id_value:
            item = session.get(Item, int(item_id_value))

            if not item:
                session.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Item not found for item_id: {item_id_value}",
                )
        else:
            item_before_create = session.exec(
                select(Item).where(Item.name == parsed_row["item_name"])
            ).first()

            item = get_or_create_item(
                session=session,
                item_name=parsed_row["item_name"],
                category=parsed_row["category"],
                brand=parsed_row["brand"],
                default_unit=parsed_row["unit"],
            )

            if item_before_create is None:
                created_item_count += 1

        observation = PriceObservation(
            item_id=item.id,
            shop_name=parsed_row["shop_name"],
            location=parsed_row["location"],
            price=parsed_row["price"],
            quantity=parsed_row["quantity"],
            unit=parsed_row["unit"],
            price_per_unit=round(parsed_row["price"] / parsed_row["quantity"], 4),
            observed_at=parsed_row["observed_at"],
        )

        session.add(observation)
        imported_count += 1

    session.commit()

    return {
        "imported_count": imported_count,
        "created_item_count": created_item_count,
    }