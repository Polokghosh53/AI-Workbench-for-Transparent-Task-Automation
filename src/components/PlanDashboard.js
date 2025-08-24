import React, { useEffect, useMemo, useState } from "react";
import apiClient from "../api/client";
import AuditTrail from "./AuditTrail";
import PlanDetails from "./PlanDetails";
import FileUpload from "./FileUpload";
import PlanPreview from "./PlanPreview";
import PlanHistory from "./PlanHistory";

function PlanDashboard() {
  const [plans, setPlans] = useState([]);
  const [input, setInput] = useState("");
  const [email, setEmail] = useState("");
  const [results, setResults] = useState(null);
  const [selectedPlanId, setSelectedPlanId] = useState("");
  const [isRunning, setIsRunning] = useState(false);
  const [uploadedData, setUploadedData] = useState(null);
  const [generatedPlan, setGeneratedPlan] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

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
      const requestData = { 
        query: input, 
        to: email 
      };
      
      // Include uploaded file path if available
      if (uploadedData && uploadedData.upload_id) {
        requestData.file_path = `uploads/${uploadedData.upload_id}`;
      }
      
      const res = await apiClient.post("/run-plan/", requestData);
      setResults(res.data?.results || []);
      await fetchPlans();
      setSelectedPlanId(res.data?.plan_id || "");
    } catch (error) {
      console.error("Plan execution failed:", error);
      setResults([{ error: error.response?.data?.detail || "Plan execution failed" }]);
    } finally {
      setIsRunning(false);
    }
  };

  const handleUploadSuccess = (data) => {
    setUploadedData(data);
    // Auto-populate task description based on uploaded data
    if (data.summary && !input) {
      setInput(`Analyze and summarize the uploaded ${data.source_type || 'data'} file: ${data.original_filename}`);
    }
  };

  return (
    <div className="grid">
      <FileUpload onUploadSuccess={handleUploadSuccess} />
      
      <section className="panel">
        <div className="section-title">🚀 Portia AI Enhanced Task Creation</div>
        <div className="row">
          <input
            className="input"
            placeholder="Describe your task (e.g., 'Analyze sales data and email summary')"
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
          <button className="btn" onClick={runPlan} disabled={isRunning || !email || !generatedPlan}>
            {isRunning ? "🔄 Executing Plan..." : "▶️ Execute Plan"}
          </button>
        </div>
        
        {uploadedData && (
          <div className="upload-summary">
            <div className="tag">📊 Data Ready</div>
            <span className="subtle">
              {uploadedData.original_filename} ({uploadedData.statistics?.total_rows || 'N/A'} rows)
            </span>
          </div>
        )}
        
        <div className="row" style={{ marginTop: '12px' }}>
          <button 
            className="btn-secondary" 
            onClick={() => setShowHistory(!showHistory)}
          >
            {showHistory ? "Hide History" : "📚 View Plan History"}
          </button>
          {generatedPlan && (
            <div className="tag">✅ Plan Generated - Ready to Execute</div>
          )}
        </div>
      </section>

      {/* Portia's Structured Plan Preview */}
      <PlanPreview 
        query={input} 
        uploadedData={uploadedData}
        onPlanGenerated={setGeneratedPlan}
      />

      <section className="panel split">
        <div>
          <div className="section-title">🎯 Execution Results</div>
          {results && results.length > 0 ? (
            <AuditTrail results={results} />
          ) : (
            <div className="subtle">Execute a plan to see detailed results here.</div>
          )}
        </div>
        <div>
          <div className="section-title">📋 Legacy Plan Preview</div>
          <ol className="card-list">
            {planPreview.map((step, idx) => (
              <li key={idx}>{step.task} <span className="meta">({step.tool_id})</span></li>
            ))}
          </ol>
        </div>
      </section>

      {/* Portia's Plan History with Rollback */}
      {showHistory && (
        <PlanHistory onPlanSelect={setSelectedPlanId} />
      )}

      {selectedPlanId && (
        <section className="panel">
          <div className="section-title">🔍 Plan Details</div>
          <PlanDetails planId={selectedPlanId} />
        </section>
      )}
    </div>
  );
}

export default PlanDashboard;


