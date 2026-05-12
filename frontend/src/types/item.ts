export type Item = {
  id: number;
  name: string;
  category: string | null;
  brand: string | null;
  default_unit: string;
  created_at: string;
};

export type CreateItemPayload = {
  name: string;
  category?: string | null;
  brand?: string | null;
  default_unit: string;
};

export type UpdateItemPayload = Partial<CreateItemPayload>;
