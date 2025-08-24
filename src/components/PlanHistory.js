import React, { useState, useEffect } from "react";
import apiClient from "../api/client";

function PlanHistory({ onPlanSelect }) {
  const [history, setHistory] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPlanHistory();
  }, []);

  const fetchPlanHistory = async () => {
    try {
      const response = await apiClient.get("/plan-history/");
      setHistory(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to fetch plan history");
    } finally {
      setLoading(false);
    }
  };

  const handleRollback = async (planId, stepIndex) => {
    if (!window.confirm(`Are you sure you want to rollback plan ${planId} to step ${stepIndex + 1}?`)) {
      return;
    }

    try {
      const response = await apiClient.post(`/rollback-plan/${planId}`, {
        step_index: stepIndex,
        reason: "User requested rollback from dashboard"
      });
      
      alert(`✅ ${response.data.message}`);
      fetchPlanHistory(); // Refresh the history
    } catch (err) {
      alert(`❌ Rollback failed: ${err.response?.data?.detail || "Unknown error"}`);
    }
  };

  if (loading) {
    return (
      <div className="plan-history loading">
        <div className="section-title">📚 Loading Plan History...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="plan-history error">
        <div className="section-title">❌ Failed to Load History</div>
        <div className="error-message">{error}</div>
        <button className="btn-secondary" onClick={fetchPlanHistory}>
          Retry
        </button>
      </div>
    );
  }

  if (!history || history.plans.length === 0) {
    return (
      <div className="plan-history empty">
        <div className="section-title">📚 Plan History</div>
        <div className="subtle">No previous plans found. Run your first plan to see history here.</div>
      </div>
    );
  }

  return (
    <div className="plan-history">
      <div className="history-header">
        <div className="section-title">📚 Plan History</div>
        <div className="history-stats">
          <span className="stat-badge">{history.total_count} Total Plans</span>
          {history.portia_features.rollback_support && (
            <span className="feature-badge">🔄 Rollback Enabled</span>
          )}
        </div>
      </div>

      <div className="history-list">
        {history.plans.map((plan, index) => (
          <div key={plan.plan_id || index} className="history-item">
            <div className="history-main">
              <div className="history-info">
                <div className="plan-query">{plan.query}</div>
                <div className="plan-meta">
                  <span className="plan-id">ID: {plan.plan_id}</span>
                  <span className="plan-date">
                    {new Date(plan.created_at).toLocaleDateString()} {new Date(plan.created_at).toLocaleTimeString()}
                  </span>
                </div>
              </div>
              
              <div className="plan-stats">
                <span className="stat-item">📋 {plan.steps_count} steps</span>
                <span className="stat-item">✅ {plan.results_count} results</span>
                {plan.has_clarifications && <span className="stat-item">⚠️ Had reviews</span>}
                {plan.rollback_points > 0 && <span className="stat-item">🔄 {plan.rollback_points} rollbacks</span>}
              </div>
            </div>

            <div className="history-actions">
              <button 
                className="btn-secondary"
                onClick={() => onPlanSelect && onPlanSelect(plan.plan_id)}
              >
                View Details
              </button>
              
              {plan.portia_enhanced && plan.steps_count > 1 && (
                <div className="rollback-options">
                  <select 
                    className="rollback-select"
                    onChange={(e) => {
                      if (e.target.value) {
                        handleRollback(plan.plan_id, parseInt(e.target.value));
                        e.target.value = "";
                      }
                    }}
                  >
                    <option value="">🔄 Rollback to...</option>
                    {Array.from({length: plan.steps_count}, (_, i) => (
                      <option key={i} value={i}>Step {i + 1}</option>
                    ))}
                  </select>
                </div>
              )}
            </div>

            <div className="plan-status">
              <span className={`status-badge status-${plan.status}`}>
                {plan.status}
              </span>
              {plan.portia_enhanced && (
                <span className="portia-badge">🤖 Portia Enhanced</span>
              )}
            </div>
          </div>
        ))}
      </div>

      <div className="portia-features-info">
        <div className="features-title">🚀 Portia AI Features Active:</div>
        <div className="features-list">
          {history.portia_features.state_management && <span className="feature-tag">📊 State Management</span>}
          {history.portia_features.rollback_support && <span className="feature-tag">🔄 Rollback Support</span>}
          {history.portia_features.clarifications && <span className="feature-tag">⚠️ Human Clarifications</span>}
          {history.portia_features.audit_trail && <span className="feature-tag">📋 Full Audit Trail</span>}
        </div>
      </div>
    </div>
  );
}

export default PlanHistory;
