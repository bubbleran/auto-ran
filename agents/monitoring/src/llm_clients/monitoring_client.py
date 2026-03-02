from bat.chat_model_client import ChatModelClient, ChatModelClientConfig

class MonitoringClient(ChatModelClient):

    SYSTEM_INSTRUCTIONS = (
        "You are a network assistant with the role of monitoring an access network "
        "configuration and KPIs. In particular, you can monitor the P0 Nominal and "
        "the Uplink Throughput of the network.\n"
        "Use the provided tools to either monitor the configuration or the KPIs (or both).\n"
        "If you are missing any information that is needed to call the tools, just say "
        "that you are not able to perform the required action.\n"
        "Reject any query that is not about monitoring either the P0 Nominal or the KPIs.\n"
        "After successfully calling the tools, extract the output and present them in a "
        "clear way to the user."
    )

    def __init__(
        self,
        tools,
    ):
        super().__init__(
            system_instructions=self.SYSTEM_INSTRUCTIONS,
            chat_model_config=ChatModelClientConfig.from_env(client_name="MonitoringClient"),
            tools=tools,
        )
