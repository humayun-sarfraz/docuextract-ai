"use client";

import { useState } from "react";
import FileUpload from "@/components/FileUpload";
import SchemaBuilder from "@/components/SchemaBuilder";
import ExtractionResults from "@/components/ExtractionResults";
import ReviewQueue from "@/components/ReviewQueue";
import { DocumentResponse, ExtractionResponse } from "@/lib/types";
import { getExtraction } from "@/lib/api";

type Step = "upload" | "schema" | "results";

export default function Home() {
  const [step, setStep] = useState<Step>("upload");
  const [document, setDocument] = useState<DocumentResponse | null>(null);
  const [extraction, setExtraction] = useState<ExtractionResponse | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleUploadSuccess = (doc: DocumentResponse) => {
    setDocument(doc);
    setStep("schema");
  };

  const handleExtracted = (result: ExtractionResponse) => {
    setExtraction(result);
    setStep("results");
    setRefreshKey((k) => k + 1);
  };

  const handleSelectExtraction = async (id: string) => {
    try {
      const result = await getExtraction(id);
      setExtraction(result);
      setStep("results");
    } catch (err) {
      console.error(err);
    }
  };

  const handleReset = () => {
    if (step !== "upload" && !window.confirm("Start over? Any unsaved changes will be lost.")) {
      return;
    }
    setStep("upload");
    setDocument(null);
    setExtraction(null);
  };

  return (
    <div className="container">
      <header>
        <h1>DocuExtract AI</h1>
        <p>Simple AI Document Data Extractor</p>
      </header>

      <div className="steps">
        <span className={`step ${step === "upload" ? "active" : document ? "done" : ""}`}>
          1. Upload
        </span>
        <span className={`step ${step === "schema" ? "active" : extraction ? "done" : ""}`}>
          2. Define Fields
        </span>
        <span className={`step ${step === "results" ? "active" : ""}`}>
          3. Results
        </span>
        {step !== "upload" && (
          <button className="btn-small" onClick={handleReset} style={{ marginLeft: "1rem" }}>
            Start Over
          </button>
        )}
      </div>

      <div className="layout">
        <aside>
          <ReviewQueue onSelect={handleSelectExtraction} refreshKey={refreshKey} />
        </aside>

        <main>
          {step === "upload" && (
            <FileUpload onUploadSuccess={handleUploadSuccess} />
          )}

          {step === "schema" && document && (
            <div>
              <div className="card">
                <h2>Document Ready</h2>
                <p><strong>File:</strong> {document.filename}</p>
                <p><strong>Type:</strong> {document.file_type}</p>
                <p><strong>Status:</strong> {document.status}</p>
                {document.extracted_text && (
                  <details style={{ marginTop: "0.5rem" }}>
                    <summary className="hint" style={{ cursor: "pointer" }}>
                      Preview extracted text ({document.extracted_text.length} chars)
                    </summary>
                    <pre className="text-preview">{document.extracted_text.slice(0, 2000)}</pre>
                  </details>
                )}
              </div>
              <SchemaBuilder documentId={document.id} onExtracted={handleExtracted} />
            </div>
          )}

          {step === "results" && extraction && (
            <ExtractionResults
              extraction={extraction}
              onUpdate={(updated) => {
                setExtraction(updated);
                setRefreshKey((k) => k + 1);
              }}
            />
          )}
        </main>
      </div>
    </div>
  );
}
