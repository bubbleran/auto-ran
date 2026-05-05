from bat.chat_model_client import ChatModelClient, ChatModelClientConfig
from bat.logging import create_logger
from langchain_core.messages import HumanMessage
from typing import Literal, List

ROUTER_TASK_MONITORING   = "monitoring"
ROUTER_TASK_OPTIMIZATION = "optimization"
ROUTER_TASK_REJECTED     = "rejected"
RouterTask = Literal["monitoring", "optimization", "rejected"]

logger = create_logger(__name__, "debug")

class RouterClient(ChatModelClient):

    SYSTEM_INSTRUCTIONS = (
        "You are a specialized assistant working in the Telecommunication industry, specifically private 5G. "
        "Your role is to redirect a user request in an agentic workflow.\n"
        "You support ONLY the following 2 types of request:\n"
        "1. Monitor the network UL throughput and/or SNR (PUSCH, PUCCH) and/or the P0 Nominal configuration.\n"
        "2. Optimize the P0 Nominal configuration parameter (validating the new config in a Digital Twin).\n\n"
        "Any other type of request must be rejected.\n"
        "Given the conversation between the user and the assistant, consider the whole context but focus "
        "your attention on the last request to classify in one of the two kinds, or reject it.\n\n"
        f"Respond with one single word: either '{ROUTER_TASK_MONITORING}' or '{ROUTER_TASK_OPTIMIZATION} "
        f"or '{ROUTER_TASK_REJECTED}' (without quotes).\n"
    )

    USER_INSTRUCTIONS = (
        "CONVERSATION:\n{conversation}\n\n"
        f"CLASSIFIED AS ({ROUTER_TASK_MONITORING}|{ROUTER_TASK_OPTIMIZATION}|{ROUTER_TASK_REJECTED}): "
    )

    def __init__(
        self,
    ):
        super().__init__(
            system_instructions=self.SYSTEM_INSTRUCTIONS,
            chat_model_config=ChatModelClientConfig.from_env(client_name="RouterClient"),
            tools=None,
        )

    def invoke(
        self,
        user_inputs: List[str],
        assistant_outputs: List[str],
    ) -> RouterTask:
        conversation = ""
        for user_input, assistant_output in zip(user_inputs, assistant_outputs):
            conversation += f"Query: {user_input}\nAnswer: {assistant_output}\n"
        conversation += f"Query: {user_inputs[-1]}"

        query = RouterClient.USER_INSTRUCTIONS.format(
            conversation=conversation,
        )
        logger.debug(f"Invoking with {len(user_inputs)} user inputs and {len(assistant_outputs)} assistant outputs.")
        response = super().invoke(HumanMessage(content=query))
        response_content = response.content.lower().strip().split("</think>")[-1].strip()
        # remove leading and trailing quotes
        if response_content.startswith('"') and response_content.endswith('"') or \
           response_content.startswith("'") and response_content.endswith("'"):
            response_content = response_content[1:-1]
        if response_content not in (
            ROUTER_TASK_MONITORING,
            ROUTER_TASK_OPTIMIZATION,
            ROUTER_TASK_REJECTED,
        ):
            raise ValueError(f"Unexpected routing output '{response_content}'")
        logger.debug(f"Response: {response_content}")
        return response_content
