import type { PriceObservation } from "./price";

export type AnalyticsSummary = {
  item_count: number;
  price_observation_count: number;
  basket_item_count: number;
  latest_price_observation: PriceObservation | null;
};
