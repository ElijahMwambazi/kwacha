import { apiRequest } from "./client";
import type { CreateItemPayload, Item, UpdateItemPayload } from "../types/item";

export function listItems(): Promise<Item[]> {
  return apiRequest<Item[]>("/items");
}

export function createItem(payload: CreateItemPayload): Promise<Item> {
  return apiRequest<Item>("/items", {
    method: "POST",
    body: payload,
  });
}

export function updateItem(
  id: number,
  payload: UpdateItemPayload,
): Promise<Item> {
  return apiRequest<Item>(`/items/${id}`, {
    method: "PATCH",
    body: payload,
  });
}

export function deleteItem(id: number): Promise<void> {
  return apiRequest<void>(`/items/${id}`, {
    method: "DELETE",
  });
}
