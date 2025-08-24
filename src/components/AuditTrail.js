import React from "react";

function AuditTrail({ results }) {
  const safeResults = Array.isArray(results) ? results : [];
  
  const formatStepData = (step) => {
    if (!step || !step.data) return "No data";
    
    const data = step.data;
    
    // If it's a data summary with statistics, show key metrics
    if (data.summary && data.statistics) {
      return (
        <div className="step-summary">
          <div className="step-title">📊 Data Analysis Complete</div>
          <div className="step-details">
            <div><strong>Summary:</strong> {data.summary}</div>
            {data.statistics && (
              <div className="stats-mini">
                <span className="stat-mini">📋 {data.statistics.total_rows} rows</span>
                <span className="stat-mini">🔢 {data.statistics.numeric_columns} numeric cols</span>
                <span className="stat-mini">📝 {data.statistics.categorical_columns} text cols</span>
              </div>
            )}
            {data.insights && data.insights.length > 0 && (
              <div className="insights-mini">
                <strong>Key Insights:</strong>
                <ul>
                  {data.insights.slice(0, 3).map((insight, i) => (
                    <li key={i}>{insight}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      );
    }
    
    // If it's an email status, show formatted result
    if (data.status) {
      return (
        <div className="step-summary">
          <div className="step-title">📧 Email Status</div>
          <div className="step-details">
            <div><strong>Status:</strong> <span className={`status-${data.status}`}>{data.status}</span></div>
            {data.to && <div><strong>To:</strong> {data.to}</div>}
            {data.from && <div><strong>From:</strong> {data.from}</div>}
            {data.error && <div className="error-text"><strong>Error:</strong> {data.error}</div>}
          </div>
        </div>
      );
    }
    
    // Fallback for other data types - truncate long JSON
    const jsonStr = JSON.stringify(data, null, 2);
    if (jsonStr.length > 200) {
      return (
        <div className="step-summary">
          <div className="step-title">📋 Step Result</div>
          <div className="step-details">
            <details>
              <summary>View raw data ({jsonStr.length} chars)</summary>
              <pre className="json-preview">{jsonStr}</pre>
            </details>
          </div>
        </div>
      );
    }
    
    return <pre className="json-preview">{jsonStr}</pre>;
  };

  return (
    <div>
      <div className="section-title">Audit Trail</div>
      {safeResults.length === 0 ? (
        <div className="subtle">No results yet.</div>
      ) : (
        <ol className="audit-list">
          {safeResults.map((step, idx) => (
            <li key={idx} className="audit-item">
              <div className="audit-step">
                <div className="step-number">{idx + 1}</div>
                <div className="step-content">
                  {formatStepData(step)}
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
export default AuditTrail;


