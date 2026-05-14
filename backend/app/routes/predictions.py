from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.database import get_session
from app.models.item import Item
from app.models.price_observation import PriceObservation
from app.ml.price_model import (
    delete_price_model,
    get_price_model_status,
    predict_next_price_with_model,
    train_price_model,
)

router = APIRouter(prefix="/predictions", tags=["predictions"])


def average(values: list[float]) -> float:
    return round(sum(values) / len(values), 4)


@router.get("/items/{item_id}/next-price")
def predict_next_item_price(
    item_id: int,
    window: int = Query(default=3, ge=1, le=30),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    item = session.get(Item, item_id)

    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found",
        )

    observations = session.exec(
        select(PriceObservation)
        .where(PriceObservation.item_id == item_id)
        .order_by(
            PriceObservation.observed_at.desc(),
            PriceObservation.id.desc(),
        )
    ).all()

    if not observations:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No price observations found for item",
        )

    selected_observations = observations[:window]
    prices = [observation.price_per_unit for observation in selected_observations]

    predicted_price_per_unit = average(prices)

    latest_observation = observations[0]
    previous_observation = observations[1] if len(observations) > 1 else None

    if previous_observation and previous_observation.price_per_unit:
        latest_change_percent = round(
            (
                (
                    latest_observation.price_per_unit
                    - previous_observation.price_per_unit
                )
                / previous_observation.price_per_unit
            )
            * 100,
            2,
        )
    else:
        latest_change_percent = None

    confidence = "low"

    if len(selected_observations) >= 10:
        confidence = "high"
    elif len(selected_observations) >= 5:
        confidence = "medium"

    return {
        "item_id": item.id,
        "item_name": item.name,
        "method": "moving_average",
        "window": window,
        "observations_used": len(selected_observations),
        "predicted_price_per_unit": predicted_price_per_unit,
        "latest_price_per_unit": latest_observation.price_per_unit,
        "latest_change_percent": latest_change_percent,
        "unit": latest_observation.unit,
        "confidence": confidence,
        "latest_observed_at": latest_observation.observed_at,
    }


@router.get("/basket/next-total")
def predict_next_basket_total(
    window: int = Query(default=3, ge=1, le=30),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    from app.models.basket import BasketItem

    basket_items = session.exec(select(BasketItem).order_by(BasketItem.id)).all()

    if not basket_items:
        return {
            "method": "moving_average",
            "window": window,
            "predicted_total": 0,
            "currency": "ZMW",
            "items": [],
        }

    lines: list[dict[str, Any]] = []
    predicted_total = 0.0

    for basket_item in basket_items:
        item = session.get(Item, basket_item.item_id)

        if not item:
            continue

        observations = session.exec(
            select(PriceObservation)
            .where(PriceObservation.item_id == basket_item.item_id)
            .order_by(
                PriceObservation.observed_at.desc(),
                PriceObservation.id.desc(),
            )
        ).all()

        if not observations:
            lines.append(
                {
                    "basket_item_id": basket_item.id,
                    "item_id": item.id,
                    "item_name": item.name,
                    "quantity": basket_item.quantity,
                    "unit": basket_item.unit,
                    "predicted_price_per_unit": None,
                    "predicted_line_total": None,
                    "observations_used": 0,
                    "status": "missing_price_history",
                }
            )
            continue

        selected_observations = observations[:window]
        prices = [
            observation.price_per_unit
            for observation in selected_observations
        ]
        predicted_price_per_unit = average(prices)
        predicted_line_total = round(
            predicted_price_per_unit * basket_item.quantity,
            2,
        )

        predicted_total += predicted_line_total

        lines.append(
            {
                "basket_item_id": basket_item.id,
                "item_id": item.id,
                "item_name": item.name,
                "quantity": basket_item.quantity,
                "unit": basket_item.unit,
                "predicted_price_per_unit": predicted_price_per_unit,
                "predicted_line_total": predicted_line_total,
                "observations_used": len(selected_observations),
                "status": "predicted",
            }
        )

    return {
        "method": "moving_average",
        "window": window,
        "predicted_total": round(predicted_total, 2),
        "currency": "ZMW",
        "items": lines,
    }

@router.get("/price-model/status")
def get_price_prediction_model_status() -> dict[str, Any]:
    return get_price_model_status()


@router.delete("/price-model", status_code=status.HTTP_200_OK)
def reset_price_prediction_model() -> dict[str, Any]:
    return delete_price_model()

@router.post("/train-price-model", status_code=status.HTTP_201_CREATED)
def train_price_prediction_model(
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    try:
        return train_price_model(session)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get("/items/{item_id}/ml-next-price")
def predict_next_item_price_with_ml(
    item_id: int,
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    try:
        return predict_next_price_with_model(
            session=session,
            item_id=item_id,
        )
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

@router.get("/items/{item_id}/compare")
def compare_item_price_predictions(
    item_id: int,
    window: int = Query(default=3, ge=1, le=30),
    session: Session = Depends(get_session),
) -> dict[str, Any]:
    baseline = predict_next_item_price(
        item_id=item_id,
        window=window,
        session=session,
    )

    ml_prediction = None
    ml_error = None

    try:
        ml_prediction = predict_next_price_with_model(
            session=session,
            item_id=item_id,
        )
    except FileNotFoundError as error:
        ml_error = str(error)
    except ValueError as error:
        ml_error = str(error)

    return {
        "item_id": baseline["item_id"],
        "item_name": baseline["item_name"],
        "unit": baseline["unit"],
        "baseline": baseline,
        "ml": ml_prediction,
        "ml_error": ml_error,
    }