"use client";

import { useEffect, useState } from "react";
import { getExtractions } from "@/lib/api";
import { ExtractionListItem } from "@/lib/types";

interface Props {
  onSelect: (id: string) => void;
  refreshKey?: number;
}

export default function ReviewQueue({ onSelect, refreshKey }: Props) {
  const [items, setItems] = useState<ExtractionListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    setLoading(true);
    setError("");
    getExtractions()
      .then(setItems)
      .catch((err) => setError(err.message || "Failed to load extractions"))
      .finally(() => setLoading(false));
  }, [refreshKey]);

  const reviewItems = items.filter((i) => i.needs_review);

  return (
    <div className="card">
      <h2>Extractions</h2>

      {loading && <p className="hint">Loading...</p>}
      {error && <p className="error">{error}</p>}

      {!loading && reviewItems.length > 0 && (
        <>
          <h3>Needs Review ({reviewItems.length})</h3>
          <ul className="extraction-list">
            {reviewItems.map((item) => (
              <li key={item.id} onClick={() => onSelect(item.id)}>
                <span className="badge pending_review">review</span>
                <span className="ext-id">{item.id.slice(0, 8)}...</span>
                <span className="ext-date">
                  {new Date(item.created_at).toLocaleDateString()}
                </span>
              </li>
            ))}
          </ul>
        </>
      )}

      <h3>All ({items.length})</h3>
      {!loading && items.length === 0 && <p className="hint">No extractions yet.</p>}
      <ul className="extraction-list">
        {items.map((item) => (
          <li key={item.id} onClick={() => onSelect(item.id)}>
            <span className={`badge ${item.status}`}>{item.status.replace("_", " ")}</span>
            <span className="ext-id">{item.id.slice(0, 8)}...</span>
            <span className="ext-date">
              {new Date(item.created_at).toLocaleDateString()}
            </span>
          </li>
        ))}
      </ul>
    </div>
  );
}
