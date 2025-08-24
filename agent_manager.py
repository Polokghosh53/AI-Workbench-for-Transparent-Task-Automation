import os
from datetime import datetime
from dotenv import load_dotenv
from db import save_plan, get_plan_by_id, list_all_plans
from tool_email import send_email
from tool_data import fetch_and_summarize_data
from tool_registry import get_tool_registry, get_portia_instance

# Import models first
from models import Plan, SimpleStep

# Optional Portia imports with graceful fallback
try:
    from portia import PlanBuilder, Plan as PortiaPlan, Config, LLMProvider
    PORTIA_AVAILABLE = True
except Exception:
    PORTIA_AVAILABLE = False

    class PortiaFinalOutputSummarizer:  # type: ignore
        def __init__(self, *_args, **_kwargs):
            pass

        def create_summary(self, plan, plan_run):
            # Basic fallback summary
            return f"Plan {getattr(plan, 'id', 'unknown')} executed with {len(getattr(plan_run, 'results', []))} results."

# Initialize Portia Config (can be customized)
# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PORTIA_API_KEY = os.getenv('PORTIA_API_KEY')

# Initialize Portia config and tool registry if available
if PORTIA_AVAILABLE:
    try:
        config = Config.from_default(
            llm_provider=LLMProvider.OPENAI,
            default_model="gpt-4",
            openai_api_key=OPENAI_API_KEY,
        )
        # Get the integrated tool registry with all database and CRM tools
        integrated_registry = get_tool_registry()
        portia_instance = get_portia_instance()
    except Exception:
        config = None
        integrated_registry = None
        portia_instance = None
        PORTIA_AVAILABLE = False
else:
    config = None
    integrated_registry = None
    portia_instance = None

def create_rich_email_body(data_result):
    """Create a rich, formatted email body from data analysis results"""
    if not isinstance(data_result, dict):
        return str(data_result)
    
    # Start with the main summary
    email_parts = []
    
    # Header
    email_parts.append("📊 DATA ANALYSIS REPORT")
    email_parts.append("=" * 50)
    email_parts.append("")
    
    # Main summary
    if data_result.get("summary"):
        email_parts.append("📋 EXECUTIVE SUMMARY")
        email_parts.append("-" * 25)
        email_parts.append(data_result["summary"])
        email_parts.append("")
    
    # Statistics section
    if data_result.get("statistics"):
        stats = data_result["statistics"]
        email_parts.append("📊 KEY STATISTICS")
        email_parts.append("-" * 20)
        email_parts.append(f"• Total Records: {stats.get('total_rows', 'N/A'):,}")
        email_parts.append(f"• Numeric Columns: {stats.get('numeric_columns', 0)}")
        email_parts.append(f"• Text Columns: {stats.get('categorical_columns', 0)}")
        
        # Missing values summary
        if stats.get("missing_values"):
            missing_total = sum(stats["missing_values"].values())
            if missing_total > 0:
                email_parts.append(f"• Missing Values: {missing_total:,} total")
        email_parts.append("")
    
    # Key insights
    if data_result.get("insights") and len(data_result["insights"]) > 0:
        email_parts.append("💡 KEY INSIGHTS")
        email_parts.append("-" * 15)
        for i, insight in enumerate(data_result["insights"][:5], 1):
            email_parts.append(f"{i}. {insight}")
        email_parts.append("")
    
    # Numeric statistics details
    if data_result.get("numeric_statistics"):
        email_parts.append("🔢 NUMERIC ANALYSIS")
        email_parts.append("-" * 20)
        for col, stats in list(data_result["numeric_statistics"].items())[:3]:
            email_parts.append(f"\n{col.upper()}:")
            if stats.get("mean") is not None:
                email_parts.append(f"  • Average: {stats['mean']:.2f}")
            if stats.get("min") is not None and stats.get("max") is not None:
                email_parts.append(f"  • Range: {stats['min']:.2f} - {stats['max']:.2f}")
            if stats.get("std") is not None:
                email_parts.append(f"  • Std Dev: {stats['std']:.2f}")
        email_parts.append("")
    
    # Data source info
    if data_result.get("source_type") or data_result.get("original_filename"):
        email_parts.append("📁 DATA SOURCE")
        email_parts.append("-" * 15)
        if data_result.get("original_filename"):
            email_parts.append(f"• File: {data_result['original_filename']}")
        if data_result.get("source_type"):
            email_parts.append(f"• Type: {data_result['source_type']}")
        if data_result.get("timestamp"):
            email_parts.append(f"• Processed: {data_result['timestamp']}")
        email_parts.append("")
    
    # Visualizations note
    if data_result.get("visualizations") and len(data_result["visualizations"]) > 0:
        email_parts.append("📈 VISUALIZATIONS GENERATED")
        email_parts.append("-" * 30)
        for viz in data_result["visualizations"]:
            email_parts.append(f"• {viz.get('title', 'Chart')} ({viz.get('type', 'unknown')})")
        email_parts.append("")
        email_parts.append("Note: Charts are available in the web dashboard for detailed viewing.")
        email_parts.append("")
    
    # Footer
    email_parts.append("-" * 50)
    email_parts.append("Generated by AI Workbench - Transparent Task Automation")
    email_parts.append("For detailed visualizations, please visit the dashboard.")
    
    return "\n".join(email_parts)

async def handle_human_review_clarification(data_summary, recipient, user):
    """
    Portia's clarification system for human review of sensitive operations
    In production, this would integrate with Portia's cloud clarification UI
    """
    
    # For demo purposes, we'll auto-approve with logging
    # In production, this would pause execution and wait for human input
    
    clarification_data = {
        "type": "human_review",
        "status": "pending_review",
        "data_preview": {
            "summary": data_summary.get("summary", "No summary") if isinstance(data_summary, dict) else str(data_summary)[:200],
            "recipient": recipient,
            "timestamp": datetime.now().isoformat(),
            "user": user.get("username", "unknown")
        }
    }
    
    # Auto-approve for demo (in production, this would wait for human input)
    # This simulates Portia's clarification resolution
    approval_result = {
        "approved": True,
        "reason": "Auto-approved for demo - in production this would require human review",
        "reviewer": user.get("username", "system"),
        "timestamp": datetime.now().isoformat(),
        "clarification_id": f"review_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    }
    
    return approval_result

class ExecutionState:
    """Custom execution state tracking results by output ID."""
    def __init__(self, plan: Plan, user=None):
        self.plan = plan
        self.user = user
        self.results = []  # Stores dicts with keys: output and data

    def add_result(self, output_id, data):
        self.results.append({"output": output_id, "data": data})

    def get_result(self, output_id):
        for res in self.results:
            if res["output"] == output_id:
                return res["data"]
        return None

async def run_plan(request, user):
    query = request.get("query", "Analyze data and send summary")
    
    # Build the plan using Portia's structured approach
    if PORTIA_AVAILABLE:
        # Use Portia's plan generation for structured, reviewable plans
        plan_builder = PlanBuilder(query=query)
        
        # Dynamic plan building based on request context
        if request.get("file_path"):
            plan_builder.step(
                task=f"Analyze uploaded data file: {request.get('file_path', 'unknown')}",
                tool_id="fetch_and_summarize_data",
                output="data_analysis",
                description="Process and analyze the uploaded data file with visualizations and insights"
            )
        else:
            plan_builder.step(
                task="Fetch and analyze demo sales data",
                tool_id="fetch_and_summarize_data", 
                output="data_analysis",
                description="Generate sample sales data analysis with charts and statistics"
            )
        
        # Add database integration if requested
        if request.get("database_query"):
            db_type = request.get("database_type", "sqlite")
            plan_builder.step(
                task=f"Execute database query on {db_type}",
                tool_id=f"query_{db_type}_database",
                output="database_results",
                description=f"Query {db_type} database for additional context",
                inputs=[
                    {"name": "query", "value": request.get("database_query")},
                    {"name": "params", "value": request.get("database_params", [])}
                ]
            )
        
        # Add CRM integration if requested
        if request.get("crm_operation"):
            crm_type = request.get("crm_type", "salesforce")
            operation = request.get("crm_operation")
            
            if operation == "get_contacts":
                plan_builder.step(
                    task=f"Retrieve contacts from {crm_type}",
                    tool_id=f"get_{crm_type}_contacts",
                    output="crm_contacts",
                    description=f"Fetch contact information from {crm_type} CRM",
                    inputs=[
                        {"name": "limit", "value": request.get("crm_limit", 10)},
                        {"name": "search_term", "value": request.get("crm_search", None)}
                    ]
                )
            elif operation == "create_lead" and crm_type == "salesforce":
                plan_builder.step(
                    task="Create new lead in Salesforce",
                    tool_id="create_salesforce_lead",
                    output="new_lead",
                    description="Create a new lead based on data analysis",
                    inputs=[
                        {"name": "first_name", "value": request.get("lead_first_name", "")},
                        {"name": "last_name", "value": request.get("lead_last_name", "")},
                        {"name": "email", "value": request.get("lead_email", "")},
                        {"name": "company", "value": request.get("lead_company", "")}
                    ]
                )
        
        # Add integration testing if requested
        if request.get("test_integrations"):
            plan_builder.step(
                task="Test all integration connections",
                tool_id="test_integrations",
                output="integration_tests",
                description="Verify connectivity to databases and CRM systems"
            )
        
        # Add clarification point for sensitive operations
        plan_builder.step(
            task="Review data analysis before sending",
            tool_id="human_review_clarification",
            output="review_approval",
            description="Pause for human review of sensitive data before email transmission",
            inputs=[
                {"name": "data_summary", "value": "${data_analysis}"},
                {"name": "recipient", "value": request.get("to", "unknown")}
            ]
        )
        
        plan_builder.step(
            task="Send comprehensive data analysis email",
            tool_id="send_email",
            output="email_status",
            description="Send formatted email with analysis results and visualizations note",
            inputs=[
                {"name": "to", "value": request.get("to")},
                {"name": "subject", "value": "Data Analysis Report - AI Workbench"},
                {"name": "body", "value": "${data_analysis}"},
                {"name": "approved", "value": "${review_approval}"}
            ]
        )
        
        plan = plan_builder.build()
    else:
        # Enhanced fallback plan with structured steps
        steps = [
            SimpleStep(
                task=f"Analyze data file: {request.get('file_path', 'demo data')}",
                tool_id="fetch_and_summarize_data",
                output="data_analysis",
                description="Process uploaded data or generate demo analysis"
            ),
            SimpleStep(
                task="Human review checkpoint",
                tool_id="human_review_clarification", 
                output="review_approval",
                description="Pause for human approval before sending email"
            ),
            SimpleStep(
                task="Send analysis email",
                tool_id="send_email",
                output="email_status",
                inputs=[
                    {"name": "to", "value": request.get("to")},
                    {"name": "subject", "value": "Data Analysis Report - AI Workbench"},
                    {"name": "body", "value": "${data_analysis}"},
                ],
                description="Send comprehensive email with analysis results"
            ),
        ]
        plan = Plan(steps=steps, user=user, query=query)
    # Attach user to plan for downstream filtering/serialization
    try:
        setattr(plan, "user", user)
    except Exception:
        pass

    # Initialize custom state tracker with current user for ownership filtering
    state = ExecutionState(plan, user=user)

    # Execute each step with Portia's structured approach
    for step in plan.steps:
        if step.tool_id == "fetch_and_summarize_data":
            # Enhanced data analysis with file path support
            file_path = request.get("file_path")
            result = fetch_and_summarize_data(file_path=file_path)
            state.add_result(step.output, result)
            
        elif step.tool_id.startswith("query_") and step.tool_id.endswith("_database"):
            # Handle database queries
            if integrated_registry:
                db_tool = integrated_registry.get_tool(step.tool_id)
                if db_tool:
                    query = next((input_["value"] for input_ in step.inputs if input_["name"] == "query"), "")
                    params = next((input_["value"] for input_ in step.inputs if input_["name"] == "params"), [])
                    result = db_tool(query=query, params=params) if params else db_tool(query=query)
                    state.add_result(step.output, result)
                else:
                    state.add_result(step.output, {"error": f"Database tool {step.tool_id} not found"})
            else:
                state.add_result(step.output, {"error": "Database tools not available"})
                
        elif step.tool_id.startswith("get_") and ("salesforce" in step.tool_id or "hubspot" in step.tool_id or "zendesk" in step.tool_id):
            # Handle CRM get operations
            if integrated_registry:
                crm_tool = integrated_registry.get_tool(step.tool_id)
                if crm_tool:
                    limit = next((input_["value"] for input_ in step.inputs if input_["name"] == "limit"), 10)
                    search_term = next((input_["value"] for input_ in step.inputs if input_["name"] == "search_term"), None)
                    result = crm_tool(limit=limit, search_term=search_term)
                    state.add_result(step.output, result)
                else:
                    state.add_result(step.output, {"error": f"CRM tool {step.tool_id} not found"})
            else:
                state.add_result(step.output, {"error": "CRM tools not available"})
                
        elif step.tool_id.startswith("create_") and ("salesforce" in step.tool_id or "hubspot" in step.tool_id or "zendesk" in step.tool_id):
            # Handle CRM create operations
            if integrated_registry:
                crm_tool = integrated_registry.get_tool(step.tool_id)
                if crm_tool:
                    # Extract inputs based on tool type
                    if "salesforce_lead" in step.tool_id:
                        result = crm_tool(
                            first_name=next((input_["value"] for input_ in step.inputs if input_["name"] == "first_name"), ""),
                            last_name=next((input_["value"] for input_ in step.inputs if input_["name"] == "last_name"), ""),
                            email=next((input_["value"] for input_ in step.inputs if input_["name"] == "email"), ""),
                            company=next((input_["value"] for input_ in step.inputs if input_["name"] == "company"), "")
                        )
                    else:
                        result = {"error": f"Create operation for {step.tool_id} not implemented"}
                    state.add_result(step.output, result)
                else:
                    state.add_result(step.output, {"error": f"CRM tool {step.tool_id} not found"})
            else:
                state.add_result(step.output, {"error": "CRM tools not available"})
                
        elif step.tool_id == "test_integrations":
            # Handle integration testing
            if integrated_registry:
                test_tool = integrated_registry.get_tool("test_integrations")
                if test_tool:
                    result = test_tool()
                    state.add_result(step.output, result)
                else:
                    state.add_result(step.output, {"error": "Integration test tool not found"})
            else:
                state.add_result(step.output, {"error": "Integration tools not available"})
            
        elif step.tool_id == "human_review_clarification":
            # Portia's clarification system for human input
            data_summary = state.get_result("data_analysis")
            recipient = next((input_["value"] for input_ in step.inputs if input_["name"] == "recipient"), "unknown")
            
            # Create clarification request for human review
            clarification_result = await handle_human_review_clarification(
                data_summary=data_summary,
                recipient=recipient,
                user=user
            )
            state.add_result(step.output, clarification_result)
            
        elif step.tool_id == "send_email":
            # Enhanced email sending with approval check
            to = next(input_["value"] for input_ in step.inputs if input_["name"] == "to")
            subject = next(input_["value"] for input_ in step.inputs if input_["name"] == "subject")
            body_ref = next(input_["value"] for input_ in step.inputs if input_["name"] == "body")
            
            # Check if human approval was given
            approval = state.get_result("review_approval")
            if approval and not approval.get("approved", False):
                result = {
                    "status": "cancelled",
                    "reason": "Human review rejected the email sending",
                    "to": to,
                    "message": approval.get("reason", "No reason provided")
                }
            else:
                # Resolve variable reference in body
                if body_ref.startswith("${") and body_ref.endswith("}"):
                    var_name = body_ref[2:-1]
                    data_result = state.get_result(var_name)
                    if isinstance(data_result, dict):
                        body = create_rich_email_body(data_result)
                    else:
                        body = str(data_result)
                else:
                    body = body_ref

                result = send_email(to, subject, body)
            
            state.add_result(step.output, result)

        # Save state after each step for transparency and rollback capability
        save_plan(state)

    # Generate final plan summary
    if PORTIA_AVAILABLE:
        summary = f"Portia plan {plan.id} executed successfully with {len(state.results)} steps completed."
    else:
        summary = f"Plan {plan.id} executed with {len(state.results)} results."

    return {
        "plan_id": str(plan.id),
        "results": state.results,
        "summary": summary,
    }

async def get_plan(plan_id, user):
    return get_plan_by_id(plan_id, user)

async def list_plans(user):
    return list_all_plans(user)
