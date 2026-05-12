import { apiRequest } from "./client";
import type {
  CreatePriceObservationPayload,
  PriceObservation,
  UpdatePriceObservationPayload,
} from "../types/price";

export function listPriceObservations(
  itemId?: number,
): Promise<PriceObservation[]> {
  const query = itemId ? `?item_id=${itemId}` : "";
  return apiRequest<PriceObservation[]>(`/prices${query}`);
}

export function createPriceObservation(
  payload: CreatePriceObservationPayload,
): Promise<PriceObservation> {
  return apiRequest<PriceObservation>("/prices", {
    method: "POST",
    body: payload,
  });
}

export function updatePriceObservation(
  id: number,
  payload: UpdatePriceObservationPayload,
): Promise<PriceObservation> {
  return apiRequest<PriceObservation>(`/prices/${id}`, {
    method: "PATCH",
    body: payload,
  });
}

export function deletePriceObservation(id: number): Promise<void> {
  return apiRequest<void>(`/prices/${id}`, {
    method: "DELETE",
  });
}
