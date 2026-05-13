export type PublicIndicator = {
  id: number;
  name: string;
  value: number;
  unit: string | null;
  source: string | null;
  observed_at: string;
  created_at: string;
};

export type CreatePublicIndicatorPayload = {
  name: string;
  value: number;
  unit?: string | null;
  source?: string | null;
  observed_at?: string;
};

export type UpdatePublicIndicatorPayload =
  Partial<CreatePublicIndicatorPayload>;
