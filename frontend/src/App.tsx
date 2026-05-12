// frontend/src/App.tsx

import { FormEvent, useEffect, useMemo, useState } from "react";

import { getAnalyticsSummary } from "./api/analytics";
import { addBasketItem, getBasketTotal, listBasketItems } from "./api/basket";
import { createItem, listItems } from "./api/items";
import { createPriceObservation, listPriceObservations } from "./api/prices";
import type { AnalyticsSummary } from "./types/analytics";
import type { BasketItem, BasketTotal } from "./types/basket";
import type { Item } from "./types/item";
import type { PriceObservation } from "./types/price";

type ItemFormState = {
  name: string;
  category: string;
  brand: string;
  default_unit: string;
};

type PriceFormState = {
  item_id: string;
  shop_name: string;
  location: string;
  price: string;
  quantity: string;
  unit: string;
};

type BasketFormState = {
  item_id: string;
  quantity: string;
  unit: string;
};

const initialItemForm: ItemFormState = {
  name: "",
  category: "",
  brand: "",
  default_unit: "unit",
};

const initialPriceForm: PriceFormState = {
  item_id: "",
  shop_name: "",
  location: "",
  price: "",
  quantity: "1",
  unit: "unit",
};

const initialBasketForm: BasketFormState = {
  item_id: "",
  quantity: "1",
  unit: "unit",
};

const currencyFormatter = new Intl.NumberFormat("en-ZM", {
  style: "currency",
  currency: "ZMW",
});

const dateFormatter = new Intl.DateTimeFormat("en-ZM", {
  dateStyle: "medium",
  timeStyle: "short",
});

export default function App() {
  const [items, setItems] = useState<Item[]>([]);
  const [prices, setPrices] = useState<PriceObservation[]>([]);
  const [basketItems, setBasketItems] = useState<BasketItem[]>([]);
  const [basketTotal, setBasketTotal] = useState<BasketTotal | null>(null);
  const [summary, setSummary] = useState<AnalyticsSummary | null>(null);

  const [itemForm, setItemForm] = useState<ItemFormState>(initialItemForm);
  const [priceForm, setPriceForm] = useState<PriceFormState>(initialPriceForm);
  const [basketForm, setBasketForm] =
    useState<BasketFormState>(initialBasketForm);

  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const itemNameById = useMemo(() => {
    return new Map(items.map((item) => [item.id, item.name]));
  }, [items]);

  async function refreshData() {
    setError(null);

    const [
      nextItems,
      nextPrices,
      nextBasketItems,
      nextBasketTotal,
      nextSummary,
    ] = await Promise.all([
      listItems(),
      listPriceObservations(),
      listBasketItems(),
      getBasketTotal(),
      getAnalyticsSummary(),
    ]);

    setItems(nextItems);
    setPrices(nextPrices);
    setBasketItems(nextBasketItems);
    setBasketTotal(nextBasketTotal);
    setSummary(nextSummary);
  }

  useEffect(() => {
    refreshData()
      .catch((currentError: unknown) => {
        setError(
          currentError instanceof Error
            ? currentError.message
            : "Failed to load dashboard data",
        );
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, []);

  async function handleCreateItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    if (!itemForm.name.trim()) {
      setError("Item name is required");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await createItem({
        name: itemForm.name.trim(),
        category: itemForm.category.trim() || null,
        brand: itemForm.brand.trim() || null,
        default_unit: itemForm.default_unit.trim() || "unit",
      });

      setItemForm(initialItemForm);
      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to create item",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleCreatePrice(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const itemId = Number(priceForm.item_id);
    const price = Number(priceForm.price);
    const quantity = Number(priceForm.quantity);

    if (!itemId || !price || !quantity || !priceForm.shop_name.trim()) {
      setError("Item, shop, price, and quantity are required");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await createPriceObservation({
        item_id: itemId,
        shop_name: priceForm.shop_name.trim(),
        location: priceForm.location.trim() || null,
        price,
        quantity,
        unit: priceForm.unit.trim() || "unit",
      });

      setPriceForm({
        ...initialPriceForm,
        item_id: priceForm.item_id,
        unit: priceForm.unit || "unit",
      });

      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to create price observation",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleAddBasketItem(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const itemId = Number(basketForm.item_id);
    const quantity = Number(basketForm.quantity);

    if (!itemId || !quantity) {
      setError("Basket item and quantity are required");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await addBasketItem({
        item_id: itemId,
        quantity,
        unit: basketForm.unit.trim() || "unit",
      });

      setBasketForm({
        ...initialBasketForm,
        item_id: basketForm.item_id,
        unit: basketForm.unit || "unit",
      });

      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to add basket item",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main style={styles.page}>
      <header style={styles.header}>
        <div>
          <p style={styles.eyebrow}>Kwacha!</p>
          <h1 style={styles.title}>Snap prices. Track change.</h1>
          <p style={styles.subtitle}>
            Local price tracking, personal basket inflation, and cost-of-living
            visibility for Zambia.
          </p>
        </div>

        <button
          style={styles.secondaryButton}
          onClick={() => void refreshData()}
        >
          Refresh
        </button>
      </header>

      {error ? <div style={styles.error}>{error}</div> : null}

      {isLoading ? (
        <section style={styles.card}>
          <p>Loading dashboard...</p>
        </section>
      ) : (
        <>
          <section style={styles.statsGrid}>
            <StatCard
              label="Items"
              value={summary?.item_count ?? items.length}
            />
            <StatCard
              label="Price observations"
              value={summary?.price_observation_count ?? prices.length}
            />
            <StatCard
              label="Basket items"
              value={summary?.basket_item_count ?? basketItems.length}
            />
            <StatCard
              label="Basket total"
              value={currencyFormatter.format(basketTotal?.total ?? 0)}
            />
          </section>

          <section style={styles.grid}>
            <form style={styles.card} onSubmit={handleCreateItem}>
              <h2 style={styles.sectionTitle}>Add item</h2>

              <label style={styles.label}>
                Name
                <input
                  style={styles.input}
                  value={itemForm.name}
                  onChange={(event) =>
                    setItemForm((current) => ({
                      ...current,
                      name: event.target.value,
                    }))
                  }
                  placeholder="Mealie meal"
                />
              </label>

              <label style={styles.label}>
                Category
                <input
                  style={styles.input}
                  value={itemForm.category}
                  onChange={(event) =>
                    setItemForm((current) => ({
                      ...current,
                      category: event.target.value,
                    }))
                  }
                  placeholder="Food"
                />
              </label>

              <label style={styles.label}>
                Brand
                <input
                  style={styles.input}
                  value={itemForm.brand}
                  onChange={(event) =>
                    setItemForm((current) => ({
                      ...current,
                      brand: event.target.value,
                    }))
                  }
                  placeholder="Optional"
                />
              </label>

              <label style={styles.label}>
                Default unit
                <input
                  style={styles.input}
                  value={itemForm.default_unit}
                  onChange={(event) =>
                    setItemForm((current) => ({
                      ...current,
                      default_unit: event.target.value,
                    }))
                  }
                  placeholder="kg"
                />
              </label>

              <button style={styles.primaryButton} disabled={isSaving}>
                Save item
              </button>
            </form>

            <form style={styles.card} onSubmit={handleCreatePrice}>
              <h2 style={styles.sectionTitle}>Add price observation</h2>

              <label style={styles.label}>
                Item
                <select
                  style={styles.input}
                  value={priceForm.item_id}
                  onChange={(event) =>
                    setPriceForm((current) => ({
                      ...current,
                      item_id: event.target.value,
                    }))
                  }
                >
                  <option value="">Select item</option>
                  {items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </label>

              <label style={styles.label}>
                Shop
                <input
                  style={styles.input}
                  value={priceForm.shop_name}
                  onChange={(event) =>
                    setPriceForm((current) => ({
                      ...current,
                      shop_name: event.target.value,
                    }))
                  }
                  placeholder="Shoprite"
                />
              </label>

              <label style={styles.label}>
                Location
                <input
                  style={styles.input}
                  value={priceForm.location}
                  onChange={(event) =>
                    setPriceForm((current) => ({
                      ...current,
                      location: event.target.value,
                    }))
                  }
                  placeholder="Lusaka"
                />
              </label>

              <div style={styles.twoColumn}>
                <label style={styles.label}>
                  Price
                  <input
                    style={styles.input}
                    type="number"
                    min="0"
                    step="0.01"
                    value={priceForm.price}
                    onChange={(event) =>
                      setPriceForm((current) => ({
                        ...current,
                        price: event.target.value,
                      }))
                    }
                    placeholder="250"
                  />
                </label>

                <label style={styles.label}>
                  Quantity
                  <input
                    style={styles.input}
                    type="number"
                    min="0"
                    step="0.01"
                    value={priceForm.quantity}
                    onChange={(event) =>
                      setPriceForm((current) => ({
                        ...current,
                        quantity: event.target.value,
                      }))
                    }
                  />
                </label>
              </div>

              <label style={styles.label}>
                Unit
                <input
                  style={styles.input}
                  value={priceForm.unit}
                  onChange={(event) =>
                    setPriceForm((current) => ({
                      ...current,
                      unit: event.target.value,
                    }))
                  }
                  placeholder="kg"
                />
              </label>

              <button style={styles.primaryButton} disabled={isSaving}>
                Save price
              </button>
            </form>

            <form style={styles.card} onSubmit={handleAddBasketItem}>
              <h2 style={styles.sectionTitle}>Add to basket</h2>

              <label style={styles.label}>
                Item
                <select
                  style={styles.input}
                  value={basketForm.item_id}
                  onChange={(event) =>
                    setBasketForm((current) => ({
                      ...current,
                      item_id: event.target.value,
                    }))
                  }
                >
                  <option value="">Select item</option>
                  {items.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name}
                    </option>
                  ))}
                </select>
              </label>

              <label style={styles.label}>
                Quantity
                <input
                  style={styles.input}
                  type="number"
                  min="0"
                  step="0.01"
                  value={basketForm.quantity}
                  onChange={(event) =>
                    setBasketForm((current) => ({
                      ...current,
                      quantity: event.target.value,
                    }))
                  }
                />
              </label>

              <label style={styles.label}>
                Unit
                <input
                  style={styles.input}
                  value={basketForm.unit}
                  onChange={(event) =>
                    setBasketForm((current) => ({
                      ...current,
                      unit: event.target.value,
                    }))
                  }
                  placeholder="kg"
                />
              </label>

              <button style={styles.primaryButton} disabled={isSaving}>
                Add basket item
              </button>
            </form>
          </section>

          <section style={styles.card}>
            <div style={styles.sectionHeader}>
              <h2 style={styles.sectionTitle}>Basket total</h2>
              <strong style={styles.total}>
                {currencyFormatter.format(basketTotal?.total ?? 0)}
              </strong>
            </div>

            <div style={styles.tableWrap}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Item</th>
                    <th style={styles.th}>Quantity</th>
                    <th style={styles.th}>Latest price/unit</th>
                    <th style={styles.th}>Shop</th>
                    <th style={styles.th}>Line total</th>
                    <th style={styles.th}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {basketTotal?.items.length ? (
                    basketTotal.items.map((line) => (
                      <tr key={line.basket_item_id}>
                        <td style={styles.td}>{line.item_name}</td>
                        <td style={styles.td}>
                          {line.quantity} {line.unit}
                        </td>
                        <td style={styles.td}>
                          {line.price_per_unit === null
                            ? "—"
                            : currencyFormatter.format(line.price_per_unit)}
                        </td>
                        <td style={styles.td}>{line.shop_name ?? "—"}</td>
                        <td style={styles.td}>
                          {line.line_total === null
                            ? "—"
                            : currencyFormatter.format(line.line_total)}
                        </td>
                        <td style={styles.td}>{line.status}</td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td style={styles.emptyCell} colSpan={6}>
                        No basket items yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>

          <section style={styles.card}>
            <h2 style={styles.sectionTitle}>Recent price observations</h2>

            <div style={styles.tableWrap}>
              <table style={styles.table}>
                <thead>
                  <tr>
                    <th style={styles.th}>Item</th>
                    <th style={styles.th}>Shop</th>
                    <th style={styles.th}>Location</th>
                    <th style={styles.th}>Price</th>
                    <th style={styles.th}>Price/unit</th>
                    <th style={styles.th}>Observed</th>
                  </tr>
                </thead>
                <tbody>
                  {prices.length ? (
                    prices.slice(0, 10).map((price) => (
                      <tr key={price.id}>
                        <td style={styles.td}>
                          {itemNameById.get(price.item_id) ??
                            `Item #${price.item_id}`}
                        </td>
                        <td style={styles.td}>{price.shop_name}</td>
                        <td style={styles.td}>{price.location ?? "—"}</td>
                        <td style={styles.td}>
                          {currencyFormatter.format(price.price)} /{" "}
                          {price.quantity} {price.unit}
                        </td>
                        <td style={styles.td}>
                          {currencyFormatter.format(price.price_per_unit)}
                        </td>
                        <td style={styles.td}>
                          {dateFormatter.format(new Date(price.observed_at))}
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td style={styles.emptyCell} colSpan={6}>
                        No price observations yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </section>
        </>
      )}
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <article style={styles.statCard}>
      <p style={styles.statLabel}>{label}</p>
      <strong style={styles.statValue}>{value}</strong>
    </article>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    background: "#f8f4ea",
    color: "#1f1f1f",
    fontFamily:
      'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
    padding: "32px",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    gap: "24px",
    alignItems: "flex-start",
    marginBottom: "24px",
  },
  eyebrow: {
    margin: 0,
    color: "#9a7a21",
    fontWeight: 800,
    textTransform: "uppercase",
    letterSpacing: "0.08em",
  },
  title: {
    margin: "6px 0",
    fontSize: "40px",
    lineHeight: 1.1,
  },
  subtitle: {
    margin: 0,
    maxWidth: "760px",
    color: "#5f5b52",
    fontSize: "16px",
  },
  statsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
    gap: "16px",
    marginBottom: "16px",
  },
  grid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "16px",
    marginBottom: "16px",
  },
  card: {
    background: "#fffdf8",
    border: "1px solid #e5dcc8",
    borderRadius: "18px",
    padding: "20px",
    boxShadow: "0 10px 30px rgba(31, 31, 31, 0.06)",
    marginBottom: "16px",
  },
  statCard: {
    background: "#fffdf8",
    border: "1px solid #e5dcc8",
    borderRadius: "18px",
    padding: "18px",
    boxShadow: "0 10px 30px rgba(31, 31, 31, 0.06)",
  },
  statLabel: {
    margin: "0 0 8px",
    color: "#6b6254",
    fontSize: "14px",
  },
  statValue: {
    fontSize: "28px",
  },
  sectionHeader: {
    display: "flex",
    justifyContent: "space-between",
    gap: "16px",
    alignItems: "center",
    marginBottom: "12px",
  },
  sectionTitle: {
    margin: "0 0 14px",
    fontSize: "20px",
  },
  total: {
    fontSize: "24px",
    color: "#8a6d1d",
  },
  label: {
    display: "grid",
    gap: "6px",
    marginBottom: "12px",
    color: "#4c463d",
    fontSize: "14px",
    fontWeight: 650,
  },
  input: {
    width: "100%",
    boxSizing: "border-box",
    border: "1px solid #d8cdb7",
    borderRadius: "12px",
    padding: "11px 12px",
    background: "#fff",
    color: "#1f1f1f",
    font: "inherit",
  },
  twoColumn: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "12px",
  },
  primaryButton: {
    width: "100%",
    border: 0,
    borderRadius: "12px",
    padding: "12px 14px",
    background: "#1f1f1f",
    color: "#fff",
    fontWeight: 800,
    cursor: "pointer",
  },
  secondaryButton: {
    border: "1px solid #d8cdb7",
    borderRadius: "12px",
    padding: "10px 14px",
    background: "#fffdf8",
    color: "#1f1f1f",
    fontWeight: 750,
    cursor: "pointer",
  },
  error: {
    background: "#fff1f1",
    border: "1px solid #f0b8b8",
    color: "#8a1f1f",
    borderRadius: "14px",
    padding: "12px 14px",
    marginBottom: "16px",
  },
  tableWrap: {
    overflowX: "auto",
  },
  table: {
    width: "100%",
    borderCollapse: "collapse",
    fontSize: "14px",
  },
  th: {
    textAlign: "left",
    borderBottom: "1px solid #e5dcc8",
    padding: "10px 8px",
    color: "#6b6254",
    whiteSpace: "nowrap",
  },
  td: {
    borderBottom: "1px solid #eee6d6",
    padding: "12px 8px",
    verticalAlign: "top",
    whiteSpace: "nowrap",
  },
  emptyCell: {
    padding: "18px 8px",
    color: "#6b6254",
    textAlign: "center",
  },
} satisfies Record<string, React.CSSProperties>;
