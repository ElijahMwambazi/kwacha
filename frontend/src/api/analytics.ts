import { apiRequest } from "./client";
import type { AnalyticsSummary } from "../types/analytics";

export function getAnalyticsSummary(): Promise<AnalyticsSummary> {
  return apiRequest<AnalyticsSummary>("/analytics/summary");
}
