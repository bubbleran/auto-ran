from bat.agent import AgentApplication
from src import ValidationAgentGraph, ValidationAgentState

if __name__ == '__main__':
    agent = AgentApplication(
        ValidationAgentGraph,
        ValidationAgentState,
    )
    agent.run()
