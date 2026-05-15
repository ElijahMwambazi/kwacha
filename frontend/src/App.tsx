import { FormEvent, useEffect, useMemo, useState } from "react";
import {
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import {
  getAnalyticsSummary,
  getBasketInflation,
  getPriceTrends,
  getShopComparison,
  getIndicatorTrends,
} from "./api/analytics";
import {
  addBasketItem,
  getBasketTotal,
  listBasketItems,
  removeBasketItem,
  updateBasketItem,
} from "./api/basket";
import { createItem, deleteItem, listItems, updateItem } from "./api/items";
import {
  createPriceObservation,
  deletePriceObservation,
  listPriceObservations,
  updatePriceObservation,
} from "./api/prices";
import { downloadCsv, type ExportKind } from "./api/export";
import {
  downloadImportTemplate,
  importPriceObservationsCsv,
  importRawPriceCollectionsCsv,
} from "./api/imports";
import {
  createIndicator,
  deleteIndicator,
  listIndicators,
} from "./api/indicators";
import {
  compareItemPricePredictions,
  getPriceModelStatus,
  listPriceModelTrainingRuns,
  predictNextBasketTotal,
  predictNextItemPrice,
  predictNextItemPriceWithMl,
  resetPriceModel,
  trainPriceModel,
} from "./api/predictions";
import {
  approveRawCollection,
  createRawCollection,
  listRawCollections,
  rejectRawCollection,
} from "./api/rawCollections";
import type {
  AnalyticsSummary,
  BasketInflationPoint,
  IndicatorTrendPoint,
  PriceTrendPoint,
  ShopComparison,
} from "./types/analytics";
import type { BasketItem, BasketTotal } from "./types/basket";
import type { Item } from "./types/item";
import type { PriceObservation } from "./types/price";
import type { PublicIndicator } from "./types/indicators";
import type {
  BasketTotalPrediction,
  ItemPredictionComparison,
  ItemPricePrediction,
  MLItemPricePrediction,
  ModelTrainingRun,
  PriceModelStatus,
  PriceModelTrainingResult,
} from "./types/prediction";
import type { RawCollection } from "./types/rawCollection";

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

type IndicatorFormState = {
  name: string;
  value: string;
  unit: string;
  source: string;
  observed_at: string;
};

type RawCollectionFormState = {
  item_name: string;
  category: string;
  brand: string;
  shop_name: string;
  location: string;
  price: string;
  quantity: string;
  unit: string;
  source: string;
  notes: string;
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

const initialIndicatorForm: IndicatorFormState = {
  name: "exchange_rate_usd_zmw",
  value: "",
  unit: "ZMW",
  source: "",
  observed_at: "",
};

const currencyFormatter = new Intl.NumberFormat("en-ZM", {
  style: "currency",
  currency: "ZMW",
});

const dateFormatter = new Intl.DateTimeFormat("en-ZM", {
  dateStyle: "medium",
  timeStyle: "short",
});

const initialRawCollectionForm: RawCollectionFormState = {
  item_name: "",
  category: "",
  brand: "",
  shop_name: "",
  location: "",
  price: "",
  quantity: "1",
  unit: "unit",
  source: "",
  notes: "",
};

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

  const [priceTrends, setPriceTrends] = useState<PriceTrendPoint[]>([]);
  const [shopComparison, setShopComparison] = useState<ShopComparison[]>([]);
  const [selectedAnalyticsItemId, setSelectedAnalyticsItemId] =
    useState<string>("");
  const [basketInflation, setBasketInflation] = useState<
    BasketInflationPoint[]
  >([]);
  const [indicatorTrends, setIndicatorTrends] = useState<IndicatorTrendPoint[]>(
    [],
  );
  const [selectedIndicatorName, setSelectedIndicatorName] =
    useState<string>("");

  const [indicators, setIndicators] = useState<PublicIndicator[]>([]);
  const [indicatorForm, setIndicatorForm] =
    useState<IndicatorFormState>(initialIndicatorForm);

  const [selectedPredictionItemId, setSelectedPredictionItemId] =
    useState<string>("");
  const [itemPrediction, setItemPrediction] =
    useState<ItemPricePrediction | null>(null);
  const [basketPrediction, setBasketPrediction] =
    useState<BasketTotalPrediction | null>(null);
  const [predictionWindow, setPredictionWindow] = useState<string>("3");

  const [mlItemPrediction, setMlItemPrediction] =
    useState<MLItemPricePrediction | null>(null);
  const [modelTrainingResult, setModelTrainingResult] =
    useState<PriceModelTrainingResult | null>(null);
  const [predictionComparison, setPredictionComparison] =
    useState<ItemPredictionComparison | null>(null);
  const [priceModelStatus, setPriceModelStatus] =
    useState<PriceModelStatus | null>(null);
  const [modelTrainingRuns, setModelTrainingRuns] = useState<
    ModelTrainingRun[]
  >([]);

  const [rawCollections, setRawCollections] = useState<RawCollection[]>([]);
  const [rawCollectionForm, setRawCollectionForm] =
    useState<RawCollectionFormState>(initialRawCollectionForm);

  const itemNameById = useMemo(() => {
    return new Map(items.map((item) => [item.id, item.name]));
  }, [items]);
  const chartData = useMemo(() => {
    return priceTrends.map((point) => ({
      ...point,
      observed_label: dateFormatter.format(new Date(point.observed_at)),
    }));
  }, [priceTrends]);
  const basketInflationChartData = useMemo(() => {
    return basketInflation.map((point) => ({
      ...point,
      monthly_change_label:
        point.monthly_change_percent === null
          ? "—"
          : `${point.monthly_change_percent}%`,
    }));
  }, [basketInflation]);
  const indicatorTrendChartData = useMemo(() => {
    return indicatorTrends.map((point) => ({
      ...point,
      observed_label: dateFormatter.format(new Date(point.observed_at)),
    }));
  }, [indicatorTrends]);

  async function refreshData(
    itemIdForAnalytics = selectedAnalyticsItemId,
    indicatorNameForAnalytics = selectedIndicatorName,
  ) {
    setError(null);

    const analyticsItemId = itemIdForAnalytics
      ? Number(itemIdForAnalytics)
      : undefined;
    const indicatorName = indicatorNameForAnalytics.trim() || undefined;

    const [
      nextItems,
      nextPrices,
      nextBasketItems,
      nextBasketTotal,
      nextSummary,
      nextPriceTrends,
      nextShopComparison,
      nextBasketInflation,
      nextIndicators,
      nextIndicatorTrends,
      nextBasketPrediction,
      nextPriceModelStatus,
      nextModelTrainingRuns,
      nextRawCollections,
    ] = await Promise.all([
      listItems(),
      listPriceObservations(),
      listBasketItems(),
      getBasketTotal(),
      getAnalyticsSummary(),
      getPriceTrends(analyticsItemId),
      getShopComparison(analyticsItemId),
      getBasketInflation(),
      listIndicators(),
      getIndicatorTrends(indicatorName),
      predictNextBasketTotal(Number(predictionWindow) || 3).catch(() => null),
      getPriceModelStatus(),
      listPriceModelTrainingRuns(),
      listRawCollections("pending"),
    ]);

    setItems(nextItems);
    setPrices(nextPrices);
    setBasketItems(nextBasketItems);
    setBasketTotal(nextBasketTotal);
    setSummary(nextSummary);
    setPriceTrends(nextPriceTrends);
    setShopComparison(nextShopComparison);
    setBasketInflation(nextBasketInflation);
    setIndicators(nextIndicators);
    setIndicatorTrends(nextIndicatorTrends);
    setBasketPrediction(nextBasketPrediction);
    setPriceModelStatus(nextPriceModelStatus);
    setModelTrainingRuns(nextModelTrainingRuns);
    setRawCollections(nextRawCollections);
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

  async function handleDownloadPriceImportTemplate() {
    setError(null);

    try {
      await downloadImportTemplate("prices");
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to download import template",
      );
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

  async function handleExport(kind: ExportKind) {
    setError(null);

    try {
      await downloadCsv(kind);
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to export CSV",
      );
    }
  }

  async function handleDeleteItem(item: Item) {
    const confirmed = window.confirm(
      `Delete "${item.name}"? This will also delete related price observations and basket entries.`,
    );

    if (!confirmed) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await deleteItem(item.id);
      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to delete item",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDeletePriceObservation(price: PriceObservation) {
    const itemName =
      itemNameById.get(price.item_id) ?? `Item #${price.item_id}`;
    const confirmed = window.confirm(
      `Delete price observation for "${itemName}"?`,
    );

    if (!confirmed) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await deletePriceObservation(price.id);
      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to delete price observation",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleRemoveBasketItem(basketItemId: number) {
    const confirmed = window.confirm("Remove this item from the basket?");

    if (!confirmed) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await removeBasketItem(basketItemId);
      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to remove basket item",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleEditItem(item: Item) {
    const name = window.prompt("Item name", item.name);

    if (name === null) {
      return;
    }

    const category = window.prompt("Category", item.category ?? "");

    if (category === null) {
      return;
    }

    const brand = window.prompt("Brand", item.brand ?? "");

    if (brand === null) {
      return;
    }

    const defaultUnit = window.prompt("Default unit", item.default_unit);

    if (defaultUnit === null) {
      return;
    }

    if (!name.trim() || !defaultUnit.trim()) {
      setError("Item name and default unit are required");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await updateItem(item.id, {
        name: name.trim(),
        category: category.trim() || null,
        brand: brand.trim() || null,
        default_unit: defaultUnit.trim(),
      });

      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to update item",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleEditPriceObservation(price: PriceObservation) {
    const shopName = window.prompt("Shop name", price.shop_name);

    if (shopName === null) {
      return;
    }

    const location = window.prompt("Location", price.location ?? "");

    if (location === null) {
      return;
    }

    const priceValue = window.prompt("Price", String(price.price));

    if (priceValue === null) {
      return;
    }

    const quantity = window.prompt("Quantity", String(price.quantity));

    if (quantity === null) {
      return;
    }

    const unit = window.prompt("Unit", price.unit);

    if (unit === null) {
      return;
    }

    const parsedPrice = Number(priceValue);
    const parsedQuantity = Number(quantity);

    if (!shopName.trim() || !parsedPrice || !parsedQuantity || !unit.trim()) {
      setError("Shop, price, quantity, and unit are required");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await updatePriceObservation(price.id, {
        shop_name: shopName.trim(),
        location: location.trim() || null,
        price: parsedPrice,
        quantity: parsedQuantity,
        unit: unit.trim(),
      });

      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to update price observation",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleEditBasketLine(line: BasketTotal["items"][number]) {
    const quantity = window.prompt("Basket quantity", String(line.quantity));

    if (quantity === null) {
      return;
    }

    const unit = window.prompt("Basket unit", line.unit);

    if (unit === null) {
      return;
    }

    const parsedQuantity = Number(quantity);

    if (!parsedQuantity || !unit.trim()) {
      setError("Basket quantity and unit are required");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await updateBasketItem(line.basket_item_id, {
        quantity: parsedQuantity,
        unit: unit.trim(),
      });

      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to update basket item",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleAnalyticsItemChange(itemId: string) {
    setSelectedAnalyticsItemId(itemId);

    try {
      await refreshData(itemId);
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to refresh analytics",
      );
    }
  }

  async function handleImportPricesCsv(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const result = await importPriceObservationsCsv(file);

      await refreshData();

      window.alert(
        `Imported ${result.imported_count} price observations. Created ${result.created_item_count} new items.`,
      );
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to import price CSV",
      );
    } finally {
      event.target.value = "";
      setIsSaving(false);
    }
  }

  async function handleImportRawPricesCsv(
    event: React.ChangeEvent<HTMLInputElement>,
  ) {
    const file = event.target.files?.[0];

    if (!file) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const result = await importRawPriceCollectionsCsv(file);

      await refreshData();

      window.alert(
        `Imported ${result.imported_count} raw price rows into the pending review queue.`,
      );
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to import raw price CSV",
      );
    } finally {
      event.target.value = "";
      setIsSaving(false);
    }
  }

  async function handleIndicatorTrendChange(name: string) {
    setSelectedIndicatorName(name);

    try {
      await refreshData(selectedAnalyticsItemId, name);
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to refresh indicator trends",
      );
    }
  }

  async function handleCreateIndicator(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const value = Number(indicatorForm.value);

    if (!indicatorForm.name.trim() || !value) {
      setError("Indicator name and value are required");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await createIndicator({
        name: indicatorForm.name.trim(),
        value,
        unit: indicatorForm.unit.trim() || null,
        source: indicatorForm.source.trim() || null,
        observed_at: indicatorForm.observed_at || undefined,
      });

      setIndicatorForm({
        ...initialIndicatorForm,
        name: indicatorForm.name,
        unit: indicatorForm.unit,
        source: indicatorForm.source,
      });

      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to create public indicator",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleDeleteIndicator(indicator: PublicIndicator) {
    const confirmed = window.confirm(`Delete indicator "${indicator.name}"?`);

    if (!confirmed) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await deleteIndicator(indicator.id);
      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to delete public indicator",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handlePredictItemPrice(
    itemIdValue = selectedPredictionItemId,
  ) {
    const itemId = Number(itemIdValue);
    const windowSize = Number(predictionWindow) || 3;

    if (!itemId) {
      setItemPrediction(null);
      return;
    }

    setError(null);

    try {
      const prediction = await predictNextItemPrice(itemId, windowSize);
      setItemPrediction(prediction);
    } catch (currentError) {
      setItemPrediction(null);
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to predict item price",
      );
    }
  }

  async function handlePredictionItemChange(itemId: string) {
    setSelectedPredictionItemId(itemId);

    await handlePredictItemPrice(itemId);
    await handlePredictItemPriceWithMl(itemId);
    await handleComparePredictions(itemId);
  }

  async function handlePredictionWindowChange(windowValue: string) {
    setPredictionWindow(windowValue);

    const windowSize = Number(windowValue) || 3;

    try {
      const nextBasketPrediction = await predictNextBasketTotal(windowSize);
      setBasketPrediction(nextBasketPrediction);

      if (selectedPredictionItemId) {
        await handlePredictItemPrice(selectedPredictionItemId);
        await handleComparePredictions(selectedPredictionItemId);
      }
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to refresh predictions",
      );
    }
  }

  async function handleTrainPriceModel() {
    setIsSaving(true);
    setError(null);

    try {
      const result = await trainPriceModel();
      setModelTrainingResult(result);

      const status = await getPriceModelStatus();
      setPriceModelStatus(status);

      const runs = await listPriceModelTrainingRuns();
      setModelTrainingRuns(runs);

      if (selectedPredictionItemId) {
        await handlePredictItemPriceWithMl(selectedPredictionItemId);
        await handleComparePredictions(selectedPredictionItemId);
      }
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to train price model",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleResetPriceModel() {
    const confirmed = window.confirm("Reset the trained price model?");

    if (!confirmed) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      const status = await resetPriceModel();

      setPriceModelStatus(status);
      setModelTrainingRuns([]);
      setMlItemPrediction(null);
      setModelTrainingResult(null);
      setPredictionComparison((current) =>
        current
          ? {
              ...current,
              ml: null,
              ml_error: "Price model has not been trained yet",
            }
          : null,
      );
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to reset price model",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handlePredictItemPriceWithMl(
    itemIdValue = selectedPredictionItemId,
  ) {
    const itemId = Number(itemIdValue);

    if (!itemId) {
      setMlItemPrediction(null);
      return;
    }

    setError(null);

    try {
      const prediction = await predictNextItemPriceWithMl(itemId);
      setMlItemPrediction(prediction);
    } catch {
      setMlItemPrediction(null);
    }
  }

  async function handleComparePredictions(
    itemIdValue = selectedPredictionItemId,
  ) {
    const itemId = Number(itemIdValue);
    const windowSize = Number(predictionWindow) || 3;

    if (!itemId) {
      setPredictionComparison(null);
      return;
    }

    setError(null);

    try {
      const comparison = await compareItemPricePredictions(itemId, windowSize);
      setPredictionComparison(comparison);
    } catch (currentError) {
      setPredictionComparison(null);
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to compare predictions",
      );
    }
  }

  async function handleCreateRawCollection(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const price = Number(rawCollectionForm.price);
    const quantity = Number(rawCollectionForm.quantity);

    if (
      !rawCollectionForm.item_name.trim() ||
      !rawCollectionForm.shop_name.trim() ||
      !price ||
      !quantity
    ) {
      setError("Raw item name, shop, price, and quantity are required");
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await createRawCollection({
        item_name: rawCollectionForm.item_name.trim(),
        category: rawCollectionForm.category.trim() || null,
        brand: rawCollectionForm.brand.trim() || null,
        shop_name: rawCollectionForm.shop_name.trim(),
        location: rawCollectionForm.location.trim() || null,
        price,
        quantity,
        unit: rawCollectionForm.unit.trim() || "unit",
        source: rawCollectionForm.source.trim() || null,
        notes: rawCollectionForm.notes.trim() || null,
      });

      setRawCollectionForm(initialRawCollectionForm);
      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to create raw collection",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleApproveRawCollection(raw: RawCollection) {
    setIsSaving(true);
    setError(null);

    try {
      await approveRawCollection(raw.id);
      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to approve raw collection",
      );
    } finally {
      setIsSaving(false);
    }
  }

  async function handleRejectRawCollection(raw: RawCollection) {
    const confirmed = window.confirm(
      `Reject raw collection for "${raw.item_name}"?`,
    );

    if (!confirmed) {
      return;
    }

    setIsSaving(true);
    setError(null);

    try {
      await rejectRawCollection(raw.id);
      await refreshData();
    } catch (currentError) {
      setError(
        currentError instanceof Error
          ? currentError.message
          : "Failed to reject raw collection",
      );
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#f8f4ea] px-4 py-6 text-[#1f1f1f] sm:px-6 lg:px-8">
      <div className="mx-auto max-w-7xl">
        <header className="mb-6 flex flex-col justify-between gap-5 md:flex-row md:items-start">
          <div>
            <p className="text-sm font-extrabold uppercase tracking-[0.14em] text-[#9a7a21]">
              Kwacha!
            </p>
            <h1 className="mt-2 text-4xl font-black tracking-tight sm:text-5xl">
              Snap prices. Track change.
            </h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-[#5f5b52]">
              Local price tracking, personal basket inflation, and
              cost-of-living visibility for Zambia.
            </p>
          </div>

          <div className="flex flex-wrap gap-2">
            <button
              className="w-fit rounded-xl border border-[#d8cdb7] bg-[#fffdf8] px-4 py-2.5 font-bold text-[#1f1f1f] shadow-sm transition hover:bg-white"
              onClick={() => void refreshData()}
            >
              Refresh
            </button>

            <button
              className="w-fit rounded-xl border border-[#d8cdb7] bg-[#fffdf8] px-4 py-2.5 font-bold text-[#1f1f1f] shadow-sm transition hover:bg-white"
              onClick={() => void handleExport("items")}
            >
              Export items
            </button>

            <button
              className="w-fit rounded-xl border border-[#d8cdb7] bg-[#fffdf8] px-4 py-2.5 font-bold text-[#1f1f1f] shadow-sm transition hover:bg-white"
              onClick={() => void handleExport("prices")}
            >
              Export prices
            </button>

            <button
              className="w-fit rounded-xl border border-[#d8cdb7] bg-[#fffdf8] px-4 py-2.5 font-bold text-[#1f1f1f] shadow-sm transition hover:bg-white"
              onClick={() => void handleExport("basket")}
            >
              Export basket
            </button>

            <label className="w-fit cursor-pointer rounded-xl border border-[#d8cdb7] bg-[#fffdf8] px-4 py-2.5 font-bold text-[#1f1f1f] shadow-sm transition hover:bg-white">
              Import prices
              <input
                className="hidden"
                type="file"
                accept=".csv,text/csv"
                disabled={isSaving}
                onChange={(event) => void handleImportPricesCsv(event)}
              />
            </label>

            <label className="w-fit cursor-pointer rounded-xl border border-[#d8cdb7] bg-[#fffdf8] px-4 py-2.5 font-bold text-[#1f1f1f] shadow-sm transition hover:bg-white">
              Import raw prices
              <input
                className="hidden"
                type="file"
                accept=".csv,text/csv"
                disabled={isSaving}
                onChange={(event) => void handleImportRawPricesCsv(event)}
              />
            </label>

            <button
              className="w-fit rounded-xl border border-[#d8cdb7] bg-[#fffdf8] px-4 py-2.5 font-bold text-[#1f1f1f] shadow-sm transition hover:bg-white"
              onClick={() => void handleDownloadPriceImportTemplate()}
            >
              Download import template
            </button>

            <button
              className="w-fit rounded-xl border border-[#d8cdb7] bg-[#fffdf8] px-4 py-2.5 font-bold text-[#1f1f1f] shadow-sm transition hover:bg-white"
              onClick={() => void handleExport("ml-prices")}
            >
              Export ML dataset
            </button>
          </div>
        </header>

        {error ? (
          <div className="mb-4 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm font-medium text-red-800">
            {error}
          </div>
        ) : null}

        {isLoading ? (
          <section className="rounded-3xl border border-[#e5dcc8] bg-[#fffdf8] p-5 shadow-[0_10px_30px_rgba(31,31,31,0.06)]">
            <p className="text-[#5f5b52]">Loading dashboard...</p>
          </section>
        ) : (
          <>
            <section className="mb-4 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
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

            {/* Price analytics */}
            <section className="card">
              <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
                <div>
                  <h2 className="section-title mb-1">Price analytics</h2>
                  <p className="text-sm text-[#6b6254]">
                    Track price-per-unit changes and compare shops.
                  </p>
                </div>

                <label className="min-w-64 text-sm font-bold text-[#4c463d]">
                  Filter item
                  <select
                    className="form-input mt-1"
                    value={selectedAnalyticsItemId}
                    onChange={(event) =>
                      void handleAnalyticsItemChange(event.target.value)
                    }
                  >
                    <option value="">All items</option>
                    {items.map((item) => (
                      <option key={item.id} value={item.id}>
                        {item.name}
                      </option>
                    ))}
                  </select>
                </label>
              </div>

              <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Price trend
                  </h3>

                  {chartData.length ? (
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={chartData}>
                          <XAxis
                            dataKey="observed_label"
                            tick={{ fontSize: 12 }}
                            interval="preserveStartEnd"
                          />
                          <YAxis tick={{ fontSize: 12 }} />
                          <Tooltip
                            formatter={(value) =>
                              typeof value === "number"
                                ? currencyFormatter.format(value)
                                : value
                            }
                            labelFormatter={(label) => `Observed: ${label}`}
                          />
                          <Line
                            type="monotone"
                            dataKey="price_per_unit"
                            name="Price per unit"
                            strokeWidth={3}
                            dot
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="flex h-72 items-center justify-center rounded-xl bg-[#f8f4ea] text-sm text-[#6b6254]">
                      No price trend data yet.
                    </div>
                  )}
                </div>

                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Best average shop prices
                  </h3>

                  <div className="overflow-x-auto">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <TableHead>Item</TableHead>
                          <TableHead>Shop</TableHead>
                          <TableHead>Avg/unit</TableHead>
                        </tr>
                      </thead>
                      <tbody>
                        {shopComparison.length ? (
                          shopComparison.slice(0, 8).map((shop) => (
                            <tr
                              key={`${shop.item_id}-${shop.shop_name}-${shop.location ?? ""}`}
                            >
                              <TableCell>{shop.item_name}</TableCell>
                              <TableCell>
                                {shop.shop_name}
                                {shop.location ? `, ${shop.location}` : ""}
                              </TableCell>
                              <TableCell>
                                {currencyFormatter.format(
                                  shop.avg_price_per_unit,
                                )}
                              </TableCell>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td className="empty-cell" colSpan={3}>
                              No shop comparison data yet.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </section>

            {/* Basket inflation */}
            <section className="card">
              <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
                <div>
                  <h2 className="section-title mb-1">Basket inflation</h2>
                  <p className="text-sm text-[#6b6254]">
                    Track basket cost changes month by month using the latest
                    available item prices.
                  </p>
                </div>

                <strong className="text-2xl font-black text-[#8a6d1d]">
                  {basketInflation.length
                    ? currencyFormatter.format(
                        basketInflation[basketInflation.length - 1]
                          .basket_total,
                      )
                    : currencyFormatter.format(0)}
                </strong>
              </div>

              <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Monthly basket cost
                  </h3>

                  {basketInflationChartData.length ? (
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={basketInflationChartData}>
                          <XAxis dataKey="month" tick={{ fontSize: 12 }} />
                          <YAxis tick={{ fontSize: 12 }} />
                          <Tooltip
                            formatter={(value, name) => {
                              if (
                                name === "basket_total" &&
                                typeof value === "number"
                              ) {
                                return [
                                  currencyFormatter.format(value),
                                  "Basket total",
                                ];
                              }

                              return [value, name];
                            }}
                          />
                          <Line
                            type="monotone"
                            dataKey="basket_total"
                            name="Basket total"
                            strokeWidth={3}
                            dot
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="flex h-72 items-center justify-center rounded-xl bg-[#f8f4ea] text-sm text-[#6b6254]">
                      No basket inflation data yet.
                    </div>
                  )}
                </div>

                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Monthly movement
                  </h3>

                  <div className="overflow-x-auto">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <TableHead>Month</TableHead>
                          <TableHead>Total</TableHead>
                          <TableHead>Change</TableHead>
                          <TableHead>Coverage</TableHead>
                        </tr>
                      </thead>
                      <tbody>
                        {basketInflation.length ? (
                          basketInflation.map((point) => (
                            <tr key={point.month}>
                              <TableCell>{point.month}</TableCell>
                              <TableCell>
                                {currencyFormatter.format(point.basket_total)}
                              </TableCell>
                              <TableCell>
                                {point.monthly_change_percent === null
                                  ? "—"
                                  : `${point.monthly_change_percent}%`}
                              </TableCell>
                              <TableCell>
                                {point.priced_items_count} priced
                                {point.missing_items_count
                                  ? `, ${point.missing_items_count} missing`
                                  : ""}
                              </TableCell>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td className="empty-cell" colSpan={4}>
                              No basket inflation data yet.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </section>

            {/* Forecast baseline */}
            <section className="card">
              <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
                <div>
                  <h2 className="section-title mb-1">Forecast baseline</h2>
                  <p className="text-sm text-[#6b6254]">
                    Compare simple moving-average forecasts against the trained
                    ML model.
                  </p>
                </div>

                <label className="w-40 text-sm font-bold text-[#4c463d]">
                  Window
                  <input
                    className="form-input mt-1"
                    type="number"
                    min="1"
                    max="30"
                    value={predictionWindow}
                    onChange={(event) =>
                      void handlePredictionWindowChange(event.target.value)
                    }
                  />
                </label>
              </div>

              <div className="grid gap-4 lg:grid-cols-3">
                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Item prediction
                  </h3>

                  <label className="form-label">
                    Item
                    <select
                      className="form-input"
                      value={selectedPredictionItemId}
                      onChange={(event) =>
                        void handlePredictionItemChange(event.target.value)
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

                  {itemPrediction ? (
                    <div className="rounded-2xl bg-[#f8f4ea] p-4">
                      <p className="text-sm text-[#6b6254]">
                        {itemPrediction.item_name}
                      </p>
                      <p className="mt-1 text-3xl font-black text-[#1f1f1f]">
                        {currencyFormatter.format(
                          itemPrediction.predicted_price_per_unit,
                        )}
                      </p>
                      <p className="mt-2 text-sm text-[#6b6254]">
                        Moving average · {itemPrediction.observations_used}{" "}
                        observations · {itemPrediction.confidence} confidence
                      </p>
                    </div>
                  ) : (
                    <div className="rounded-2xl bg-[#f8f4ea] p-4 text-sm text-[#6b6254]">
                      Select an item with price history.
                    </div>
                  )}
                </div>

                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <div>
                      <h3 className="text-sm font-black uppercase tracking-wide text-[#6b6254]">
                        ML model
                      </h3>
                      <p className="mt-1 text-xs text-[#6b6254]">
                        {priceModelStatus?.is_trained
                          ? `Trained with ${priceModelStatus.training_rows} rows`
                          : "Not trained yet"}
                      </p>
                    </div>

                    <div className="flex gap-2">
                      <button
                        className="secondary-small-button"
                        disabled={isSaving}
                        onClick={() => void handleTrainPriceModel()}
                      >
                        Train
                      </button>

                      <button
                        className="danger-button"
                        disabled={isSaving || !priceModelStatus?.is_trained}
                        onClick={() => void handleResetPriceModel()}
                      >
                        Reset
                      </button>
                    </div>
                  </div>

                  {mlItemPrediction ? (
                    <div className="rounded-2xl bg-[#f8f4ea] p-4">
                      <p className="text-sm text-[#6b6254]">
                        {mlItemPrediction.item_name}
                      </p>
                      <p className="mt-1 text-3xl font-black text-[#1f1f1f]">
                        {currencyFormatter.format(
                          mlItemPrediction.predicted_price_per_unit,
                        )}
                      </p>
                      <p className="mt-2 text-sm text-[#6b6254]">
                        Random forest · {mlItemPrediction.model.training_rows}{" "}
                        training rows
                      </p>
                    </div>
                  ) : (
                    <div className="rounded-2xl bg-[#f8f4ea] p-4 text-sm text-[#6b6254]">
                      Train the model, then select an item.
                    </div>
                  )}

                  {modelTrainingResult ? (
                    <p className="mt-3 text-xs text-[#6b6254]">
                      Last trained with {modelTrainingResult.training_rows}{" "}
                      rows.
                    </p>
                  ) : null}
                </div>

                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <h3 className="text-sm font-black uppercase tracking-wide text-[#6b6254]">
                      Baseline vs ML
                    </h3>

                    <button
                      className="secondary-small-button"
                      disabled={isSaving || !selectedPredictionItemId}
                      onClick={() => void handleComparePredictions()}
                    >
                      Compare
                    </button>
                  </div>

                  {predictionComparison ? (
                    <div className="grid gap-3">
                      <div className="rounded-2xl bg-[#f8f4ea] p-4">
                        <p className="text-xs font-black uppercase tracking-wide text-[#6b6254]">
                          Baseline
                        </p>
                        <p className="mt-2 text-2xl font-black text-[#1f1f1f]">
                          {currencyFormatter.format(
                            predictionComparison.baseline
                              .predicted_price_per_unit,
                          )}
                        </p>
                      </div>

                      <div className="rounded-2xl bg-[#f8f4ea] p-4">
                        <p className="text-xs font-black uppercase tracking-wide text-[#6b6254]">
                          ML model
                        </p>

                        {predictionComparison.ml ? (
                          <p className="mt-2 text-2xl font-black text-[#1f1f1f]">
                            {currencyFormatter.format(
                              predictionComparison.ml.predicted_price_per_unit,
                            )}
                          </p>
                        ) : (
                          <p className="mt-2 text-sm text-[#6b6254]">
                            {predictionComparison.ml_error ??
                              "ML prediction unavailable"}
                          </p>
                        )}
                      </div>
                    </div>
                  ) : (
                    <div className="rounded-2xl bg-[#f8f4ea] p-4 text-sm text-[#6b6254]">
                      Select an item, then compare predictions.
                    </div>
                  )}
                </div>

                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Training runs
                  </h3>

                  <div className="overflow-x-auto">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <TableHead>Run</TableHead>
                          <TableHead>Rows</TableHead>
                          <TableHead>MAE</TableHead>
                          <TableHead>R²</TableHead>
                          <TableHead>Created</TableHead>
                        </tr>
                      </thead>
                      <tbody>
                        {modelTrainingRuns.length ? (
                          modelTrainingRuns.slice(0, 5).map((run) => (
                            <tr key={run.id}>
                              <TableCell>#{run.id}</TableCell>
                              <TableCell>{run.training_rows}</TableCell>
                              <TableCell>{run.mae ?? "—"}</TableCell>
                              <TableCell>{run.r2 ?? "—"}</TableCell>
                              <TableCell>
                                {dateFormatter.format(new Date(run.created_at))}
                              </TableCell>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td className="empty-cell" colSpan={5}>
                              No model training runs yet.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>

              <div className="mt-4 rounded-2xl border border-[#eee6d6] bg-white p-4">
                <div className="mb-3 flex flex-col justify-between gap-2 sm:flex-row sm:items-center">
                  <h3 className="text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Predicted basket total
                  </h3>

                  <strong className="text-2xl font-black text-[#8a6d1d]">
                    {currencyFormatter.format(
                      basketPrediction?.predicted_total ?? 0,
                    )}
                  </strong>
                </div>

                <div className="overflow-x-auto">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <TableHead>Item</TableHead>
                        <TableHead>Predicted/unit</TableHead>
                        <TableHead>Line total</TableHead>
                        <TableHead>Data</TableHead>
                      </tr>
                    </thead>
                    <tbody>
                      {basketPrediction?.items.length ? (
                        basketPrediction.items.map((line) => (
                          <tr key={line.basket_item_id}>
                            <TableCell>{line.item_name}</TableCell>
                            <TableCell>
                              {line.predicted_price_per_unit === null
                                ? "—"
                                : currencyFormatter.format(
                                    line.predicted_price_per_unit,
                                  )}
                            </TableCell>
                            <TableCell>
                              {line.predicted_line_total === null
                                ? "—"
                                : currencyFormatter.format(
                                    line.predicted_line_total,
                                  )}
                            </TableCell>
                            <TableCell>
                              {line.observations_used} observations
                            </TableCell>
                          </tr>
                        ))
                      ) : (
                        <tr>
                          <td className="empty-cell" colSpan={4}>
                            No basket prediction available yet.
                          </td>
                        </tr>
                      )}
                    </tbody>
                  </table>
                </div>
              </div>
            </section>

            {/* Indicator trends */}
            <section className="card">
              <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
                <div>
                  <h2 className="section-title mb-1">Indicator trends</h2>
                  <p className="text-sm text-[#6b6254]">
                    Track external signals over time for later forecasting
                    features.
                  </p>
                </div>

                <label className="min-w-64 text-sm font-bold text-[#4c463d]">
                  Filter indicator
                  <select
                    className="form-input mt-1"
                    value={selectedIndicatorName}
                    onChange={(event) =>
                      void handleIndicatorTrendChange(event.target.value)
                    }
                  >
                    <option value="">All indicators</option>
                    <option value="exchange_rate_usd_zmw">
                      USD/ZMW exchange rate
                    </option>
                    <option value="fuel_price_petrol">
                      Fuel price - petrol
                    </option>
                    <option value="fuel_price_diesel">
                      Fuel price - diesel
                    </option>
                    <option value="official_inflation">
                      Official inflation
                    </option>
                  </select>
                </label>
              </div>

              <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr]">
                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Indicator value trend
                  </h3>

                  {indicatorTrendChartData.length ? (
                    <div className="h-72">
                      <ResponsiveContainer width="100%" height="100%">
                        <LineChart data={indicatorTrendChartData}>
                          <XAxis
                            dataKey="observed_label"
                            tick={{ fontSize: 12 }}
                            interval="preserveStartEnd"
                          />
                          <YAxis tick={{ fontSize: 12 }} />
                          <Tooltip
                            formatter={(value, name) => {
                              if (name === "value") {
                                return [value, "Value"];
                              }

                              return [value, name];
                            }}
                            labelFormatter={(label) => `Observed: ${label}`}
                          />
                          <Line
                            type="monotone"
                            dataKey="value"
                            name="Value"
                            strokeWidth={3}
                            dot
                          />
                        </LineChart>
                      </ResponsiveContainer>
                    </div>
                  ) : (
                    <div className="flex h-72 items-center justify-center rounded-xl bg-[#f8f4ea] text-sm text-[#6b6254]">
                      No indicator trend data yet.
                    </div>
                  )}
                </div>

                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Recent indicator readings
                  </h3>

                  <div className="overflow-x-auto">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <TableHead>Name</TableHead>
                          <TableHead>Value</TableHead>
                          <TableHead>Observed</TableHead>
                        </tr>
                      </thead>
                      <tbody>
                        {indicatorTrends.length ? (
                          indicatorTrends
                            .slice(-8)
                            .reverse()
                            .map((point) => (
                              <tr key={point.indicator_id}>
                                <TableCell>{point.name}</TableCell>
                                <TableCell>
                                  {point.value} {point.unit ?? ""}
                                </TableCell>
                                <TableCell>
                                  {dateFormatter.format(
                                    new Date(point.observed_at),
                                  )}
                                </TableCell>
                              </tr>
                            ))
                        ) : (
                          <tr>
                            <td className="empty-cell" colSpan={3}>
                              No indicator trend data yet.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </section>

            {/* Public indicators */}
            <section className="card">
              <div className="mb-4">
                <h2 className="section-title mb-1">Public indicators</h2>
                <p className="text-sm text-[#6b6254]">
                  Track external signals like exchange rate, fuel price, and
                  official inflation.
                </p>
              </div>

              <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
                <form
                  className="rounded-2xl border border-[#eee6d6] bg-white p-4"
                  onSubmit={handleCreateIndicator}
                >
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Add indicator
                  </h3>

                  <label className="form-label">
                    Indicator
                    <select
                      className="form-input"
                      value={indicatorForm.name}
                      onChange={(event) =>
                        setIndicatorForm((current) => ({
                          ...current,
                          name: event.target.value,
                        }))
                      }
                    >
                      <option value="exchange_rate_usd_zmw">
                        USD/ZMW exchange rate
                      </option>
                      <option value="fuel_price_petrol">
                        Fuel price - petrol
                      </option>
                      <option value="fuel_price_diesel">
                        Fuel price - diesel
                      </option>
                      <option value="official_inflation">
                        Official inflation
                      </option>
                    </select>
                  </label>

                  <TextInput
                    label="Value"
                    type="number"
                    value={indicatorForm.value}
                    onChange={(value) =>
                      setIndicatorForm((current) => ({ ...current, value }))
                    }
                    placeholder="25.50"
                  />

                  <TextInput
                    label="Unit"
                    value={indicatorForm.unit}
                    onChange={(value) =>
                      setIndicatorForm((current) => ({
                        ...current,
                        unit: value,
                      }))
                    }
                    placeholder="ZMW"
                  />

                  <TextInput
                    label="Source"
                    value={indicatorForm.source}
                    onChange={(value) =>
                      setIndicatorForm((current) => ({
                        ...current,
                        source: value,
                      }))
                    }
                    placeholder="BOZ, ERB, ZamStats"
                  />

                  <label className="form-label">
                    Observed at
                    <input
                      className="form-input"
                      type="datetime-local"
                      value={indicatorForm.observed_at}
                      onChange={(event) =>
                        setIndicatorForm((current) => ({
                          ...current,
                          observed_at: event.target.value,
                        }))
                      }
                    />
                  </label>

                  <button className="primary-button" disabled={isSaving}>
                    Save indicator
                  </button>
                </form>

                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Recent indicators
                  </h3>

                  <div className="overflow-x-auto">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <TableHead>Name</TableHead>
                          <TableHead>Value</TableHead>
                          <TableHead>Source</TableHead>
                          <TableHead>Observed</TableHead>
                          <TableHead>Action</TableHead>
                        </tr>
                      </thead>
                      <tbody>
                        {indicators.length ? (
                          indicators.slice(0, 10).map((indicator) => (
                            <tr key={indicator.id}>
                              <TableCell>{indicator.name}</TableCell>
                              <TableCell>
                                {indicator.value} {indicator.unit ?? ""}
                              </TableCell>
                              <TableCell>{indicator.source ?? "—"}</TableCell>
                              <TableCell>
                                {dateFormatter.format(
                                  new Date(indicator.observed_at),
                                )}
                              </TableCell>
                              <TableCell>
                                <button
                                  className="danger-button"
                                  disabled={isSaving}
                                  onClick={() =>
                                    void handleDeleteIndicator(indicator)
                                  }
                                >
                                  Delete
                                </button>
                              </TableCell>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td className="empty-cell" colSpan={5}>
                              No public indicators yet.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </section>

            {/* Add item, price observation, and basket item forms */}
            <section className="mb-4 grid gap-4 lg:grid-cols-3">
              <form className="card" onSubmit={handleCreateItem}>
                <h2 className="section-title">Add item</h2>

                <TextInput
                  label="Name"
                  value={itemForm.name}
                  onChange={(value) =>
                    setItemForm((current) => ({ ...current, name: value }))
                  }
                  placeholder="Mealie meal"
                />

                <TextInput
                  label="Category"
                  value={itemForm.category}
                  onChange={(value) =>
                    setItemForm((current) => ({ ...current, category: value }))
                  }
                  placeholder="Food"
                />

                <TextInput
                  label="Brand"
                  value={itemForm.brand}
                  onChange={(value) =>
                    setItemForm((current) => ({ ...current, brand: value }))
                  }
                  placeholder="Optional"
                />

                <TextInput
                  label="Default unit"
                  value={itemForm.default_unit}
                  onChange={(value) =>
                    setItemForm((current) => ({
                      ...current,
                      default_unit: value,
                    }))
                  }
                  placeholder="kg"
                />

                <button className="primary-button" disabled={isSaving}>
                  Save item
                </button>
              </form>

              <form className="card" onSubmit={handleCreatePrice}>
                <h2 className="section-title">Add price observation</h2>

                <label className="form-label">
                  Item
                  <select
                    className="form-input"
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

                <TextInput
                  label="Shop"
                  value={priceForm.shop_name}
                  onChange={(value) =>
                    setPriceForm((current) => ({
                      ...current,
                      shop_name: value,
                    }))
                  }
                  placeholder="Shoprite"
                />

                <TextInput
                  label="Location"
                  value={priceForm.location}
                  onChange={(value) =>
                    setPriceForm((current) => ({ ...current, location: value }))
                  }
                  placeholder="Lusaka"
                />

                <div className="grid grid-cols-2 gap-3">
                  <TextInput
                    label="Price"
                    type="number"
                    value={priceForm.price}
                    onChange={(value) =>
                      setPriceForm((current) => ({ ...current, price: value }))
                    }
                    placeholder="250"
                  />

                  <TextInput
                    label="Quantity"
                    type="number"
                    value={priceForm.quantity}
                    onChange={(value) =>
                      setPriceForm((current) => ({
                        ...current,
                        quantity: value,
                      }))
                    }
                  />
                </div>

                <TextInput
                  label="Unit"
                  value={priceForm.unit}
                  onChange={(value) =>
                    setPriceForm((current) => ({ ...current, unit: value }))
                  }
                  placeholder="kg"
                />

                <button className="primary-button" disabled={isSaving}>
                  Save price
                </button>
              </form>

              <form className="card" onSubmit={handleAddBasketItem}>
                <h2 className="section-title">Add to basket</h2>

                <label className="form-label">
                  Item
                  <select
                    className="form-input"
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

                <TextInput
                  label="Quantity"
                  type="number"
                  value={basketForm.quantity}
                  onChange={(value) =>
                    setBasketForm((current) => ({
                      ...current,
                      quantity: value,
                    }))
                  }
                />

                <TextInput
                  label="Unit"
                  value={basketForm.unit}
                  onChange={(value) =>
                    setBasketForm((current) => ({ ...current, unit: value }))
                  }
                  placeholder="kg"
                />

                <button className="primary-button" disabled={isSaving}>
                  Add basket item
                </button>
              </form>
            </section>

            {/* Pending review queue */}
            <section className="card">
              <div className="mb-4">
                <h2 className="section-title mb-1">Pending review queue</h2>
                <p className="text-sm text-[#6b6254]">
                  Review raw collected prices before they become approved price
                  observations.
                </p>
              </div>

              <div className="grid gap-4 lg:grid-cols-[0.8fr_1.2fr]">
                <form
                  className="rounded-2xl border border-[#eee6d6] bg-white p-4"
                  onSubmit={handleCreateRawCollection}
                >
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Add raw price
                  </h3>

                  <TextInput
                    label="Item name"
                    value={rawCollectionForm.item_name}
                    onChange={(value) =>
                      setRawCollectionForm((current) => ({
                        ...current,
                        item_name: value,
                      }))
                    }
                    placeholder="Mealie Meal"
                  />

                  <TextInput
                    label="Category"
                    value={rawCollectionForm.category}
                    onChange={(value) =>
                      setRawCollectionForm((current) => ({
                        ...current,
                        category: value,
                      }))
                    }
                    placeholder="Food"
                  />

                  <TextInput
                    label="Brand"
                    value={rawCollectionForm.brand}
                    onChange={(value) =>
                      setRawCollectionForm((current) => ({
                        ...current,
                        brand: value,
                      }))
                    }
                    placeholder="Optional"
                  />

                  <TextInput
                    label="Shop"
                    value={rawCollectionForm.shop_name}
                    onChange={(value) =>
                      setRawCollectionForm((current) => ({
                        ...current,
                        shop_name: value,
                      }))
                    }
                    placeholder="Shoprite"
                  />

                  <TextInput
                    label="Location"
                    value={rawCollectionForm.location}
                    onChange={(value) =>
                      setRawCollectionForm((current) => ({
                        ...current,
                        location: value,
                      }))
                    }
                    placeholder="Lusaka"
                  />

                  <div className="grid grid-cols-2 gap-3">
                    <TextInput
                      label="Price"
                      type="number"
                      value={rawCollectionForm.price}
                      onChange={(value) =>
                        setRawCollectionForm((current) => ({
                          ...current,
                          price: value,
                        }))
                      }
                      placeholder="250"
                    />

                    <TextInput
                      label="Quantity"
                      type="number"
                      value={rawCollectionForm.quantity}
                      onChange={(value) =>
                        setRawCollectionForm((current) => ({
                          ...current,
                          quantity: value,
                        }))
                      }
                    />
                  </div>

                  <TextInput
                    label="Unit"
                    value={rawCollectionForm.unit}
                    onChange={(value) =>
                      setRawCollectionForm((current) => ({
                        ...current,
                        unit: value,
                      }))
                    }
                    placeholder="kg"
                  />

                  <TextInput
                    label="Source"
                    value={rawCollectionForm.source}
                    onChange={(value) =>
                      setRawCollectionForm((current) => ({
                        ...current,
                        source: value,
                      }))
                    }
                    placeholder="Manual, CSV, website"
                  />

                  <button className="primary-button" disabled={isSaving}>
                    Add to review queue
                  </button>
                </form>

                <div className="rounded-2xl border border-[#eee6d6] bg-white p-4">
                  <h3 className="mb-3 text-sm font-black uppercase tracking-wide text-[#6b6254]">
                    Pending prices
                  </h3>

                  <div className="overflow-x-auto">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <TableHead>Item</TableHead>
                          <TableHead>Shop</TableHead>
                          <TableHead>Price</TableHead>
                          <TableHead>Source</TableHead>
                          <TableHead>Action</TableHead>
                        </tr>
                      </thead>
                      <tbody>
                        {rawCollections.length ? (
                          rawCollections.map((raw) => (
                            <tr key={raw.id}>
                              <TableCell>{raw.item_name}</TableCell>
                              <TableCell>
                                {raw.shop_name}
                                {raw.location ? `, ${raw.location}` : ""}
                              </TableCell>
                              <TableCell>
                                {currencyFormatter.format(raw.price)} /{" "}
                                {raw.quantity} {raw.unit}
                              </TableCell>
                              <TableCell>{raw.source ?? "—"}</TableCell>
                              <TableCell>
                                <div className="flex gap-2">
                                  <button
                                    className="secondary-small-button"
                                    disabled={isSaving}
                                    onClick={() =>
                                      void handleApproveRawCollection(raw)
                                    }
                                  >
                                    Approve
                                  </button>

                                  <button
                                    className="danger-button"
                                    disabled={isSaving}
                                    onClick={() =>
                                      void handleRejectRawCollection(raw)
                                    }
                                  >
                                    Reject
                                  </button>
                                </div>
                              </TableCell>
                            </tr>
                          ))
                        ) : (
                          <tr>
                            <td className="empty-cell" colSpan={5}>
                              No pending raw prices.
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            </section>

            {/* Items */}
            <section className="card">
              <h2 className="section-title">Items</h2>

              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <TableHead>Name</TableHead>
                      <TableHead>Category</TableHead>
                      <TableHead>Brand</TableHead>
                      <TableHead>Default unit</TableHead>
                      <TableHead>Action</TableHead>
                    </tr>
                  </thead>
                  <tbody>
                    {items.length ? (
                      items.map((item) => (
                        <tr key={item.id}>
                          <TableCell>{item.name}</TableCell>
                          <TableCell>{item.category ?? "—"}</TableCell>
                          <TableCell>{item.brand ?? "—"}</TableCell>
                          <TableCell>{item.default_unit}</TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <button
                                className="secondary-small-button"
                                disabled={isSaving}
                                onClick={() => void handleEditItem(item)}
                              >
                                Edit
                              </button>

                              <button
                                className="danger-button"
                                disabled={isSaving}
                                onClick={() => void handleDeleteItem(item)}
                              >
                                Delete
                              </button>
                            </div>
                          </TableCell>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td className="empty-cell" colSpan={5}>
                          No items yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Basket total */}
            <section className="card">
              <div className="mb-4 flex flex-col justify-between gap-3 sm:flex-row sm:items-center">
                <h2 className="section-title mb-0">Basket total</h2>
                <strong className="text-2xl font-black text-[#8a6d1d]">
                  {currencyFormatter.format(basketTotal?.total ?? 0)}
                </strong>
              </div>

              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <TableHead>Item</TableHead>
                      <TableHead>Quantity</TableHead>
                      <TableHead>Latest price/unit</TableHead>
                      <TableHead>Shop</TableHead>
                      <TableHead>Line total</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead>Action</TableHead>
                    </tr>
                  </thead>
                  <tbody>
                    {basketTotal?.items.length ? (
                      basketTotal.items.map((line) => (
                        <tr key={line.basket_item_id}>
                          <TableCell>{line.item_name}</TableCell>
                          <TableCell>
                            {line.quantity} {line.unit}
                          </TableCell>
                          <TableCell>
                            {line.price_per_unit === null
                              ? "—"
                              : currencyFormatter.format(line.price_per_unit)}
                          </TableCell>
                          <TableCell>{line.shop_name ?? "—"}</TableCell>
                          <TableCell>
                            {line.line_total === null
                              ? "—"
                              : currencyFormatter.format(line.line_total)}
                          </TableCell>
                          <TableCell>{line.status}</TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <button
                                className="secondary-small-button"
                                disabled={isSaving}
                                onClick={() => void handleEditBasketLine(line)}
                              >
                                Edit
                              </button>

                              <button
                                className="danger-button"
                                disabled={isSaving}
                                onClick={() =>
                                  void handleRemoveBasketItem(
                                    line.basket_item_id,
                                  )
                                }
                              >
                                Remove
                              </button>
                            </div>
                          </TableCell>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td className="empty-cell" colSpan={7}>
                          No basket items yet.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </section>

            {/* Recent price observations */}
            <section className="card">
              <h2 className="section-title">Recent price observations</h2>

              <div className="overflow-x-auto">
                <table className="data-table">
                  <thead>
                    <tr>
                      <TableHead>Item</TableHead>
                      <TableHead>Shop</TableHead>
                      <TableHead>Location</TableHead>
                      <TableHead>Price</TableHead>
                      <TableHead>Price/unit</TableHead>
                      <TableHead>Observed</TableHead>
                      <TableHead>Action</TableHead>
                    </tr>
                  </thead>
                  <tbody>
                    {prices.length ? (
                      prices.slice(0, 10).map((price) => (
                        <tr key={price.id}>
                          <TableCell>
                            {itemNameById.get(price.item_id) ??
                              `Item #${price.item_id}`}
                          </TableCell>
                          <TableCell>{price.shop_name}</TableCell>
                          <TableCell>{price.location ?? "—"}</TableCell>
                          <TableCell>
                            {currencyFormatter.format(price.price)} /{" "}
                            {price.quantity} {price.unit}
                          </TableCell>
                          <TableCell>
                            {currencyFormatter.format(price.price_per_unit)}
                          </TableCell>
                          <TableCell>
                            {dateFormatter.format(new Date(price.observed_at))}
                          </TableCell>
                          <TableCell>
                            <div className="flex gap-2">
                              <button
                                className="secondary-small-button"
                                disabled={isSaving}
                                onClick={() =>
                                  void handleEditPriceObservation(price)
                                }
                              >
                                Edit
                              </button>

                              <button
                                className="danger-button"
                                disabled={isSaving}
                                onClick={() =>
                                  void handleDeletePriceObservation(price)
                                }
                              >
                                Delete
                              </button>
                            </div>
                          </TableCell>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td className="empty-cell" colSpan={7}>
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
      </div>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: string | number }) {
  return (
    <article className="rounded-3xl border border-[#e5dcc8] bg-[#fffdf8] p-5 shadow-[0_10px_30px_rgba(31,31,31,0.06)]">
      <p className="mb-2 text-sm text-[#6b6254]">{label}</p>
      <strong className="text-3xl font-black">{value}</strong>
    </article>
  );
}

function TextInput({
  label,
  value,
  onChange,
  placeholder,
  type = "text",
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  type?: "text" | "number";
}) {
  return (
    <label className="form-label">
      {label}
      <input
        className="form-input"
        type={type}
        min={type === "number" ? "0" : undefined}
        step={type === "number" ? "0.01" : undefined}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
      />
    </label>
  );
}

function TableHead({ children }: { children: React.ReactNode }) {
  return <th className="table-head">{children}</th>;
}

function TableCell({ children }: { children: React.ReactNode }) {
  return <td className="table-cell">{children}</td>;
}
