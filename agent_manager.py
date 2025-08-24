import os
from dotenv import load_dotenv
from db import save_plan, get_plan_by_id, list_all_plans
from tool_email import send_email
from tool_data import fetch_and_summarize_data

# Optional Portia imports with graceful fallback
try:
    from portia.plan import PlanBuilder
    from portia.plan import Plan as PortiaPlan
    from portia.execution_agents.utils.final_output_summarizer import FinalOutputSummarizer as PortiaFinalOutputSummarizer
    from portia.config import Config
    from portia import LLMProvider
    PORTIA_AVAILABLE = True
except Exception:
    from models import Plan  # fallback Plan model
    PORTIA_AVAILABLE = False

    class PortiaFinalOutputSummarizer:  # type: ignore
        def __init__(self, *_args, **_kwargs):
            pass

        def create_summary(self, plan, plan_run):
            # Basic fallback summary
            return f"Plan {getattr(plan, 'id', 'unknown')} executed with {len(getattr(plan_run, 'results', []))} results."

    class SimpleStep:
        def __init__(self, task, tool_id, output, inputs=None):
            self.task = task
            self.tool_id = tool_id
            self.output = output
            self.inputs = inputs or []

# Initialize Portia Config (can be customized)
# Load environment variables from .env file
load_dotenv()

# Get API keys from environment variables
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
PORTIA_API_KEY = os.getenv('PORTIA_API_KEY')

# Initialize summarizer based on availability
if PORTIA_AVAILABLE:
    # Initialize Portia Config with API keys and preferred LLM provider
    config = Config.from_default(
        llm_provider=LLMProvider.OPENAI,
        default_model="openai/gpt-4.1",
        openai_api_key=OPENAI_API_KEY,
    )
    final_output_summarizer = PortiaFinalOutputSummarizer(config, agent_memory=None)
else:
    config = None
    final_output_summarizer = PortiaFinalOutputSummarizer()

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
    # Build the plan
    if PORTIA_AVAILABLE:
        plan_builder = PlanBuilder(query=request.get("query", "Default query"))
        plan_builder.step(
            task="Fetch and summarize sales data",
            tool_id="fetch_and_summarize_data",
            output="data_summary"
        )
        plan_builder.step(
            task="Send sales summary email",
            tool_id="send_email",
            output="email_status",
            inputs=[
                {"name": "to", "value": request["to"]},
                {"name": "subject", "value": "Sales Summary"},
                {"name": "body", "value": "${data_summary}"}
            ]
        )
        plan = plan_builder.build()
    else:
        # Fallback plan without Portia
        steps = [
            SimpleStep(
                task="Fetch and summarize sales data",
                tool_id="fetch_and_summarize_data",
                output="data_summary",
            ),
            SimpleStep(
                task="Send sales summary email",
                tool_id="send_email",
                output="email_status",
                inputs=[
                    {"name": "to", "value": request["to"]},
                    {"name": "subject", "value": "Sales Summary"},
                    {"name": "body", "value": "${data_summary}"},
                ],
            ),
        ]
        plan = Plan(steps=steps, user=user)
    # Attach user to plan for downstream filtering/serialization
    try:
        setattr(plan, "user", user)
    except Exception:
        pass

    # Initialize custom state tracker with current user for ownership filtering
    state = ExecutionState(plan, user=user)

    # Execute each step
    for step in plan.steps:
        if step.tool_id == "fetch_and_summarize_data":
            result = fetch_and_summarize_data()
            state.add_result(step.output, result)
        elif step.tool_id == "send_email":
            to = next(input_["value"] for input_ in step.inputs if input_["name"] == "to")
            subject = next(input_["value"] for input_ in step.inputs if input_["name"] == "subject")
            body_ref = next(input_["value"] for input_ in step.inputs if input_["name"] == "body")

            # Resolve variable reference in body
            if body_ref.startswith("${") and body_ref.endswith("}"):
                var_name = body_ref[2:-1]
                body = state.get_result(var_name)
                if isinstance(body, dict) and "summary" in body:
                    body = body["summary"]
            else:
                body = body_ref

            result = send_email(to, subject, body)
            state.add_result(step.output, result)

        # Save state after each step for transparency
        save_plan(state)

    # Generate final plan summary using Portia's summarizer utility
    summary = final_output_summarizer.create_summary(plan, state)

    return {
        "plan_id": str(plan.id),
        "results": state.results,
        "summary": summary,
    }

async def get_plan(plan_id, user):
    return get_plan_by_id(plan_id, user)

async def list_plans(user):
    return list_all_plans(user)
