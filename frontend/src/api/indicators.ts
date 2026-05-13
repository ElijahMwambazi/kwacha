import { apiRequest } from "./client";
import type {
  CreatePublicIndicatorPayload,
  PublicIndicator,
  UpdatePublicIndicatorPayload,
} from "../types/indicators";

export function listIndicators(name?: string): Promise<PublicIndicator[]> {
  const query = name ? `?name=${encodeURIComponent(name)}` : "";
  return apiRequest<PublicIndicator[]>(`/indicators${query}`);
}

export function createIndicator(
  payload: CreatePublicIndicatorPayload,
): Promise<PublicIndicator> {
  return apiRequest<PublicIndicator>("/indicators", {
    method: "POST",
    body: payload,
  });
}

export function updateIndicator(
  id: number,
  payload: UpdatePublicIndicatorPayload,
): Promise<PublicIndicator> {
  return apiRequest<PublicIndicator>(`/indicators/${id}`, {
    method: "PATCH",
    body: payload,
  });
}

export function deleteIndicator(id: number): Promise<void> {
  return apiRequest<void>(`/indicators/${id}`, {
    method: "DELETE",
  });
}
