from bat.chat_model_client import ChatModelClient, ChatModelClientConfig

class EnforceClient(ChatModelClient):
    SYSTEM_INSTRUCTIONS = (
        "You are the Enforcement Client for p0-nominal decisions. "
        "You receive monitoring KPIs and configuration, optimization output, and validator results.\n"
        "If the validation is successful and the new P0 Nominal give better UL throughput, "
        "use the provided tool to enforce "
        "the new recommended P0 Nominal, otherwise state that no action is going to take place.\n"
        "In case you use the enforcement tool, provide a short answer describing the applied changes. "
        "The name of the network you are working on is 'colsstb01'."
    )

    def __init__(
        self,
        tools,
    ):
        super().__init__(
            system_instructions=self.SYSTEM_INSTRUCTIONS,
            chat_model_config=ChatModelClientConfig.from_env(client_name="EnforceClient"),
            tools=tools,
        )
