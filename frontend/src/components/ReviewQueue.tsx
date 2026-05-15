"use client";

import { useEffect, useState } from "react";
import { getExtractions } from "@/lib/api";
import { ExtractionListItem } from "@/lib/types";

const PAGE_SIZE = 50;

interface Props {
  onSelect: (id: string) => void;
  refreshKey?: number;
}

export default function ReviewQueue({ onSelect, refreshKey }: Props) {
  const [items, setItems] = useState<ExtractionListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [hasMore, setHasMore] = useState(false);

  const loadExtractions = (loadMore = false) => {
    setLoading(true);
    setError("");
    const skip = loadMore ? items.length : 0;
    getExtractions(skip, PAGE_SIZE)
      .then((data) => {
        setItems((prev) => (loadMore ? [...prev, ...data] : data));
        setHasMore(data.length === PAGE_SIZE);
      })
      .catch((err) => setError(err.message || "Failed to load extractions"))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadExtractions();
  }, [refreshKey]);

  const reviewItems = items.filter((i) => i.needs_review);

  return (
    <div className="card">
      <h2>Extractions</h2>

      {loading && items.length === 0 && <p className="hint">Loading...</p>}
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

      <h3>All ({items.length}{hasMore ? "+" : ""})</h3>
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

      {hasMore && (
        <button
          className="btn-small"
          onClick={() => loadExtractions(true)}
          disabled={loading}
          style={{ width: "100%", marginTop: "0.5rem" }}
        >
          {loading ? "Loading..." : "Load more"}
        </button>
      )}
    </div>
  );
}
