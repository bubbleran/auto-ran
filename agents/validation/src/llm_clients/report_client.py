from bat.chat_model_client import ChatModelClient, ChatModelClientConfig
from bat.logging import create_logger

logger = create_logger(__name__, level="debug")

class ReportClient(ChatModelClient):

    SYSTEM_INSTRUCTIONS = (
        "You are a specialized assistant which generates a report about P0 Nominal configuration "
        "validation for a RAN E2 Node.\n\n"
        "You receive:\n"
        "1. The result of the validation procedure, i.e. the measured Uplink Throughput with the new P0 Nominal.\n"
        "2. The original request from the user, OPTIONALLY containing the current value of P0 Nominal as well.\n"
        "\n"
        "Your goal is to write a clean and concise report of 1-2 sentences following these instructions:\n"
        "- If the validation failed, just report the failure and nothing more.\n"
        "- If the validation succeeded, use the provided tools to register the result of the validation "
            "with the new P0 Nominal in your memory. Also, use the tools to read from your memory the "
            "Uplink Throughput measured with the current value (if provided in the original user request). "
            "Finally, generate a report including at least the measurement with the new P0 Nominal, and "
            "also the measurement with the current P0 Nominal if available.\n"
        "Note: No need to ask back the user to provide the current P0 Nominal if he doesn't provide it."
    )

    def __init__(
        self,
        tools,
    ):
        super().__init__(
            system_instructions=self.SYSTEM_INSTRUCTIONS,
            chat_model_config=ChatModelClientConfig.from_env(client_name="ExecutorClient"),
            tools=tools,
        )
