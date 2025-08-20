from uuid import uuid4

class Plan:
    def __init__(self, steps, user):
        self.id = str(uuid4())
        self.steps = steps
        self.user = user

class PlanState:
    def __init__(self, plan):
        self.plan = plan
        self.results = []
