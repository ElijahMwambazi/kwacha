from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import create_db_and_tables
from app.routes import (
    analytics,
    basket,
    export,
    health,
    imports,
    indicators,
    items,
    predictions,
    prices,
)

app = FastAPI(title="Kwacha API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()


app.include_router(health.router)
app.include_router(items.router)
app.include_router(prices.router)
app.include_router(basket.router)
app.include_router(analytics.router)
app.include_router(export.router)
app.include_router(imports.router)
app.include_router(indicators.router)
app.include_router(predictions.router)