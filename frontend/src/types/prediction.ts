export type ItemPricePrediction = {
  item_id: number;
  item_name: string;
  method: "moving_average";
  window: number;
  observations_used: number;
  predicted_price_per_unit: number;
  latest_price_per_unit: number;
  latest_change_percent: number | null;
  unit: string;
  confidence: "low" | "medium" | "high";
  latest_observed_at: string;
};

export type BasketPredictionLine = {
  basket_item_id: number;
  item_id: number;
  item_name: string;
  quantity: number;
  unit: string;
  predicted_price_per_unit: number | null;
  predicted_line_total: number | null;
  observations_used: number;
  status: "predicted" | "missing_price_history";
};

export type BasketTotalPrediction = {
  method: "moving_average";
  window: number;
  predicted_total: number;
  currency: "ZMW";
  items: BasketPredictionLine[];
};
