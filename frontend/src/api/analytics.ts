import { apiRequest } from "./client";
import type {
  AnalyticsSummary,
  BasketInflationPoint,
  IndicatorTrendPoint,
  PriceTrendPoint,
  ShopComparison,
} from "../types/analytics";

export function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  return apiRequest<AnalyticsSummary>("/analytics/summary");
}

export function getPriceTrends(itemId?: number): Promise<PriceTrendPoint[]> {
  const query = itemId ? `?item_id=${itemId}` : "";
  return apiRequest<PriceTrendPoint[]>(`/analytics/price-trends${query}`);
}

export function getShopComparison(itemId?: number): Promise<ShopComparison[]> {
  const query = itemId ? `?item_id=${itemId}` : "";
  return apiRequest<ShopComparison[]>(`/analytics/shop-comparison${query}`);
}

export function getBasketInflation(): Promise<BasketInflationPoint[]> {
  return apiRequest<BasketInflationPoint[]>("/analytics/basket-inflation");
}

export function getIndicatorTrends(
  name?: string,
): Promise<IndicatorTrendPoint[]> {
  const query = name ? `?name=${encodeURIComponent(name)}` : "";
  return apiRequest<IndicatorTrendPoint[]>(
    `/analytics/indicator-trends${query}`,
  );
}
