export type PriceObservation = {
  id: number;
  item_id: number;
  shop_name: string;
  location: string | null;
  price: number;
  quantity: number;
  unit: string;
  price_per_unit: number;
  observed_at: string;
  created_at: string;
};

export type CreatePriceObservationPayload = {
  item_id: number;
  shop_name: string;
  location?: string | null;
  price: number;
  quantity: number;
  unit: string;
  observed_at?: string;
};

export type UpdatePriceObservationPayload =
  Partial<CreatePriceObservationPayload>;
