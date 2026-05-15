"use client";

import { useState } from "react";
import { extractFields } from "@/lib/api";
import { FieldDefinition, ExtractionResponse } from "@/lib/types";

interface FieldWithId extends FieldDefinition {
  _id: string;
}

interface Props {
  documentId: string;
  onExtracted: (result: ExtractionResponse) => void;
}

let fieldIdCounter = 0;

const emptyField = (): FieldWithId => ({
  _id: `field_${++fieldIdCounter}`,
  name: "",
  description: "",
  type: "string",
  required: false,
});

const FIELD_NAME_REGEX = /^[a-zA-Z][a-zA-Z0-9_]*$/;

export default function SchemaBuilder({ documentId, onExtracted }: Props) {
  const [fields, setFields] = useState<FieldWithId[]>([emptyField()]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const updateField = (index: number, updates: Partial<FieldWithId>) => {
    setFields((prev) =>
      prev.map((f, i) => (i === index ? { ...f, ...updates } : f))
    );
    setError("");
  };

  const addField = () => setFields((prev) => [...prev, emptyField()]);

  const removeField = (index: number) => {
    if (fields.length <= 1) return;
    setFields((prev) => prev.filter((_, i) => i !== index));
  };

  const validate = (): string | null => {
    const valid = fields.filter((f) => f.name.trim());
    if (valid.length === 0) return "Add at least one field with a name.";

    for (const f of valid) {
      if (!FIELD_NAME_REGEX.test(f.name)) {
        return `"${f.name}" is invalid. Use letters, numbers, and underscores (start with a letter).`;
      }
    }

    const names = valid.map((f) => f.name);
    const dupes = names.filter((n, i) => names.indexOf(n) !== i);
    if (dupes.length > 0) {
      return `Duplicate field name: "${dupes[0]}"`;
    }

    return null;
  };

  const handleExtract = async () => {
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }

    const valid = fields
      .filter((f) => f.name.trim())
      .map(({ _id, ...rest }) => rest);
    setLoading(true);
    setError("");

    try {
      const result = await extractFields(documentId, valid);
      onExtracted(result);
    } catch (err: any) {
      setError(err.message || "Extraction failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Define Fields to Extract</h2>

      {fields.map((field, i) => (
        <div key={field._id} className="field-row">
          <input
            placeholder="Field name (e.g. vendor_name)"
            value={field.name}
            onChange={(e) => updateField(i, { name: e.target.value })}
          />
          <input
            placeholder="Description for AI"
            value={field.description}
            onChange={(e) => updateField(i, { description: e.target.value })}
            maxLength={500}
          />
          <select
            value={field.type}
            onChange={(e) =>
              updateField(i, { type: e.target.value as FieldDefinition["type"] })
            }
          >
            <option value="string">String</option>
            <option value="number">Number</option>
            <option value="date">Date</option>
            <option value="boolean">Boolean</option>
          </select>
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={field.required}
              onChange={(e) => updateField(i, { required: e.target.checked })}
            />
            Required
          </label>
          <button className="btn-remove" onClick={() => removeField(i)} title="Remove field">
            ✕
          </button>
        </div>
      ))}

      <div className="actions">
        <button onClick={addField}>+ Add Field</button>
        <button className="btn-primary" onClick={handleExtract} disabled={loading}>
          {loading ? "Extracting..." : "Extract Data"}
        </button>
      </div>

      {error && <p className="error">{error}</p>}
    </div>
  );
}
