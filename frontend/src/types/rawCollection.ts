import type { Item } from "./item";
import type { PriceObservation } from "./price";

export type RawCollectionStatus = "pending" | "approved" | "rejected";

export type RawCollection = {
  id: number;
  item_name: string;
  category: string | null;
  brand: string | null;
  shop_name: string;
  location: string | null;
  price: number;
  quantity: number;
  unit: string;
  source: string | null;
  notes: string | null;
  status: RawCollectionStatus;
  collected_at: string;
  reviewed_at: string | null;
  created_at: string;
};

export type CreateRawCollectionPayload = {
  item_name: string;
  category?: string | null;
  brand?: string | null;
  shop_name: string;
  location?: string | null;
  price: number;
  quantity: number;
  unit: string;
  source?: string | null;
  notes?: string | null;
  collected_at?: string;
};

export type UpdateRawCollectionPayload = Partial<CreateRawCollectionPayload>;

export type ApproveRawCollectionResult = {
  raw_collection: RawCollection;
  item: Item;
  price_observation: PriceObservation;
};

export type BulkApproveRawCollectionsResult = {
  approved_count: number;
  created_items_count: number;
  created_price_observations_count: number;
};

export type BulkRejectRawCollectionsResult = {
  rejected_count: number;
};
