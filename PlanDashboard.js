import React, { useState, useEffect } from "react";
import axios from "axios";
import AuditTrail from "./AuditTrail";

function PlanDashboard() {
  const [plans, setPlans] = useState([]);
  const [input, setInput] = useState("");
  const [email, setEmail] = useState("");
  const [results, setResults] = useState(null);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    const res = await axios.get("/plans", {
      headers: { Authorization: "Bearer demo" },
    });
    setPlans(res.data);
  };

  const runPlan = async () => {
    const res = await axios.post(
      "/run-plan/",
      { query: input, to: email },
      { headers: { Authorization: "Bearer demo" } }
    );
    setResults(res.data.results);
    await fetchPlans();
  };

  return (
    <div>
      <h2>Create Plan</h2>
      <input
        placeholder="Describe your task"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <input
        placeholder="Recipient Email"
        value={email}
        onChange={(e) => setEmail(e.target.value)}
      />
      <button onClick={runPlan}>Run</button>

      {results && <AuditTrail results={results} />}

      <h2>Past Plans</h2>
      <ul>
        {plans.map((plan) => (
          <li key={plan.plan.id}>
            {plan.plan.id}
            <AuditTrail results={plan.results} />
          </li>
        ))}
      </ul>
    </div>
  );
}

export default PlanDashboard;
