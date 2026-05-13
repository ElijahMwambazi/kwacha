import { apiRequest } from "./client";
import type {
  AnalyticsSummary,
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
