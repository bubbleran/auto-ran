from bat.chat_model_client import ChatModelClient, ChatModelClientConfig
from langchain_core.messages import HumanMessage

class ValRequestClient(ChatModelClient):
    SYSTEM_INSTRUCTIONS = (
        "You are an expert in generating a request for a P0 Nominal Validation Agent.\n"
        "You are provided two inputs:\n"
        "- The result of a Monitoring Agent, with the current P0 Nominal and Uplink throughput.\n"
        "- The result of an Optimization algorithm, which includes a new P0 Nominal proposal.\n"
        "\n"
        "Your task is to write down a clear request for a P0 Nominal Validation Agent, following "
        "exactly this template and filling the placeholders in angular brackets with the "
        "information in your inputs."
        "TEMPLATE: Please validate a new P0 Nominal value of <new_p0_value>, considering that "
        "the current value of P0 Nominal is <current_p0_value>."
    )

    USER_INSTRUCTIONS = (
        "Result of Monitoring Agent:\n{mon_result}\n\n"
        "Result of Optimization algorithm:\n{opt_result}"
    )

    def __init__(
        self,
    ):
        super().__init__(
            system_instructions=self.SYSTEM_INSTRUCTIONS,
            chat_model_config=ChatModelClientConfig.from_env(client_name="ValRequestClient"),
            tools=None,
        )

    def invoke(
        self,
        monitoring_result: str,
        optimization_result: str,
    ) -> str:
        query = ValRequestClient.USER_INSTRUCTIONS.format(
            mon_result=monitoring_result,
            opt_result=optimization_result,
        )
        response = super().invoke(HumanMessage(content=query))
        response_content = response.content.lower().strip().split("</think>")[-1].strip()

        return response_content
