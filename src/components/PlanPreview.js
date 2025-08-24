import React, { useState, useEffect } from "react";
import apiClient from "../api/client";

function PlanPreview({ query, uploadedData, onPlanGenerated }) {
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (query || uploadedData) {
      generatePlan();
    }
  }, [query, uploadedData]);

  const generatePlan = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const requestData = { query };
      if (uploadedData && uploadedData.upload_id) {
        requestData.file_path = `uploads/${uploadedData.upload_id}`;
      }
      
      const response = await apiClient.post("/generate-plan/", requestData);
      setPlan(response.data);
      if (onPlanGenerated) {
        onPlanGenerated(response.data);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to generate plan");
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="plan-preview loading">
        <div className="section-title">🔄 Generating Structured Plan...</div>
        <div className="subtle">Using Portia AI's planning system</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="plan-preview error">
        <div className="section-title">❌ Plan Generation Failed</div>
        <div className="error-message">{error}</div>
        <button className="btn-secondary" onClick={generatePlan}>
          Retry
        </button>
      </div>
    );
  }

  if (!plan) {
    return (
      <div className="plan-preview empty">
        <div className="section-title">📋 Plan Preview</div>
        <div className="subtle">Enter a task description to generate a structured plan</div>
      </div>
    );
  }

  return (
    <div className="plan-preview">
      <div className="plan-header">
        <div className="section-title">📋 Structured Plan Preview</div>
        <div className="plan-meta">
          <span className="tag">🤖 Portia Enhanced</span>
          <span className="plan-duration">{plan.estimated_total_duration}</span>
        </div>
      </div>
      
      <div className="plan-query">
        <strong>Query:</strong> {plan.query}
      </div>

      <div className="plan-steps">
        {plan.steps.map((step, index) => (
          <div key={index} className={`plan-step ${step.requires_auth ? 'requires-auth' : ''}`}>
            <div className="step-indicator">
              <div className="step-number">{step.step}</div>
              {step.requires_auth && <div className="auth-badge">🔐</div>}
            </div>
            
            <div className="step-content">
              <div className="step-task">{step.task}</div>
              <div className="step-description">{step.description}</div>
              
              <div className="step-details">
                <span className="step-tool">Tool: {step.tool_id}</span>
                <span className="step-duration">⏱️ {step.estimated_duration}</span>
                {step.clarification_type && (
                  <span className="clarification-type">⚠️ {step.clarification_type}</span>
                )}
              </div>
              
              {step.depends_on && (
                <div className="step-dependencies">
                  <strong>Depends on:</strong> {step.depends_on.join(", ")}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="plan-features">
        <div className="feature-badges">
          {plan.supports_rollback && <span className="feature-badge">🔄 Rollback Support</span>}
          {plan.has_clarifications && <span className="feature-badge">⚠️ Human Review Points</span>}
          <span className="feature-badge">📊 Full Audit Trail</span>
        </div>
      </div>
    </div>
  );
}

export default PlanPreview;
