from portia.agent import Agent, Plan, PlanState, PlanRun
from tool_email import send_email
from tool_data import fetch_and_summarize_data
from db import save_plan, get_plan_by_id, list_all_plans
from final_output_summarizer import FinalOutputSummarizer
from portia.config import Config
from portia.memory import AgentMemory

# Initialize config and memory for summarizer (you would configure properly)
config = Config()
agent_memory = AgentMemory()
final_output_summarizer = FinalOutputSummarizer(config, agent_memory)

async def run_plan(request, user):
    plan_steps = [
        {"tool": "fetch_and_summarize_data", "params": {"source": "sales_db"}},
        {"tool": "send_email", "params": {
            "to": request["to"], "subject": "Sales Summary", "body_from_result": True
        }}
    ]
    plan = Plan(steps=plan_steps, user=user)
    state = PlanState(plan=plan)

    # Create plan run container for summarizer utility
    plan_run = PlanRun(plan=plan, state=state)

    for idx, step in enumerate(plan.steps):
        if step["tool"] == "fetch_and_summarize_data":
            result = fetch_and_summarize_data(**step["params"])
            state.results.append(result)
        elif step["tool"] == "send_email":
            body = state.results[-1]["summary"] if step.get("body_from_result") else step["params"]["body"]
            result = send_email(step["params"]["to"], step["params"]["subject"], body)
            state.results.append(result)
        save_plan(state)

    summary = final_output_summarizer.create_summary(plan, plan_run)
    return {"plan_id": state.plan.id, "results": state.results, "summary": summary}

async def get_plan(plan_id, user):
    return get_plan_by_id(plan_id, user)

async def list_plans(user):
    return list_all_plans(user)
