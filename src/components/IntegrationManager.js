import React, { useState, useEffect } from 'react';
import apiClient from '../api/client';

function IntegrationManager({ onIntegrationSelect }) {
  const [integrations, setIntegrations] = useState(null);
  const [testResults, setTestResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedIntegration, setSelectedIntegration] = useState(null);
  const [queryInput, setQueryInput] = useState('');
  const [crmContacts, setCrmContacts] = useState(null);

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    try {
      setLoading(true);
      const response = await apiClient.get('/integrations/');
      setIntegrations(response.data);
    } catch (err) {
      setError('Failed to fetch integrations');
      console.error('Integration fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  const testAllIntegrations = async () => {
    try {
      setLoading(true);
      const response = await apiClient.post('/integrations/test/');
      setTestResults(response.data);
    } catch (err) {
      setError('Failed to test integrations');
      console.error('Integration test error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleDatabaseQuery = async (dbType) => {
    if (!queryInput.trim()) {
      setError('Please enter a SQL query');
      return;
    }

    try {
      setLoading(true);
      const response = await apiClient.post('/database/query/', {
        database_type: dbType,
        query: queryInput,
        params: []
      });
      
      setSelectedIntegration({
        type: 'database',
        subtype: dbType,
        result: response.data
      });
      
      if (onIntegrationSelect) {
        onIntegrationSelect({
          database_query: queryInput,
          database_type: dbType
        });
      }
    } catch (err) {
      setError(`Database query failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const fetchCrmContacts = async (crmType) => {
    try {
      setLoading(true);
      const response = await apiClient.get(`/crm/${crmType}/contacts/`, {
        params: { limit: 10 }
      });
      
      setCrmContacts(response.data);
      setSelectedIntegration({
        type: 'crm',
        subtype: crmType,
        result: response.data
      });
      
      if (onIntegrationSelect) {
        onIntegrationSelect({
          crm_operation: 'get_contacts',
          crm_type: crmType,
          crm_limit: 10
        });
      }
    } catch (err) {
      setError(`CRM query failed: ${err.response?.data?.detail || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const renderIntegrationStatus = (integration) => {
    const isConfigured = integration.configured;
    const statusClass = isConfigured ? 'status-configured' : 'status-unconfigured';
    
    return (
      <span className={`integration-status ${statusClass}`}>
        {isConfigured ? '✅ Configured' : '⚠️ Not Configured'}
      </span>
    );
  };

  const renderDatabaseSection = () => {
    if (!integrations?.integrations?.databases) return null;

    return (
      <div className="integration-section">
        <h3 className="section-title">🗄️ Database Integrations</h3>
        <div className="integration-grid">
          {Object.entries(integrations.integrations.databases).map(([dbType, config]) => (
            <div key={dbType} className="integration-card">
              <div className="integration-header">
                <h4>{dbType.toUpperCase()}</h4>
                {renderIntegrationStatus(config)}
              </div>
              <p className="integration-description">
                Execute SQL queries on {dbType} database
              </p>
              <div className="integration-tools">
                <span className="tool-count">{config.tools.length} tools</span>
              </div>
              {config.configured && (
                <div className="integration-actions">
                  <button 
                    className="btn btn-secondary"
                    onClick={() => handleDatabaseQuery(dbType)}
                    disabled={loading || !queryInput.trim()}
                  >
                    Query {dbType.toUpperCase()}
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
        
        <div className="query-input-section">
          <h4>SQL Query</h4>
          <textarea
            value={queryInput}
            onChange={(e) => setQueryInput(e.target.value)}
            placeholder="Enter your SQL query here..."
            className="query-input"
            rows="3"
          />
        </div>
      </div>
    );
  };

  const renderCrmSection = () => {
    if (!integrations?.integrations?.crm) return null;

    return (
      <div className="integration-section">
        <h3 className="section-title">👥 CRM Integrations</h3>
        <div className="integration-grid">
          {Object.entries(integrations.integrations.crm).map(([crmType, config]) => (
            <div key={crmType} className="integration-card">
              <div className="integration-header">
                <h4>{crmType.charAt(0).toUpperCase() + crmType.slice(1)}</h4>
                {renderIntegrationStatus(config)}
              </div>
              <p className="integration-description">
                Manage contacts and leads in {crmType}
              </p>
              <div className="integration-tools">
                <span className="tool-count">{config.tools.length} tools</span>
              </div>
              {config.configured && (
                <div className="integration-actions">
                  <button 
                    className="btn btn-secondary"
                    onClick={() => fetchCrmContacts(crmType)}
                    disabled={loading}
                  >
                    Get Contacts
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  const renderTestResults = () => {
    if (!testResults) return null;

    return (
      <div className="test-results">
        <h3 className="section-title">🧪 Integration Test Results</h3>
        <div className="test-summary">
          <span className={`test-status test-${testResults.overall_status}`}>
            Overall Status: {testResults.overall_status.toUpperCase()}
          </span>
        </div>

        <div className="test-sections">
          <div className="test-section">
            <h4>Database Tests</h4>
            {Object.entries(testResults.database_tests).map(([db, result]) => (
              <div key={db} className="test-item">
                <span className="test-name">{db.toUpperCase()}</span>
                <span className={`test-result test-${result.status}`}>
                  {result.status === 'success' ? '✅' : '❌'}
                </span>
                {result.error && <span className="test-error">{result.message}</span>}
              </div>
            ))}
          </div>

          <div className="test-section">
            <h4>CRM Tests</h4>
            {Object.entries(testResults.crm_tests).map(([crm, result]) => (
              <div key={crm} className="test-item">
                <span className="test-name">{crm.charAt(0).toUpperCase() + crm.slice(1)}</span>
                <span className={`test-result test-${result.status}`}>
                  {result.status === 'success' ? '✅' : '❌'}
                </span>
                {result.error && <span className="test-error">{result.message}</span>}
              </div>
            ))}
          </div>
        </div>
      </div>
    );
  };

  const renderSelectedIntegration = () => {
    if (!selectedIntegration) return null;

    const { type, subtype, result } = selectedIntegration;

    return (
      <div className="integration-result">
        <h3 className="section-title">
          📊 {type.toUpperCase()} Result - {subtype.toUpperCase()}
        </h3>
        
        {result.status === 'success' ? (
          <div className="result-success">
            <div className="result-meta">
              <span className="result-status">✅ Success</span>
              <span className="result-time">{result.timestamp}</span>
            </div>
            
            {type === 'database' && result.data && (
              <div className="database-results">
                <p><strong>Query Type:</strong> {result.query_type}</p>
                <p><strong>Database:</strong> {result.database}</p>
                {Array.isArray(result.data) ? (
                  <div className="data-table">
                    <p><strong>Records:</strong> {result.data.length}</p>
                    {result.data.length > 0 && (
                      <div className="table-preview">
                        <pre>{JSON.stringify(result.data.slice(0, 3), null, 2)}</pre>
                        {result.data.length > 3 && <p>... and {result.data.length - 3} more records</p>}
                      </div>
                    )}
                  </div>
                ) : (
                  <pre>{JSON.stringify(result.data, null, 2)}</pre>
                )}
              </div>
            )}
            
            {type === 'crm' && result.data && (
              <div className="crm-results">
                <p><strong>CRM:</strong> {result.crm}</p>
                <p><strong>Total:</strong> {result.total || result.total_size || result.data.length}</p>
                {result.data.length > 0 && (
                  <div className="contacts-preview">
                    <h4>Sample Contacts:</h4>
                    {result.data.slice(0, 3).map((contact, index) => (
                      <div key={index} className="contact-item">
                        <p><strong>Name:</strong> {contact.Name || `${contact.firstname || ''} ${contact.lastname || ''}`.trim()}</p>
                        <p><strong>Email:</strong> {contact.Email || contact.email}</p>
                        {(contact.Phone || contact.phone) && <p><strong>Phone:</strong> {contact.Phone || contact.phone}</p>}
                      </div>
                    ))}
                    {result.data.length > 3 && <p>... and {result.data.length - 3} more contacts</p>}
                  </div>
                )}
              </div>
            )}
          </div>
        ) : (
          <div className="result-error">
            <span className="error-status">❌ Error</span>
            <p>{result.message || result.error}</p>
          </div>
        )}
      </div>
    );
  };

  if (loading && !integrations) {
    return <div className="loading">Loading integrations...</div>;
  }

  return (
    <div className="integration-manager">
      <div className="integration-header">
        <h2>🔗 Integration Manager</h2>
        <div className="integration-actions">
          <button 
            className="btn btn-primary"
            onClick={testAllIntegrations}
            disabled={loading}
          >
            {loading ? 'Testing...' : 'Test All'}
          </button>
          <button 
            className="btn btn-secondary"
            onClick={fetchIntegrations}
            disabled={loading}
          >
            Refresh
          </button>
        </div>
      </div>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {integrations && (
        <div className="integration-overview">
          <div className="integration-stats">
            <div className="stat-item">
              <span className="stat-value">{integrations.total_tools}</span>
              <span className="stat-label">Total Tools</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">{integrations.portia_available ? 'Yes' : 'No'}</span>
              <span className="stat-label">Portia Available</span>
            </div>
            <div className="stat-item">
              <span className="stat-value">
                {Object.keys(integrations.tool_categories).length}
              </span>
              <span className="stat-label">Categories</span>
            </div>
          </div>
        </div>
      )}

      {renderDatabaseSection()}
      {renderCrmSection()}
      {renderTestResults()}
      {renderSelectedIntegration()}
    </div>
  );
}

export default IntegrationManager;
