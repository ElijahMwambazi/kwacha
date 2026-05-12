from fastapi import FastAPI

from app.database import create_db_and_tables
from app.routes import analytics, basket, health, imports, indicators, items, predictions, prices

app = FastAPI(title="Kwacha API", version="0.1.0")


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


app.include_router(health.router)
app.include_router(items.router)
app.include_router(prices.router)
app.include_router(basket.router)
app.include_router(analytics.router)
app.include_router(imports.router)
app.include_router(indicators.router)
app.include_router(predictions.router)