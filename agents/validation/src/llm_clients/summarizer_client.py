from bat.chat_model_client import ChatModelClient, ChatModelClientConfig
from bat.logging import create_logger
from langchain_core.messages import HumanMessage
from typing_extensions import override

logger = create_logger(__name__, level="debug")

class SummarizerClient(ChatModelClient):

    SYSTEM_INSTRUCTIONS = (
        "You are a specialized assistant which formulates a final answer as a result of an agentic "
        "P0 Nominal validation workflow for a RAN E2 Node."
        "\n\n"
        "Your task is simple:\n"
        "- You are provided as input a boolean flag indicating if the task was correctly formulated or not.\n"
        "- If it was NOT correctly formulated, you are also provided the original request, and your goal "
            "is to politely explain that the requested task is out of scope, or the request is malformed.\n"
        "- If it is correctly formulated, you are also provided the result of the validation. You should "
            "summarize it explaining if it was successful or not, and if it was, what is the numerical "
            "value of the Uplink throughput measured during the validation."
    )

    USER_INSTRUCTIONS = (
        "CORRECTLY FORMULATED:\n"
        "{flag}\n\n"
        "ORIGINAL QUERY OR VALIDATION RESULT:\n"
        "{input_str}\n\n"
        "YOUR ANSWER:\n"
    )

    def __init__(
        self,
    ):
        super().__init__(
            system_instructions=self.SYSTEM_INSTRUCTIONS,
            chat_model_config=ChatModelClientConfig.from_env(client_name="SummarizerClient"),
        )

    @override
    def invoke(
        self,
        flag: bool,
        input_str: str,
    ) -> str:
        input = HumanMessage(
            content=self.USER_INSTRUCTIONS.format(
                flag=flag,
                input_str=input_str,
            )
        )
        response = super().invoke(input)
        response = response.content.strip()
        return response
