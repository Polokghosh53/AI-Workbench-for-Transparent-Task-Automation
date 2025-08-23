# Demo: Use in-memory storage for plans
plan_store = {}

def save_plan(state):
    plan_store[state.plan.id] = state

def get_plan_by_id(plan_id, user):
    state = plan_store.get(plan_id)
    return state.__dict__ if state and state.plan.user["username"] == user["username"] else None

def list_all_plans(user):
    results = []
    for state in plan_store.values():
        owner = None
        try:
            owner = state.plan.user["username"] if state and state.plan and state.plan.user else None
        except Exception:
            owner = None
        if owner == user["username"] or getattr(state, "user", {}).get("username") == user["username"]:
            results.append(state.__dict__)
    return results
