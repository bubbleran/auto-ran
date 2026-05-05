from bat.chat_model_client import ChatModelClient, ChatModelClientConfig

class OptimizationClient(ChatModelClient):
    SYSTEM_INSTRUCTIONS = (
        "You are the Optimization Client for p0-nominal planning.\n"
        "Use the provided tool to generate one p0 nominal recommendation, "
        "based on the current Uplink Throughput. If no current uplink throughput is "
        "provided, state it and propose a default P0 Nominal of -90 dBm without using any tool."
        "\n\n"
        "Always reply with the following format:\n"
        "{\n"
        "   p0_candidate: <recommended P0 nominal value in dBm (DON'T put the unit)>,\n"
        "   rationale: <one sentence to explain your choice>\n"
        "}\n"
    )

    def __init__(
        self,
        tools
    ):
        super().__init__(
            system_instructions=self.SYSTEM_INSTRUCTIONS,
            chat_model_config=ChatModelClientConfig.from_env(client_name="OptimizationClient"),
            tools=tools,
        )
