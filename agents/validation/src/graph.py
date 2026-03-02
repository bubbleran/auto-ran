import asyncio
from .llm_clients import QueryValidationClient, RAppExecutorClient, ReportClient, SummarizerClient
from .tools import read_from_memory, write_to_memory
from bat.agent import AgentGraph, AgentState, AgentTaskResult
from bat.logging import create_logger
from bat.prebuilt import ReActLoop
from langgraph.graph import START, END
from typing import Literal, Optional, Self
from typing_extensions import override

logger = create_logger(__name__, level="debug")

class ValidationAgentState(AgentState):
    query: str
    status: Optional[str] = ""
    valid_query_flag: Optional[bool] = None
    dt_validation_response: Optional[str] = None
    report_request: Optional[str] = None
    response: Optional[str] = None
    completed: bool = False

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
            task_status="completed" if self.completed else "working",
            content=self.response or self.status or "Generating response...",
        )

class ValidationAgentGraph(AgentGraph):
    VALIDATE_QUERY = "validate_query"
    EXECUTE = "execute"
    BUILD_REPORT_REQUEST = "build_report_request"
    REPORT = "report"
    SUMMARIZE = "summarize"

    @classmethod
    def execute_or_summarize(
        cls,
        state: ValidationAgentState
    ) -> Literal["execute", "summarize"]:
        if state.valid_query_flag:
            return ValidationAgentGraph.EXECUTE
        return ValidationAgentGraph.SUMMARIZE

    @override
    def setup(
        self,
        config,
    ) -> None:
        dt_rapp_tools = asyncio.run(config.list_tools(["DTrApp"]))
        logger.debug(f"Retrieved {len(dt_rapp_tools)} tools for DT rApp.")

        self.router_client = QueryValidationClient()
        self.executor_client = RAppExecutorClient(
            tools=dt_rapp_tools,
        )
        self.report_client = ReportClient(
            tools=[read_from_memory, write_to_memory],
        )
        self.summarizer_client = SummarizerClient()

        self.rapp_loop = ReActLoop(
            config=config,
            StateType=ValidationAgentState,
            chat_model_client=self.executor_client,
            loop_name="rapp_loop",
            input_key="query",
            output_key="dt_validation_response",
            status_key="status",
        )
        self.report_loop = ReActLoop(
            config=config,
            StateType=ValidationAgentState,
            chat_model_client=self.report_client,
            loop_name="report_loop",
            input_key="report_request",
            output_key="response",
            status_key="status",
        )

        # Add nodes to the graph
        self.graph_builder.add_node(ValidationAgentGraph.VALIDATE_QUERY, self.validate_query)
        self.graph_builder.add_node(ValidationAgentGraph.EXECUTE, self.rapp_loop.as_runnable())
        self.graph_builder.add_node(ValidationAgentGraph.BUILD_REPORT_REQUEST, self.build_report_request)
        self.graph_builder.add_node(ValidationAgentGraph.REPORT, self.report_loop.as_runnable())
        self.graph_builder.add_node(ValidationAgentGraph.SUMMARIZE, self.summarize)

        # Add edges to connect the nodes
        self.graph_builder.add_edge(START, ValidationAgentGraph.VALIDATE_QUERY)
        self.graph_builder.add_conditional_edges(ValidationAgentGraph.VALIDATE_QUERY, ValidationAgentGraph.execute_or_summarize)
        self.graph_builder.add_edge(ValidationAgentGraph.EXECUTE, ValidationAgentGraph.BUILD_REPORT_REQUEST)
        self.graph_builder.add_edge(ValidationAgentGraph.BUILD_REPORT_REQUEST, ValidationAgentGraph.REPORT)
        self.graph_builder.add_edge(ValidationAgentGraph.REPORT, ValidationAgentGraph.SUMMARIZE)
        self.graph_builder.add_edge(ValidationAgentGraph.SUMMARIZE, END)

    async def validate_query(
        self,
        state: ValidationAgentState,
    ) -> ValidationAgentState:
        logger.debug("Node `validate_query`: invoked")
        state.valid_query_flag = self.router_client.invoke(state.query)
        logger.debug(f"Node `validate_query`: valid_query = {state.valid_query_flag}")
        return state

    async def summarize(
        self,
        state: ValidationAgentState,
    ) -> ValidationAgentState:
        logger.debug("Node `summarize`: invoked")
        response = self.summarizer_client.invoke(
            state.valid_query_flag,
            state.response if state.valid_query_flag else state.query,
        )
        state.response = response
        state.completed = True
        logger.debug("Node `summarize`: completed")
        return state

    async def build_report_request(
        self,
        state: ValidationAgentState,
    ) -> ValidationAgentState:
        logger.debug("Node `build_report_request`: invoked")
        state.report_request = (
            f"- Validation output: {state.dt_validation_response}\n"
            f"- Original user query: {state.query}"
        )
        logger.debug("Node `build_report_request`: completed")
        return state
