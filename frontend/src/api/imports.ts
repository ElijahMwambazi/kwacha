const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "") ??
  "http://localhost:8000";

export type ImportPriceCsvResult = {
  imported_count: number;
  created_item_count: number;
};

export type ImportTemplateKind = "prices";

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

export async function downloadImportTemplate(
  kind: ImportTemplateKind,
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/imports/${kind}-template.csv`);

  if (!response.ok) {
    throw new Error(`Failed to download ${kind} import template`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "kwacha_price_import_template.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();

  window.URL.revokeObjectURL(url);
}
