import React, { useState } from "react";
import apiClient from "../api/client";

function FileUpload({ onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [dragActive, setDragActive] = useState(false);
  const [result, setResult] = useState(null);

  const supportedFormats = [
    { ext: ".xlsx", desc: "Excel Workbook" },
    { ext: ".xls", desc: "Excel 97-2003" },
    { ext: ".csv", desc: "CSV File" },
    { ext: ".docx", desc: "Word Document" },
    { ext: ".txt", desc: "Text File" },
    { ext: ".json", desc: "JSON Data" }
  ];

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const uploadFile = async () => {
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await apiClient.post("/upload-file/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });
      
      setResult(response.data);
      if (onUploadSuccess) {
        onUploadSuccess(response.data);
      }
    } catch (error) {
      console.error("Upload failed:", error);
      setResult({
        error: error.response?.data?.detail || "Upload failed",
        summary: "File upload error"
      });
    } finally {
      setUploading(false);
    }
  };

  const clearFile = () => {
    setFile(null);
    setResult(null);
  };

  return (
    <div className="panel">
      <div className="section-title">Data File Upload</div>
      
      {!file ? (
        <div
          className={`upload-zone ${dragActive ? "drag-active" : ""}`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => document.getElementById("file-input").click()}
        >
          <div className="upload-content">
            <div className="upload-icon">📁</div>
            <div>
              <strong>Drop files here or click to browse</strong>
            </div>
            <div className="subtle">
              Supports: {supportedFormats.map(f => f.ext).join(", ")}
            </div>
          </div>
          <input
            id="file-input"
            type="file"
            accept=".xlsx,.xls,.csv,.docx,.txt,.json"
            onChange={handleFileSelect}
            style={{ display: "none" }}
          />
        </div>
      ) : (
        <div className="file-selected">
          <div className="row">
            <div>
              <strong>{file.name}</strong>
              <div className="meta">{(file.size / 1024).toFixed(1)} KB</div>
            </div>
            <div className="row">
              <button className="btn" onClick={uploadFile} disabled={uploading}>
                {uploading ? "Processing..." : "Process File"}
              </button>
              <button className="btn-secondary" onClick={clearFile}>
                Clear
              </button>
            </div>
          </div>
        </div>
      )}

      {result && (
        <div className="upload-results">
          <div className="section-title">Processing Results</div>
          
          {result.error ? (
            <div className="error-message">
              <strong>Error:</strong> {result.error}
            </div>
          ) : (
            <div>
              <div className="result-summary">
                <strong>Summary:</strong> {result.summary}
              </div>
              
              {result.statistics && (
                <div className="stats-grid">
                  <div className="stat-item">
                    <span className="stat-label">Rows:</span>
                    <span className="stat-value">{result.statistics.total_rows?.toLocaleString()}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Numeric Cols:</span>
                    <span className="stat-value">{result.statistics.numeric_columns}</span>
                  </div>
                  <div className="stat-item">
                    <span className="stat-label">Text Cols:</span>
                    <span className="stat-value">{result.statistics.categorical_columns}</span>
                  </div>
                </div>
              )}

              {result.insights && result.insights.length > 0 && (
                <div>
                  <div className="subsection-title">Key Insights</div>
                  <ul className="insights-list">
                    {result.insights.map((insight, idx) => (
                      <li key={idx} className="insight-item">{insight}</li>
                    ))}
                  </ul>
                </div>
              )}

              {result.visualizations && result.visualizations.length > 0 && (
                <div>
                  <div className="subsection-title">Visualizations</div>
                  <div className="visualizations-grid">
                    {result.visualizations.map((viz, idx) => (
                      <div key={idx} className="visualization-item">
                        <div className="viz-title">{viz.title}</div>
                        <img 
                          src={`data:image/png;base64,${viz.image}`} 
                          alt={viz.title}
                          className="viz-image"
                        />
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default FileUpload;
