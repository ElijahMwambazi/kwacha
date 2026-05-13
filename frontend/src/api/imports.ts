const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

export type ImportPriceCsvResult = {
  imported_count: number;
  created_item_count: number;
};

export async function importPriceObservationsCsv(
  file: File,
): Promise<ImportPriceCsvResult> {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${API_BASE_URL}/imports/prices.csv`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let message = `CSV import failed: ${response.status}`;

    try {
      const error = await response.json();

      if (typeof error.detail === "string") {
        message = error.detail;
      } else if (error.detail?.message) {
        message = error.detail.message;
      }
    } catch {
      // Keep fallback message.
    }

    throw new Error(message);
  }

  return response.json() as Promise<ImportPriceCsvResult>;
}
