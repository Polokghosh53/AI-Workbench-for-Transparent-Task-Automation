from fastapi import FastAPI, Depends
from agent_manager import run_plan, get_plan, list_plans
from auth import get_current_user

app = FastAPI()

@app.post("/run-plan/")
async def run_plan_endpoint(request: dict, user=Depends(get_current_user)):
    return await run_plan(request, user)

@app.get("/plans/")
async def get_plans(user=Depends(get_current_user)):
    return await list_plans(user)

@app.get("/plan/{plan_id}")
async def get_plan_endpoint(plan_id: str, user=Depends(get_current_user)):
    return await get_plan(plan_id, user)
