"""
Generic connector between BAT agents and NAT A2A server.
Provides a LangGraph wrapper that converts NAT message format to BAT agent state.
"""
import os
from bat.agent import AgentState, AgentGraph
from bat.agent.config import AgentConfig
from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.graph.state import CompiledStateGraph
from typing import Any, Dict, Optional, Type

load_dotenv()

class MessageWrapper(MessagesState):
    query: str
    
def _get_query_from_state(state: Dict[str, Any]) -> str:
    """Extract query string from the last message in state."""
    msgs = state.get("messages") or []
    if isinstance(msgs, list) and msgs:
        last = msgs[-1]
        content = getattr(last, "content", None)
        if isinstance(content, str) and content.strip():
            return content.strip()

class ConnectorNatBat:
    """LangGraph connector between NAT A2A server and BAT agent."""
    
    def __init__(
        self,
        AgentClass: Optional[Type[AgentGraph]] = None,
        StateClass: Optional[Type[AgentState]] = None,
        config_path: Optional[str] = None
    ):
        """
        Initialize the connector and build the graph.
        
        Args:
            AgentClass: BAT agent class (e.g., RNGAgentGraph). If None, uses env vars.
            StateClass: BAT state class (e.g., RNGAgentState). If None, uses env vars.
            config_path: Path to agent config YAML. If None, uses CONFIG env var.
        
        Environment variables (used as fallback if args not provided):
        - CONFIG: Path to agent config YAML (default: "config.yaml")
        - AGENT_MODULE: Module path for agent (default: "src.graph")
        - AGENT_CLASS: Agent class name (default: "RNGAgentGraph")
        - AGENT_STATE_CLASS: State class name (default: "RNGAgentState")
        """
        self.AgentClass = AgentClass
        self.StateClass = StateClass
        self.config_path = config_path
        
        # Load config and create BAT agent
        cfg = AgentConfig.load(self.config_path or os.getenv("CONFIG", "config.yaml"))
        agent_obj = self.AgentClass(config=cfg, StateType=self.StateClass)
        self.agent_compiled = agent_obj._graph

        # Build LangGraph wrapper
        self.graph = StateGraph(MessageWrapper)

        def normalize(state: Dict[str, Any]) -> Dict[str, Any]:
            """Extract query from messages."""
            q = _get_query_from_state(state)
            return {"query": q}

        async def run_agent(state: Dict[str, Any]) -> Dict[str, Any]:
            """Run BAT agent and convert result to message."""
            q = state.get("query", "")
            agent_state = self.StateClass.from_query(q)
            out = await self.agent_compiled.ainvoke(agent_state.model_dump())

            if hasattr(out, "response"):
                text = out.response or ""
            elif isinstance(out, dict) and "response" in out:
                text = out["response"] or ""
            else:
                text = str(out)
            return {"messages": [AIMessage(content=text)]}

        self.graph.add_node("normalize", normalize)
        self.graph.add_node("run_agent", run_agent)
        
        self.graph.add_edge(START, "normalize")
        self.graph.add_edge("normalize", "run_agent")
        self.graph.add_edge("run_agent", END)
    
    def run(self) -> CompiledStateGraph:
        """
        Compile and return the LangGraph.
        
        Returns:
            Compiled LangGraph that wraps the BAT agent.
        """
        return self.graph.compile()
