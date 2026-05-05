from src.bat_nat_connector import ConnectorNatBat
from src.graph import MonitoringAgentGraph, MonitoringAgentState

connector= ConnectorNatBat(
    AgentClass=MonitoringAgentGraph,
    StateClass=MonitoringAgentState
)
agent = connector.run()
