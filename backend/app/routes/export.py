import csv
from io import StringIO

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select

from app.database import get_session
from app.models.basket import BasketItem
from app.models.item import Item
from app.models.price_observation import PriceObservation
from app.models.public_indicator import PublicIndicator

router = APIRouter(prefix="/export", tags=["export"])


def csv_response(content: str, filename: str) -> StreamingResponse:
    return StreamingResponse(
        iter([content]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )

def get_latest_indicator_value(
    *,
    session: Session,
    name: str,
    observed_at,
) -> float | None:
    indicator = session.exec(
        select(PublicIndicator)
        .where(PublicIndicator.name == name)
        .where(PublicIndicator.observed_at <= observed_at)
        .order_by(
            PublicIndicator.observed_at.desc(),
            PublicIndicator.id.desc(),
        )
    ).first()

    if not indicator:
        return None

    return indicator.value

@router.get("/items.csv")
def export_items(
    session: Session = Depends(get_session),
):
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "id",
            "name",
            "category",
            "brand",
            "default_unit",
            "created_at",
        ]
    )

    items = session.exec(select(Item).order_by(Item.name)).all()

    for item in items:
        writer.writerow(
            [
                item.id,
                item.name,
                item.category,
                item.brand,
                item.default_unit,
                item.created_at,
            ]
        )

    return csv_response(output.getvalue(), "kwacha_items.csv")


@router.get("/prices.csv")
def export_prices(
    session: Session = Depends(get_session),
):
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "id",
            "item_id",
            "item_name",
            "category",
            "brand",
            "shop_name",
            "location",
            "price",
            "quantity",
            "unit",
            "price_per_unit",
            "observed_at",
            "created_at",
        ]
    )

    observations = session.exec(
        select(PriceObservation, Item)
        .join(Item, PriceObservation.item_id == Item.id)
        .order_by(PriceObservation.observed_at.desc())
    ).all()

    for observation, item in observations:
        writer.writerow(
            [
                observation.id,
                observation.item_id,
                item.name,
                item.category,
                item.brand,
                observation.shop_name,
                observation.location,
                observation.price,
                observation.quantity,
                observation.unit,
                observation.price_per_unit,
                observation.observed_at,
                observation.created_at,
            ]
        )

    return csv_response(output.getvalue(), "kwacha_price_observations.csv")


@router.get("/basket.csv")
def export_basket(
    session: Session = Depends(get_session),
):
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "basket_item_id",
            "item_id",
            "item_name",
            "category",
            "brand",
            "basket_quantity",
            "basket_unit",
            "latest_price",
            "latest_quantity",
            "latest_unit",
            "latest_price_per_unit",
            "latest_shop_name",
            "latest_location",
            "latest_observed_at",
            "line_total",
            "status",
        ]
    )

    basket_items = session.exec(select(BasketItem).order_by(BasketItem.id)).all()

    for basket_item in basket_items:
        item = session.get(Item, basket_item.item_id)

        if not item:
            continue

        latest_price = session.exec(
            select(PriceObservation)
            .where(PriceObservation.item_id == basket_item.item_id)
            .order_by(
                PriceObservation.observed_at.desc(),
                PriceObservation.id.desc(),
            )
        ).first()

        if not latest_price:
            writer.writerow(
                [
                    basket_item.id,
                    item.id,
                    item.name,
                    item.category,
                    item.brand,
                    basket_item.quantity,
                    basket_item.unit,
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "missing_price",
                ]
            )
            continue

        line_total = round(latest_price.price_per_unit * basket_item.quantity, 2)

        writer.writerow(
            [
                basket_item.id,
                item.id,
                item.name,
                item.category,
                item.brand,
                basket_item.quantity,
                basket_item.unit,
                latest_price.price,
                latest_price.quantity,
                latest_price.unit,
                latest_price.price_per_unit,
                latest_price.shop_name,
                latest_price.location,
                latest_price.observed_at,
                line_total,
                "priced",
            ]
        )

    return csv_response(output.getvalue(), "kwacha_basket.csv")

@router.get("/ml-prices.csv")
def export_ml_price_dataset(
    session: Session = Depends(get_session),
):
    output = StringIO()
    writer = csv.writer(output)

    writer.writerow(
        [
            "price_observation_id",
            "item_id",
            "item_name",
            "category",
            "brand",
            "shop_name",
            "location",
            "price",
            "quantity",
            "unit",
            "price_per_unit",
            "observed_at",
            "observed_year",
            "observed_month",
            "observed_day",
            "exchange_rate_usd_zmw",
            "fuel_price_petrol",
            "fuel_price_diesel",
            "official_inflation",
        ]
    )

    rows = session.exec(
        select(PriceObservation, Item)
        .join(Item, PriceObservation.item_id == Item.id)
        .order_by(
            PriceObservation.observed_at.asc(),
            PriceObservation.id.asc(),
        )
    ).all()

    for observation, item in rows:
        exchange_rate = get_latest_indicator_value(
            session=session,
            name="exchange_rate_usd_zmw",
            observed_at=observation.observed_at,
        )

        petrol_price = get_latest_indicator_value(
            session=session,
            name="fuel_price_petrol",
            observed_at=observation.observed_at,
        )

        diesel_price = get_latest_indicator_value(
            session=session,
            name="fuel_price_diesel",
            observed_at=observation.observed_at,
        )

        official_inflation = get_latest_indicator_value(
            session=session,
            name="official_inflation",
            observed_at=observation.observed_at,
        )

        writer.writerow(
            [
                observation.id,
                observation.item_id,
                item.name,
                item.category,
                item.brand,
                observation.shop_name,
                observation.location,
                observation.price,
                observation.quantity,
                observation.unit,
                observation.price_per_unit,
                observation.observed_at,
                observation.observed_at.year,
                observation.observed_at.month,
                observation.observed_at.day,
                exchange_rate,
                petrol_price,
                diesel_price,
                official_inflation,
            ]
        )

    return csv_response(output.getvalue(), "kwacha_ml_prices.csv")