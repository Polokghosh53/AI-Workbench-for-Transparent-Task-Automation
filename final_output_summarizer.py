from pydantic import BaseModel
from portia.execution_agents.utils.final_output_summarizer import FinalOutputSummarizer as PortiaFinalOutputSummarizer


class FinalOutputSummarizer:
    def __init__(self, config, agent_memory):
        self.summarizer = PortiaFinalOutputSummarizer(config, agent_memory)

    def get_output_value(self, output):
        return self.summarizer.get_output_value(output)

    def create_summary(self, plan, plan_run):
        # Returns a string summary or None
        return self.summarizer.create_summary(plan, plan_run)
