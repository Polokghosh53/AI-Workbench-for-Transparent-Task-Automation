import React from "react";

function AuditTrail({ results }) {
  const safeResults = Array.isArray(results) ? results : [];
  return (
    <div>
      <div className="section-title">Audit Trail</div>
      {safeResults.length === 0 ? (
        <div className="subtle">No results yet.</div>
      ) : (
        <ol className="card-list">
          {safeResults.map((step, idx) => (
            <li key={idx}><code className="subtle">{JSON.stringify(step)}</code></li>
          ))}
        </ol>
      )}
    </div>
  );
}
export default AuditTrail;


