import React from "react";

function AuditTrail({ results }) {
  return (
    <div>
      <h3>Audit Trail</h3>
      <ol>
        {results.map((step, idx) => (
          <li key={idx}>{JSON.stringify(step)}</li>
        ))}
      </ol>
    </div>
  );
}
export default AuditTrail;
