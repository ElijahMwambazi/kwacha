const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

export type ExportKind = "items" | "prices" | "basket" | "ml-prices";

const filenames: Record<ExportKind, string> = {
  items: "kwacha_items.csv",
  prices: "kwacha_price_observations.csv",
  basket: "kwacha_basket.csv",
  "ml-prices": "kwacha_ml_prices.csv",
};

export async function downloadCsv(kind: ExportKind): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/export/${kind}.csv`);

  if (!response.ok) {
    throw new Error(`Failed to export ${kind} CSV`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = filenames[kind];
  document.body.appendChild(link);
  link.click();
  link.remove();

  window.URL.revokeObjectURL(url);
}
