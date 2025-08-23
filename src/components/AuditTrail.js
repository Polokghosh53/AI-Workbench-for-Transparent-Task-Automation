import React from "react";

function AuditTrail({ results }) {
  const safeResults = Array.isArray(results) ? results : [];
  return (
    <div>
      <h3>Audit Trail</h3>
      {safeResults.length === 0 ? (
        <div>No results yet.</div>
      ) : (
        <ol>
          {safeResults.map((step, idx) => (
            <li key={idx}>{JSON.stringify(step)}</li>
          ))}
        </ol>
      )}
    </div>
  );
}
export default AuditTrail;


