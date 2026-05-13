import { apiRequest } from "./client";
import type {
  BasketTotalPrediction,
  ItemPricePrediction,
} from "../types/prediction";

export function predictNextItemPrice(
  itemId: number,
  window = 3,
): Promise<ItemPricePrediction> {
  return apiRequest<ItemPricePrediction>(
    `/predictions/items/${itemId}/next-price?window=${window}`,
  );
}

export function predictNextBasketTotal(
  window = 3,
): Promise<BasketTotalPrediction> {
  return apiRequest<BasketTotalPrediction>(
    `/predictions/basket/next-total?window=${window}`,
  );
}
