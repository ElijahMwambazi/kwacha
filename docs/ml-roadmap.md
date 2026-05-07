# Machine Learning Roadmap

## Goal

Use historical price observations and public indicators to forecast item prices and basket cost.

## Stage 1: Baseline

- Calculate moving averages
- Compare current price to previous price
- Build simple trend charts

## Stage 2: Classical ML

Models:

- LinearRegression
- RandomForestRegressor
- GradientBoostingRegressor
- XGBoost or LightGBM later

Features:

- item
- category
- shop
- location
- month
- previous price
- rolling 7-day average
- rolling 30-day average
- exchange rate
- fuel price
- official inflation

Target:

- next price_per_unit

## Stage 3: Forecasting

- Forecast item-level prices
- Forecast basket-level cost
- Add prediction confidence
- Compare model performance against simple moving average baseline

## Stage 4: App Integration

- Save model with joblib
- Serve prediction through backend
- Display forecast cards in frontend
