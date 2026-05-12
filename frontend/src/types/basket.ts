export type BasketItem = {
  id: number;
  item_id: number;
  quantity: number;
  unit: string;
  created_at: string;
};

export type CreateBasketItemPayload = {
  item_id: number;
  quantity: number;
  unit: string;
};

export type UpdateBasketItemPayload = Partial<CreateBasketItemPayload>;

export type BasketTotalLine = {
  basket_item_id: number;
  item_id: number;
  item_name: string;
  quantity: number;
  unit: string;
  latest_price: number | null;
  price_per_unit: number | null;
  shop_name?: string;
  location?: string | null;
  observed_at?: string;
  line_total: number | null;
  status: "priced" | "missing_price";
};

export type BasketTotal = {
  currency: "ZMW";
  total: number;
  items: BasketTotalLine[];
};
