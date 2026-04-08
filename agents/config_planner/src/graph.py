import asyncio
import os
from .llm_clients import EnforceClient, OptimizationClient, RouterClient, RouterTask, ValRequestClient, NetworkNameInferClient
from .tools import optimize_p0_tool
from a2a.types import Message, TextPart
from bat.agent import AgentGraph, AgentState, AgentTaskResult
from bat.logging import create_logger
from bat.prebuilt import ReActLoop, CallAgentNode
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, END
from typing import List, Optional, Self
from typing_extensions import override

logger = create_logger(__name__, "debug")

called_agent_context_id = 0

def _build_agent_message(config: RunnableConfig, text: str) -> Message:
    global called_agent_context_id
    cfg = (config or {}).get("configurable", {}) or {}
    thread_id = cfg.get("thread_id", "config-planner")
    called_agent_context_id += 1
    return Message(
        context_id=f"{thread_id}-{called_agent_context_id}",
        message_id="0",
        role="user",
        parts=[TextPart(text=text)],
    )

class ConfigPlannerAgentState(AgentState):
    query: str
    response: Optional[str] = None

    task: Optional[RouterTask] = None

    history: List[BaseMessage] = []
    user_inputs: List[str] = []
    assistant_outputs: List[str] = []
    status: Optional[str] = None

    # Monitoring phase
    monitoring_prompt: Optional[str] = None
    monitoring_response: Optional[str] = None

    # Optimization phase
    optimization_prompt: Optional[str] = None
    optimization_response: Optional[str] = None

    # Validation phase
    validation_prompt: Optional[str] = None
    validation_response: Optional[str] = None

    # Enforce phase
    enforce_prompt: Optional[str] = None

    # Shared agent streaming fields (reused across sub-agent calls)
    agent_response_status: Optional[str] = None
    agent_input_required: bool = False
    agent_response_content: Optional[str] = None

    @classmethod
    @override
    def from_query(
        cls,
        query: str,
    ) -> Self:
        return cls(query=query, user_inputs=[query])

    @override
    def update_after_checkpoint_restore(self, query: str) -> None:
        self.user_inputs.append(query)
        self.query = query
        self.response = None
        self.task = None
        self.status = None
        self.monitoring_prompt = None
        self.monitoring_response = None
        self.optimization_prompt = None
        self.optimization_response = None
        self.validation_prompt = None
        self.validation_response = None
        self.enforce_prompt = None
        self.agent_response_status = None
        self.agent_input_required = False
        self.agent_response_content = None

    @override
    def to_task_result(self) -> AgentTaskResult:
        if self.response is not None:
            return AgentTaskResult(
                task_status="completed",
                content=self.response,
            )

        # Still working - stream content based on current phase
        if self.enforce_prompt:
            content = "Planning next action..."
        elif self.validation_response:
            content = self.validation_response
        elif self.validation_prompt:
            content = self.agent_response_content or self.optimization_response or "Validating configuration..."
        elif self.optimization_response:
            content = self.optimization_response
        elif self.optimization_prompt:
            content = "Optimizing p0-nominal..."
        elif self.monitoring_response:
            content = self.monitoring_response
        elif self.monitoring_prompt:
            content = self.agent_response_content or "Retrieving KPIs..."
        else:
            content = "Working..."

        if len(content) > 200:
            content = content[:200] + "..."

        return AgentTaskResult(
            task_status="working",
            content=content,
        )

class ConfigPlannerAgentGraph(AgentGraph):
    ROUTING = "routing"
    BUILD_MONITORING = "build_monitoring"
    CALL_MONITORING = "call_monitoring"
    BUILD_OPTIMIZATION = "build_optimization"
    OPTIMIZE = "optimize"
    BUILD_VALIDATION = "build_validation"
    CALL_VALIDATION = "call_validation"
    BUILD_ENFORCE = "build_enforce"
    ENFORCE = "enforce"
    SAVE_ANSWER = "save_answer"

    @classmethod
    def _monitor_or_save(
        cls,
        state: ConfigPlannerAgentState,
    ) -> str:
        return cls.SAVE_ANSWER if state.task == "rejected" else cls.BUILD_MONITORING

    @classmethod
    def _optimize_or_save(
        cls,
        state: ConfigPlannerAgentState,
    ) -> str:
        return cls.SAVE_ANSWER if state.task == "monitoring" else cls.BUILD_OPTIMIZATION

    @override
    def setup(self, config) -> None:
        monitoring_agent = os.getenv("MONITORING_AGENT_NAME", "Monitoring Agent")
        validator_agent = os.getenv("VALIDATOR_AGENT_NAME", "Validation Agent")
        enforcement_list_tools = asyncio.run(config.list_tools(["Auto-RAN"]))
        enforcement_tools= []
        for t in enforcement_list_tools:
            if t.name == "set_p0_nominal_tool":
                enforcement_tools.append(t)

        self.monitoring_call = CallAgentNode(
            config=config, 
            StateType=ConfigPlannerAgentState,
            loop_name="call_monitoring",
            agent_name=monitoring_agent,
            input="monitoring_prompt",
            output="monitoring_response",
            global_status="status",
            agent_input_required="agent_input_required",
            agent_response_status="agent_response_status",
            agent_response_content="agent_response_content",
            build_message=_build_agent_message,
        )

        self.validation_call = CallAgentNode(
            config=config,
            StateType=ConfigPlannerAgentState,
            loop_name="call_validation",
            agent_name=validator_agent,
            input="validation_prompt",
            output="validation_response",
            global_status="status",
            agent_input_required="agent_input_required",
            agent_response_status="agent_response_status",
            agent_response_content="agent_response_content",
            build_message=_build_agent_message,
        )

        self.router_client = RouterClient()
        self.netinfer_client = NetworkNameInferClient()
        self.optimization_client = OptimizationClient(tools=[optimize_p0_tool])
        self.validation_request_client = ValRequestClient()
        self.enforce_client = EnforceClient(tools=enforcement_tools)

        self.optimization_loop = ReActLoop(
            config=config,
            StateType=ConfigPlannerAgentState,
            loop_name="optimization_loop",
            chat_model_client=self.optimization_client,
            input_key="optimization_prompt",
            output_key="optimization_response",
            messages_key="history",
            status_key="status",
        )

        self.enforce_loop = ReActLoop(
            config=config,
            StateType=ConfigPlannerAgentState,
            loop_name="enforce_loop",
            chat_model_client=self.enforce_client,
            input_key="enforce_prompt",
            output_key="response",
            messages_key="history",
            status_key="status",
        )

        self.graph_builder.add_node(self.ROUTING, self._routing)
        self.graph_builder.add_node(self.BUILD_MONITORING, self._build_monitoring_prompt)
        self.graph_builder.add_node(self.CALL_MONITORING, self.monitoring_call.as_runnable())
        self.graph_builder.add_node(self.BUILD_OPTIMIZATION, self._build_optimization_prompt)
        self.graph_builder.add_node(self.OPTIMIZE, self.optimization_loop.as_runnable())
        self.graph_builder.add_node(self.BUILD_VALIDATION, self._build_validation_prompt)
        self.graph_builder.add_node(self.CALL_VALIDATION, self.validation_call.as_runnable())
        self.graph_builder.add_node(self.BUILD_ENFORCE, self._build_enforce_prompt)
        self.graph_builder.add_node(self.ENFORCE, self.enforce_loop.as_runnable())
        self.graph_builder.add_node(self.SAVE_ANSWER, self._save_answer)

        self.graph_builder.add_edge(START, self.ROUTING)
        self.graph_builder.add_conditional_edges(self.ROUTING, self._monitor_or_save)
        self.graph_builder.add_edge(self.BUILD_MONITORING, self.CALL_MONITORING)
        self.graph_builder.add_conditional_edges(self.CALL_MONITORING, self._optimize_or_save)
        self.graph_builder.add_edge(self.BUILD_OPTIMIZATION, self.OPTIMIZE)
        self.graph_builder.add_edge(self.OPTIMIZE, self.BUILD_VALIDATION)
        self.graph_builder.add_edge(self.BUILD_VALIDATION, self.CALL_VALIDATION)
        self.graph_builder.add_edge(self.CALL_VALIDATION, self.BUILD_ENFORCE)
        self.graph_builder.add_edge(self.BUILD_ENFORCE, self.ENFORCE)
        self.graph_builder.add_edge(self.ENFORCE, self.SAVE_ANSWER)
        self.graph_builder.add_edge(self.SAVE_ANSWER, END)

    def _routing(
        self,
        state: ConfigPlannerAgentState,
    ) -> ConfigPlannerAgentState:
        logger.debug("Node `routing`: invoked")
        task = self.router_client.invoke(state.user_inputs, state.assistant_outputs)
        state.task = task
        logger.debug(f"Node `routing`: task = {task}")
        return state

    def _build_monitoring_prompt(
        self,
        state: ConfigPlannerAgentState
    ) -> ConfigPlannerAgentState:
        logger.debug("Node `build_monitoring_prompt`: invoked")
        if state.task == "monitoring":
            state.monitoring_prompt = state.query
        else:
            network_name = self.netinfer_client.invoke(HumanMessage(state.query))
            state.monitoring_prompt = (
                f"Provide the current P0 Nominal and Uplink Throughput for the network called {network_name}"
            )
        logger.debug(f"Node `build_monitoring_prompt`: {state.task}, done")
        return state

    def _build_optimization_prompt(
        self,
        state: ConfigPlannerAgentState
    ) -> ConfigPlannerAgentState:
        logger.debug("Node `build_optimization_prompt`: invoked")
        state.agent_response_content = None
        state.optimization_prompt = (
            "A Monitoring assistant reports the following situation for the network:\n"
            f"{state.monitoring_response}\n\n"
            "If possible, propose an optimized P0 Nominal value."
        )
        logger.debug(f"Node `build_optimization_prompt`: done")
        return state

    def _build_validation_prompt(
        self,
        state: ConfigPlannerAgentState
    ) -> ConfigPlannerAgentState:
        logger.debug("Node `build_validation_prompt`: invoked")
        state.validation_prompt = self.validation_request_client.invoke(
            monitoring_result=state.monitoring_response,
            optimization_result=state.optimization_response,
        )
        logger.debug(f"Node `build_validation_prompt`: generated prompt: {state.validation_prompt}")
        return state

    def _build_enforce_prompt(
        self,
        state: ConfigPlannerAgentState
    ) -> ConfigPlannerAgentState:
        logger.debug("Node `build_enforce_prompt`: invoked")
        state.agent_response_content = None
        state.enforce_prompt = (
            "A Validation Agent validated a new P0 Nominal proposal.\n"
            f"Validation Agent response: {state.validation_response}\n\n"
            "Based on all the provided information, enforce the new P0 Nominal when it leads to "
            "a higher uplink throughput."
        )
        logger.debug(f"Node `build_enforce_prompt`: {state.enforce_prompt}")
        return state

    def _save_answer(
        self,
        state: ConfigPlannerAgentState,
    ) -> ConfigPlannerAgentState:
        logger.debug("Node `save_answer`: invoked")
        if state.response is None:
            state.response = state.validation_response or state.monitoring_response or \
                "Unfortunately, your request is out of my scope."
        state.assistant_outputs.append(state.response)
        logger.debug(f"Node `save_answer`: saved `{state.response}`")
        return state
