import React, { useEffect, useState } from "react";
import apiClient from "../api/client";
import AuditTrail from "./AuditTrail";

function PlanDetails({ planId }) {
  const [plan, setPlan] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (!planId) return;
    const load = async () => {
      setIsLoading(true);
      try {
        const res = await apiClient.get(`/plan/${planId}`);
        setPlan(res.data || null);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, [planId]);

  if (!planId) return null;
  if (isLoading) return <div className="subtle">Loading plan...</div>;
  if (!plan) return <div className="subtle">Plan not found.</div>;

  const steps = plan.plan?.steps || [];
  const results = plan.results || [];

  return (
    <div>
      <div className="row" style={{justifyContent: "space-between"}}>
        <div><strong>Plan ID:</strong> {plan.plan?.id}</div>
        <span className="tag">{steps.length} steps</span>
      </div>
      <div className="section-title">Steps</div>
      <ol className="card-list">
        {steps.map((step, idx) => (
          <li key={idx}>{step?.task || step?.tool_id || "Step"}</li>
        ))}
      </ol>
      <div style={{ marginTop: 16 }}>
        <AuditTrail results={results} />
      </div>
    </div>
  );
}

export default PlanDetails;


