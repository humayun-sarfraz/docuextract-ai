import { FieldDefinition, DocumentResponse, ExtractionResponse, ExtractionListItem } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function request(path: string, options?: RequestInit): Promise<Response> {
  const res = await fetch(`${API_BASE}${path}`, options);
  if (!res.ok) {
    let message = res.statusText;
    try {
      const body = await res.json();
      message = body.detail || message;
    } catch {
      // Response wasn't JSON
    }
    throw new ApiError(message, res.status);
  }
  return res;
}

export async function uploadDocument(file: File): Promise<DocumentResponse> {
  const form = new FormData();
  form.append("file", file);
  const res = await request("/api/documents/upload", { method: "POST", body: form });
  return res.json();
}

export async function getDocuments(): Promise<DocumentResponse[]> {
  const res = await request("/api/documents");
  return res.json();
}

export async function getDocument(id: string): Promise<DocumentResponse> {
  const res = await request(`/api/documents/${id}`);
  return res.json();
}

export async function extractFields(
  documentId: string,
  fields: FieldDefinition[]
): Promise<ExtractionResponse> {
  const res = await request("/api/extraction/extract", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ document_id: documentId, fields }),
  });
  return res.json();
}

export async function getExtractions(skip = 0, limit = 50): Promise<ExtractionListItem[]> {
  const res = await request(`/api/extractions?skip=${skip}&limit=${limit}`);
  return res.json();
}

export async function getExtraction(id: string): Promise<ExtractionResponse> {
  const res = await request(`/api/extractions/${id}`);
  return res.json();
}

export async function updateExtraction(
  id: string,
  extractedData: Record<string, any>
): Promise<ExtractionResponse> {
  const res = await request(`/api/extractions/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ extracted_data: extractedData }),
  });
  return res.json();
}

export async function approveExtraction(id: string): Promise<ExtractionResponse> {
  const res = await request(`/api/extractions/${id}/approve`, { method: "POST" });
  return res.json();
}

export async function exportJson(id: string): Promise<Record<string, any>> {
  const res = await request(`/api/extractions/${id}/export/json`);
  return res.json();
}

export async function exportCsv(id: string): Promise<string> {
  const res = await request(`/api/extractions/${id}/export/csv`);
  return res.text();
}
