from bat.agent import AgentApplication
from dotenv import load_dotenv
from src import ConfigPlannerAgentGraph, ConfigPlannerAgentState

load_dotenv()

if __name__ == '__main__':
    agent = AgentApplication(
        AgentGraphType=ConfigPlannerAgentGraph,
        AgentStateType=ConfigPlannerAgentState,
    )
    agent.run()
