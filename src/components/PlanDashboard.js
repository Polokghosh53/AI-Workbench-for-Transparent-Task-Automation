import React, { useEffect, useMemo, useState } from "react";
import apiClient from "../api/client";
import AuditTrail from "./AuditTrail";
import PlanDetails from "./PlanDetails";

function PlanDashboard() {
  const [plans, setPlans] = useState([]);
  const [input, setInput] = useState("");
  const [email, setEmail] = useState("");
  const [results, setResults] = useState(null);
  const [selectedPlanId, setSelectedPlanId] = useState("");
  const [isRunning, setIsRunning] = useState(false);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    const res = await apiClient.get("/plans/");
    setPlans(res.data || []);
  };

  const planPreview = useMemo(() => {
    if (!email) {
      return [
        { task: "Fetch and summarize sales data", tool_id: "fetch_and_summarize_data", output: "data_summary" },
        { task: "Send sales summary email", tool_id: "send_email", output: "email_status", inputs: [{ name: "to", value: "<missing email>" }, { name: "subject", value: "Sales Summary" }, { name: "body", value: "${data_summary}" }] },
      ];
    }
    return [
      { task: "Fetch and summarize sales data", tool_id: "fetch_and_summarize_data", output: "data_summary" },
      { task: "Send sales summary email", tool_id: "send_email", output: "email_status", inputs: [{ name: "to", value: email }, { name: "subject", value: "Sales Summary" }, { name: "body", value: "${data_summary}" }] },
    ];
  }, [email]);

  const runPlan = async () => {
    setIsRunning(true);
    try {
      const res = await apiClient.post(
        "/run-plan/",
        { query: input, to: email }
      );
      setResults(res.data?.results || []);
      await fetchPlans();
      setSelectedPlanId(res.data?.plan_id || "");
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="grid">
      <section className="panel">
        <div className="section-title">Create Plan</div>
        <div className="row">
          <input
            className="input"
            placeholder="Describe your task"
            value={input}
            onChange={(e) => setInput(e.target.value)}
          />
          <input
            className="input"
            placeholder="Recipient Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            type="email"
          />
          <button className="btn" onClick={runPlan} disabled={isRunning || !email}>
            {isRunning ? "Running..." : "Run"}
          </button>
        </div>
      </section>

      <section className="panel split">
        <div>
          <div className="section-title">Plan Preview</div>
          <ol className="card-list">
            {planPreview.map((step, idx) => (
              <li key={idx}>{step.task} <span className="meta">({step.tool_id})</span></li>
            ))}
          </ol>
        </div>
        <div>
          <div className="section-title">Latest Run</div>
          {results && results.length > 0 ? (
            <AuditTrail results={results} />
          ) : (
            <div className="subtle">No run yet.</div>
          )}
        </div>
      </section>

      <section className="panel">
        <div className="section-title">Past Plans</div>
        <ul className="card-list">
          {plans.map((plan) => (
            <li key={plan.plan?.id} className="row">
              <span>{plan.plan?.id}</span>
              <button className="btn" onClick={() => setSelectedPlanId(plan.plan?.id)} style={{ marginLeft: 8 }}>
                View
              </button>
            </li>
          ))}
        </ul>
      </section>

      {selectedPlanId && (
        <section className="panel">
          <div className="section-title">Plan Details</div>
          <PlanDetails planId={selectedPlanId} />
        </section>
      )}
    </div>
  );
}

export default PlanDashboard;


