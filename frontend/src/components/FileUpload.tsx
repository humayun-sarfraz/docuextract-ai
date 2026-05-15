"use client";

import { useState, useRef } from "react";
import { uploadDocument } from "@/lib/api";
import { DocumentResponse } from "@/lib/types";

interface Props {
  onUploadSuccess: (doc: DocumentResponse) => void;
}

export default function FileUpload({ onUploadSuccess }: Props) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [warning, setWarning] = useState("");
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    setError("");
    setWarning("");

    try {
      const doc: DocumentResponse = await uploadDocument(file);
      if (doc.duplicate_warning) {
        setWarning(doc.duplicate_warning);
      }
      setFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
      onUploadSuccess(doc);
    } catch (err: any) {
      setError(err.message || "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) {
      setFile(dropped);
      setError("");
      setWarning("");
    }
  };

  return (
    <div className="card">
      <h2>Upload Document</h2>
      <p className="hint">Supported formats: PDF, TXT, DOCX (max 10MB)</p>

      <div
        className={`drop-zone ${dragOver ? "drop-zone-active" : ""}`}
        onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".pdf,.txt,.docx"
          style={{ display: "none" }}
          onChange={(e) => {
            setFile(e.target.files?.[0] || null);
            setError("");
            setWarning("");
          }}
        />
        {file ? (
          <p className="drop-zone-text">{file.name} ({(file.size / 1024).toFixed(1)} KB)</p>
        ) : (
          <p className="drop-zone-text">Click or drag a file here</p>
        )}
      </div>

      <button onClick={handleUpload} disabled={!file || loading} className="btn-primary" style={{ marginTop: "0.75rem", width: "100%" }}>
        {loading ? "Uploading..." : "Upload"}
      </button>

      {error && <p className="error">{error}</p>}
      {warning && <p className="warning">{warning}</p>}
    </div>
  );
}
