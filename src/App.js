import React from "react";
import PlanDashboard from "./components/PlanDashboard";
import "./styles.css";

function App() {
  return (
    <div className="container">
      <header className="app-header">
        <div className="brand">
          <span className="tag">AI</span>
          <div>
            <div className="headline">AI Workbench</div>
            <div className="subtle">Transparent task automation</div>
          </div>
        </div>
      </header>
      <PlanDashboard />
      <div className="footer">Built for clarity and speed</div>
    </div>
  );
}

export default App;


