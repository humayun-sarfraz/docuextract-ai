"use client";

import { useState } from "react";
import { approveExtraction, updateExtraction, exportCsv, exportJson } from "@/lib/api";
import { ExtractionResponse, FieldResult } from "@/lib/types";

interface Props {
  extraction: ExtractionResponse;
  onUpdate: (updated: ExtractionResponse) => void;
}

export default function ExtractionResults({ extraction, onUpdate }: Props) {
  const [editingField, setEditingField] = useState<string | null>(null);
  const [editValue, setEditValue] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState<string | null>(null);

  const confidenceColor = (c: number) => {
    if (c >= 0.85) return "#22c55e";
    if (c >= 0.75) return "#eab308";
    return "#ef4444";
  };

  const handleSaveEdit = async (fieldName: string) => {
    const newData: Record<string, FieldResult> = { ...extraction.extracted_data };
    newData[fieldName] = {
      ...newData[fieldName],
      value: editValue,
      confidence: 1.0,
      evidence: "Manually edited",
    };
    setLoading(true);
    setError("");
    try {
      const updated = await updateExtraction(extraction.id, newData);
      onUpdate(updated);
    } catch (err: any) {
      setError(err.message || "Update failed");
    } finally {
      setLoading(false);
      setEditingField(null);
    }
  };

  const handleApprove = async () => {
    setLoading(true);
    setError("");
    try {
      const updated = await approveExtraction(extraction.id);
      onUpdate(updated);
    } catch (err: any) {
      setError(err.message || "Approval failed");
    } finally {
      setLoading(false);
    }
  };

  const handleExportJson = async () => {
    setError("");
    try {
      const data = await exportJson(extraction.id);
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `extraction_${extraction.id.slice(0, 8)}.json`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.message || "JSON export failed");
    }
  };

  const handleExportCsv = async () => {
    setError("");
    try {
      const csv = await exportCsv(extraction.id);
      const blob = new Blob([csv], { type: "text/csv" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `extraction_${extraction.id.slice(0, 8)}.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.message || "CSV export failed");
    }
  };

  const handleCopy = (fieldName: string, value: string) => {
    navigator.clipboard.writeText(value).then(() => {
      setCopied(fieldName);
      setTimeout(() => setCopied(null), 1500);
    });
  };

  return (
    <div className="card">
      <div className="results-header">
        <h2>Extraction Results</h2>
        <span className={`badge ${extraction.status}`}>{extraction.status.replace("_", " ")}</span>
      </div>

      {extraction.needs_review && (
        <p className="warning">This extraction needs review — check highlighted fields below.</p>
      )}

      {extraction.missing_required_fields.length > 0 && (
        <p className="error">
          Missing required fields: {extraction.missing_required_fields.join(", ")}
        </p>
      )}

      <div className="table-wrapper">
        <table>
          <thead>
            <tr>
              <th>Field</th>
              <th>Value</th>
              <th>Confidence</th>
              <th>Evidence</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(extraction.extracted_data).map(([name, field]) => (
              <tr
                key={name}
                className={
                  extraction.missing_required_fields.includes(name)
                    ? "row-missing"
                    : field.confidence < 0.75
                      ? "row-low-confidence"
                      : ""
                }
              >
                <td className="field-name">{name}</td>
                <td>
                  {editingField === name ? (
                    <div className="edit-inline">
                      <input
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onKeyDown={(e) => {
                          if (e.key === "Enter") handleSaveEdit(name);
                          if (e.key === "Escape") setEditingField(null);
                        }}
                        autoFocus
                      />
                      <button onClick={() => handleSaveEdit(name)} disabled={loading}>
                        Save
                      </button>
                      <button onClick={() => setEditingField(null)}>Cancel</button>
                    </div>
                  ) : (
                    <span>{field.value !== null ? String(field.value) : "—"}</span>
                  )}
                </td>
                <td>
                  <span
                    className="confidence"
                    style={{ color: confidenceColor(field.confidence) }}
                  >
                    {(field.confidence * 100).toFixed(0)}%
                  </span>
                </td>
                <td className="evidence">{field.evidence || "—"}</td>
                <td className="action-cell">
                  <button
                    className="btn-small"
                    onClick={() => {
                      setEditingField(name);
                      setEditValue(String(field.value ?? ""));
                    }}
                  >
                    Edit
                  </button>
                  {field.value !== null && (
                    <button
                      className="btn-small"
                      onClick={() => handleCopy(name, String(field.value))}
                    >
                      {copied === name ? "Copied!" : "Copy"}
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {error && <p className="error">{error}</p>}

      <div className="actions">
        {extraction.status !== "approved" && extraction.status !== "exported" && (
          <button className="btn-primary" onClick={handleApprove} disabled={loading}>
            {loading ? "Approving..." : "Approve"}
          </button>
        )}
        <button onClick={handleExportJson}>Export JSON</button>
        <button onClick={handleExportCsv}>Export CSV</button>
      </div>
    </div>
  );
}
