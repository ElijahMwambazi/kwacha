import type { PriceObservation } from "./price";

export type AnalyticsSummary = {
  item_count: number;
  price_observation_count: number;
  basket_item_count: number;
  latest_price_observation: PriceObservation | null;
};

export type PriceTrendPoint = {
  price_id: number;
  item_id: number;
  item_name: string;
  shop_name: string;
  location: string | null;
  price: number;
  quantity: number;
  unit: string;
  price_per_unit: number;
  observed_at: string;
};

export type ShopComparison = {
  item_id: number;
  item_name: string;
  shop_name: string;
  location: string | null;
  observation_count: number;
  min_price_per_unit: number;
  max_price_per_unit: number;
  avg_price_per_unit: number;
};

export type BasketInflationPoint = {
  month: string;
  basket_total: number;
  monthly_change_percent: number | null;
  priced_items_count: number;
  missing_items_count: number;
};

export type IndicatorTrendPoint = {
  indicator_id: number;
  name: string;
  value: number;
  unit: string | null;
  source: string | null;
  observed_at: string;
};
