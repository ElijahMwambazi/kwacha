import { apiRequest } from "./client";
import type {
  BasketItem,
  BasketTotal,
  CreateBasketItemPayload,
  UpdateBasketItemPayload,
} from "../types/basket";

export function listBasketItems(): Promise<BasketItem[]> {
  return apiRequest<BasketItem[]>("/basket");
}

export function addBasketItem(
  payload: CreateBasketItemPayload,
): Promise<BasketItem> {
  return apiRequest<BasketItem>("/basket", {
    method: "POST",
    body: payload,
  });
}

export function updateBasketItem(
  id: number,
  payload: UpdateBasketItemPayload,
): Promise<BasketItem> {
  return apiRequest<BasketItem>(`/basket/${id}`, {
    method: "PATCH",
    body: payload,
  });
}

export function removeBasketItem(id: number): Promise<void> {
  return apiRequest<void>(`/basket/${id}`, {
    method: "DELETE",
  });
}

export function getBasketTotal(): Promise<BasketTotal> {
  return apiRequest<BasketTotal>("/basket/total");
}
