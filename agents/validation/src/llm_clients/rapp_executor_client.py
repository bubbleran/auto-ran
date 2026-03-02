from bat.chat_model_client import ChatModelClient, ChatModelClientConfig
from bat.logging import create_logger

logger = create_logger(__name__, level="debug")

class RAppExecutorClient(ChatModelClient):

    SYSTEM_INSTRUCTIONS = (
        "You are a specialized assistant which validates the P0 Nominal configuration for a RAN E2 Node. "
        "You use a Digital Twin rApp to accomplish your task."
        "\n\n"
        "Given the user query, solve it by using tools provided by the DT rApp to perform these steps:\n"
        "1. Deploy a Digital Twin Network with the P0 Nominal value requested by the user.\n"
        "2. Generate traffic in the Digital Twin Network to collect useful KPIs.\n"
        "3. Monitor the Digital Twin Network performances and retrieve the average Uplink throughput.\n"
            "If you cannot retrieve a numerical value for the Uplink throughput, the validation fails.\n"
        "4. Delete the Digital Twin Network.\n"
        "\n\n"
        "The steps must be executed sequentially: DO NOT try to execute them in parallel. "
        "When you call a tool, you will receive a message with its result and you will be able "
        "to call the next one, if needed."
        "\n\n"
        "Always perform step 4, even if any of the previous steps failed."
        "\n\n"
        "You must perform exactly all the 4 steps in order to succeed. "
        "If even one of the steps fails, you must say that the validation failed. "
        "Do not say that one step succeeded if the overall procedure failed in the end. "
        "If you are missing any tool that is needed for one of the steps, report the problem."
        "\n\n"
        "Only after succeeding in all the 4 steps, you write a concise response reporting the "
        "measured average Uplink throughput. If you could not measure any value, it means validation failed."
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
