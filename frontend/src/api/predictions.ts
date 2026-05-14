import { apiRequest } from "./client";
import type {
  BasketTotalPrediction,
  ItemPredictionComparison,
  ItemPricePrediction,
  MLItemPricePrediction,
  PriceModelStatus,
  PriceModelTrainingResult,
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

export function trainPriceModel(): Promise<PriceModelTrainingResult> {
  return apiRequest<PriceModelTrainingResult>(
    "/predictions/train-price-model",
    {
      method: "POST",
    },
  );
}

export function predictNextItemPriceWithMl(
  itemId: number,
): Promise<MLItemPricePrediction> {
  return apiRequest<MLItemPricePrediction>(
    `/predictions/items/${itemId}/ml-next-price`,
  );
}

export function compareItemPricePredictions(
  itemId: number,
  window = 3,
): Promise<ItemPredictionComparison> {
  return apiRequest<ItemPredictionComparison>(
    `/predictions/items/${itemId}/compare?window=${window}`,
  );
}

export function getPriceModelStatus(): Promise<PriceModelStatus> {
  return apiRequest<PriceModelStatus>("/predictions/price-model/status");
}

export function resetPriceModel(): Promise<PriceModelStatus> {
  return apiRequest<PriceModelStatus>("/predictions/price-model", {
    method: "DELETE",
  });
}
