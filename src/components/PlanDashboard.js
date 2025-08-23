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
    <div>
      <h2>Create Plan</h2>
      <div>
        <input
          placeholder="Describe your task"
          value={input}
          onChange={(e) => setInput(e.target.value)}
        />
      </div>
      <div>
        <input
          placeholder="Recipient Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </div>
      <div>
        <h3>Plan Preview</h3>
        <ol>
          {planPreview.map((step, idx) => (
            <li key={idx}>
              {step.task} ({step.tool_id})
            </li>
          ))}
        </ol>
      </div>
      <button onClick={runPlan} disabled={isRunning || !email}>
        {isRunning ? "Running..." : "Run"}
      </button>

      {results && results.length > 0 && (
        <div>
          <h2>Latest Run</h2>
          <AuditTrail results={results} />
        </div>
      )}

      <h2>Past Plans</h2>
      <ul>
        {plans.map((plan) => (
          <li key={plan.plan?.id}>
            {plan.plan?.id}
            <button onClick={() => setSelectedPlanId(plan.plan?.id)} style={{ marginLeft: 8 }}>
              View
            </button>
          </li>
        ))}
      </ul>

      {selectedPlanId && (
        <div>
          <h2>Plan Details</h2>
          <PlanDetails planId={selectedPlanId} />
        </div>
      )}
    </div>
  );
}

export default PlanDashboard;


