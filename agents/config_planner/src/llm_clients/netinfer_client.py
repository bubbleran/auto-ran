from bat.chat_model_client import ChatModelClient, ChatModelClientConfig

class NetworkNameInferClient(ChatModelClient):
    SYSTEM_INSTRUCTIONS = (
        "Given a user query, you always reply with the name of the network specified in the request, "
        "or unknown if the name is not provided.\n"
        "Example:\n"
        "User asks: What is the status of network 'abc123'?\n"
        "You reply: abc123\n"
        "User asks: Optimize the parameter XYZ of the `testnet` network\n"
        "You reply: testnet\n"
    )

    def __init__(
        self,
    ):
        super().__init__(
            system_instructions=self.SYSTEM_INSTRUCTIONS,
            chat_model_config=ChatModelClientConfig.from_env(client_name="NetworkNameInferClient"),
        )
