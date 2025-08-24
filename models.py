from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Any, Optional

class Plan:
    def __init__(self, steps, user, query=None, description=None):
        self.id = str(uuid4())
        self.steps = steps
        self.user = user
        self.query = query or "AI Workbench Task"
        self.description = description
        self.created_at = datetime.now().isoformat()
        self.status = "created"
        self.metadata = {
            "portia_enhanced": True,
            "supports_clarifications": True,
            "supports_rollback": True
        }

class SimpleStep:
    def __init__(self, task, tool_id, output, inputs=None, description=None):
        self.task = task
        self.tool_id = tool_id
        self.output = output
        self.inputs = inputs or []
        self.description = description
        self.status = "pending"
        self.created_at = datetime.now().isoformat()

class PlanState:
    def __init__(self, plan):
        self.plan = plan
        self.results = []
        self.clarifications = []
        self.rollback_points = []
        
    def add_rollback_point(self, step_index, state_snapshot):
        """Add rollback point for Portia's state management"""
        self.rollback_points.append({
            "step_index": step_index,
            "timestamp": datetime.now().isoformat(),
            "state_snapshot": state_snapshot
        })
        
    def add_clarification(self, clarification_data):
        """Track clarifications for audit trail"""
        self.clarifications.append({
            "timestamp": datetime.now().isoformat(),
            **clarification_data
        })
