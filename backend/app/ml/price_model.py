from datetime import datetime
from pathlib import Path
from typing import Any

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sqlmodel import Session, select

from app.database import DATA_DIR
from app.models.item import Item
from app.models.price_observation import PriceObservation
from app.models.public_indicator import PublicIndicator

MODEL_DIR = DATA_DIR / "models"
MODEL_DIR.mkdir(parents=True, exist_ok=True)

MODEL_PATH = MODEL_DIR / "price_model.joblib"

CATEGORICAL_FEATURES = [
    "item_name",
    "category",
    "brand",
    "shop_name",
    "location",
    "unit",
]

NUMERIC_FEATURES = [
    "observed_month",
    "observed_day",
    "previous_price_per_unit",
    "exchange_rate_usd_zmw",
    "fuel_price_petrol",
    "fuel_price_diesel",
    "official_inflation",
]

FEATURE_COLUMNS = CATEGORICAL_FEATURES + NUMERIC_FEATURES
TARGET_COLUMN = "price_per_unit"


def get_latest_indicator_value(
    *,
    session: Session,
    name: str,
    observed_at: datetime,
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


def build_price_training_frame(session: Session) -> pd.DataFrame:
    rows = session.exec(
        select(PriceObservation, Item)
        .join(Item, PriceObservation.item_id == Item.id)
        .order_by(
            PriceObservation.item_id.asc(),
            PriceObservation.observed_at.asc(),
            PriceObservation.id.asc(),
        )
    ).all()

    records: list[dict[str, Any]] = []

    for observation, item in rows:
        records.append(
            {
                "price_observation_id": observation.id,
                "item_id": item.id,
                "item_name": item.name,
                "category": item.category,
                "brand": item.brand,
                "shop_name": observation.shop_name,
                "location": observation.location,
                "unit": observation.unit,
                "observed_at": observation.observed_at,
                "observed_month": observation.observed_at.month,
                "observed_day": observation.observed_at.day,
                "price_per_unit": observation.price_per_unit,
                "exchange_rate_usd_zmw": get_latest_indicator_value(
                    session=session,
                    name="exchange_rate_usd_zmw",
                    observed_at=observation.observed_at,
                ),
                "fuel_price_petrol": get_latest_indicator_value(
                    session=session,
                    name="fuel_price_petrol",
                    observed_at=observation.observed_at,
                ),
                "fuel_price_diesel": get_latest_indicator_value(
                    session=session,
                    name="fuel_price_diesel",
                    observed_at=observation.observed_at,
                ),
                "official_inflation": get_latest_indicator_value(
                    session=session,
                    name="official_inflation",
                    observed_at=observation.observed_at,
                ),
            }
        )

    frame = pd.DataFrame.from_records(records)

    if frame.empty:
        return frame

    frame["previous_price_per_unit"] = frame.groupby("item_id")[
        "price_per_unit"
    ].shift(1)

    return frame.dropna(subset=["previous_price_per_unit"]).reset_index(drop=True)


def create_model_pipeline() -> Pipeline:
    categorical_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="unknown")),
            ("encoder", OneHotEncoder(handle_unknown="ignore")),
        ]
    )

    numeric_pipeline = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
        ]
    )

    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", categorical_pipeline, CATEGORICAL_FEATURES),
            ("numeric", numeric_pipeline, NUMERIC_FEATURES),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        min_samples_leaf=1,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )


def train_price_model(session: Session) -> dict[str, Any]:
    frame = build_price_training_frame(session)

    if frame.empty or len(frame) < 2:
        raise ValueError(
            "Not enough price history to train model. Add at least two observations for one item."
        )

    x = frame[FEATURE_COLUMNS]
    y = frame[TARGET_COLUMN]

    pipeline = create_model_pipeline()

    if len(frame) >= 5:
        x_train, x_test, y_train, y_test = train_test_split(
            x,
            y,
            test_size=0.25,
            random_state=42,
        )

        pipeline.fit(x_train, y_train)
        predictions = pipeline.predict(x_test)

        metrics: dict[str, float | None] = {
            "mae": round(float(mean_absolute_error(y_test, predictions)), 4),
            "r2": round(float(r2_score(y_test, predictions)), 4),
        }
    else:
        pipeline.fit(x, y)
        metrics = {
            "mae": None,
            "r2": None,
        }

    bundle = {
        "model": pipeline,
        "feature_columns": FEATURE_COLUMNS,
        "target_column": TARGET_COLUMN,
        "trained_at": datetime.utcnow().isoformat(),
        "training_rows": len(frame),
        "metrics": metrics,
    }

    joblib.dump(bundle, MODEL_PATH)

    return {
        "model_path": str(MODEL_PATH),
        "trained_at": bundle["trained_at"],
        "training_rows": len(frame),
        "metrics": metrics,
    }


def load_price_model_bundle() -> dict[str, Any]:
    if not Path(MODEL_PATH).exists():
        raise FileNotFoundError("Price model has not been trained yet")

    return joblib.load(MODEL_PATH)


def predict_next_price_with_model(
    *,
    session: Session,
    item_id: int,
) -> dict[str, Any]:
    bundle = load_price_model_bundle()

    item = session.get(Item, item_id)

    if not item:
        raise ValueError("Item not found")

    latest_observation = session.exec(
        select(PriceObservation)
        .where(PriceObservation.item_id == item_id)
        .order_by(
            PriceObservation.observed_at.desc(),
            PriceObservation.id.desc(),
        )
    ).first()

    if not latest_observation:
        raise ValueError("No price observations found for item")

    now = datetime.utcnow()

    prediction_frame = pd.DataFrame(
        [
            {
                "item_name": item.name,
                "category": item.category,
                "brand": item.brand,
                "shop_name": latest_observation.shop_name,
                "location": latest_observation.location,
                "unit": latest_observation.unit,
                "observed_month": now.month,
                "observed_day": now.day,
                "previous_price_per_unit": latest_observation.price_per_unit,
                "exchange_rate_usd_zmw": get_latest_indicator_value(
                    session=session,
                    name="exchange_rate_usd_zmw",
                    observed_at=now,
                ),
                "fuel_price_petrol": get_latest_indicator_value(
                    session=session,
                    name="fuel_price_petrol",
                    observed_at=now,
                ),
                "fuel_price_diesel": get_latest_indicator_value(
                    session=session,
                    name="fuel_price_diesel",
                    observed_at=now,
                ),
                "official_inflation": get_latest_indicator_value(
                    session=session,
                    name="official_inflation",
                    observed_at=now,
                ),
            }
        ]
    )

    model = bundle["model"]
    predicted_price_per_unit = round(float(model.predict(prediction_frame)[0]), 4)

    return {
        "item_id": item.id,
        "item_name": item.name,
        "method": "random_forest_regressor",
        "predicted_price_per_unit": predicted_price_per_unit,
        "latest_price_per_unit": latest_observation.price_per_unit,
        "unit": latest_observation.unit,
        "latest_observed_at": latest_observation.observed_at,
        "model": {
            "trained_at": bundle["trained_at"],
            "training_rows": bundle["training_rows"],
            "metrics": bundle["metrics"],
        },
    }