# Architecture

Kwacha! has four main layers:

## 1. Frontend

A React dashboard for entering prices, reviewing imports, viewing basket inflation, and exploring trends.

## 2. Backend

A FastAPI service that exposes item, price, basket, analytics, import, and prediction endpoints.

## 3. Database

SQLite stores price observations, basket definitions, public indicators, and imported raw data.

## 4. Data Science Layer

Google Colab notebooks are used to clean exported data, analyze trends, train models, and evaluate predictions.

## Data Flow

Manual entry / CSV / collector
→ raw collection
→ pending review
→ approved price observation
→ analytics dashboard
→ exported dataset
→ model training
→ prediction endpoint
→ forecast dashboard
