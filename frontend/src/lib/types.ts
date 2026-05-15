export interface FieldDefinition {
  name: string;
  description: string;
  type: "string" | "number" | "date" | "boolean";
  required: boolean;
}

export interface FieldResult {
  value: string | number | boolean | null;
  confidence: number;
  evidence: string | null;
}

export interface DocumentResponse {
  id: string;
  filename: string;
  file_type: string;
  file_hash: string | null;
  extracted_text: string | null;
  status: string;
  created_at: string;
  duplicate_warning: string | null;
}

export interface ExtractionResponse {
  id: string;
  document_id: string;
  extracted_data: Record<string, FieldResult>;
  missing_required_fields: string[];
  needs_review: boolean;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface ExtractionListItem {
  id: string;
  document_id: string;
  needs_review: boolean;
  status: string;
  created_at: string;
}
