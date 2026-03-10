import asyncio
from bat.agent import AgentGraph, AgentState, AgentTaskResult
from bat.logging import create_logger
from bat.prebuilt import ReActLoop
from langgraph.graph import START, END
from .llm_clients import MonitoringClient
from .tools import wrap_mcp_tool
from typing import Any, Optional, Self
from typing_extensions import override


logger = create_logger("MonitoringAgentGraph", level="debug")
class MonitoringAgentState(AgentState):
    query: str
    response: Optional[str] = None

    @classmethod
    @override
    def from_query(
        cls,
        query: str
    ) -> Self:
        return cls(query=query)

    @override
    def to_task_result(
        self
    ) -> AgentTaskResult:
        return AgentTaskResult(
            task_status="completed" if self.response else "working",
            content=self.response or "Generating response...",
        )


class MonitoringAgentGraph(AgentGraph):
    # Node names
    GENERATION = "generation"

    @override
    def setup(
        self,
        config,
    ) -> None:
        # Create an LLM client providing the tools
        monitoring_list_tools = asyncio.run(config.list_tools(["Auto-RAN"]))
        monitoring_tools = [wrap_mcp_tool(t) for t in monitoring_list_tools if t.name!="set_p0_nominal_tool"]
        self.monitoring_client = MonitoringClient(tools=monitoring_tools)

        # Create the ReAct loop providing the monitoring_client
        # Note: 'query' is a key in MonitoringAgentState
        self.monitoring_loop = ReActLoop(
            config=config,
            StateType=MonitoringAgentState,
            chat_model_client=self.monitoring_client,
            loop_name="generation_loop",
            input_key="query",
            output_key="response",
        )
        # Add nodes and edges to the graph
        self.graph_builder.add_node(MonitoringAgentGraph.GENERATION, self.monitoring_loop.as_runnable())

        # Add edges to connect the nodes
        self.graph_builder.add_edge(START, MonitoringAgentGraph.GENERATION)
        self.graph_builder.add_edge(MonitoringAgentGraph.GENERATION, END)
