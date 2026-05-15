import { apiRequest } from "./client";
import type {
  ApproveRawCollectionResult,
  BulkApproveRawCollectionsResult,
  BulkRejectRawCollectionsResult,
  CreateRawCollectionPayload,
  RawCollection,
  RawCollectionStatus,
  UpdateRawCollectionPayload,
} from "../types/rawCollection";

export function listRawCollections(
  status?: RawCollectionStatus,
): Promise<RawCollection[]> {
  const query = status ? `?status=${status}` : "";
  return apiRequest<RawCollection[]>(`/raw-collections${query}`);
}

export function createRawCollection(
  payload: CreateRawCollectionPayload,
): Promise<RawCollection> {
  return apiRequest<RawCollection>("/raw-collections", {
    method: "POST",
    body: payload,
  });
}

export function updateRawCollection(
  id: number,
  payload: UpdateRawCollectionPayload,
): Promise<RawCollection> {
  return apiRequest<RawCollection>(`/raw-collections/${id}`, {
    method: "PATCH",
    body: payload,
  });
}

export function approveRawCollection(
  id: number,
): Promise<ApproveRawCollectionResult> {
  return apiRequest<ApproveRawCollectionResult>(
    `/raw-collections/${id}/approve`,
    {
      method: "POST",
    },
  );
}

export function rejectRawCollection(id: number): Promise<RawCollection> {
  return apiRequest<RawCollection>(`/raw-collections/${id}/reject`, {
    method: "POST",
  });
}

export function deleteRawCollection(id: number): Promise<void> {
  return apiRequest<void>(`/raw-collections/${id}`, {
    method: "DELETE",
  });
}

export function bulkApproveRawCollections(): Promise<BulkApproveRawCollectionsResult> {
  return apiRequest<BulkApproveRawCollectionsResult>(
    "/raw-collections/bulk/approve",
    {
      method: "POST",
    },
  );
}

export function bulkRejectRawCollections(): Promise<BulkRejectRawCollectionsResult> {
  return apiRequest<BulkRejectRawCollectionsResult>(
    "/raw-collections/bulk/reject",
    {
      method: "POST",
    },
  );
}
