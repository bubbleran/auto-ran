from bat.chat_model_client import ChatModelClient, ChatModelClientConfig
from bat.logging import create_logger
from langchain_core.messages import HumanMessage
from typing_extensions import override

logger = create_logger(__name__, level="debug")

class QueryValidationClient(ChatModelClient):

    SYSTEM_INSTRUCTIONS = (
        "You are a specialized assistant which validates queries for a P0 Nominal Validation Agent."
        "\n\n"
        "Your task is to determine if the user's query is related to validating a P0 Nominal value "
        "for a RAN E2 node and accept ONLY such queries. Also, you should reject any relevant query "
        "that is not specifying a P0 Nominal value to validate."
        "\n\n"
        "Your answer MUST consist of ONE SINGLE WORD:\n"
        "- True: if the query is related to P0 Nominal validation and specifies a P0 Nominal value.\n"
        "- False: if the query is not related to P0 Nominal validation or does not specify a P0 Nominal value.\n"
    )

    USER_INSTRUCTIONS = (
        "QUERY:\n"
        "{query}"
        "\n\n"
        "ANSWER (True or False):\n"
    )

    def __init__(
        self,
    ):
        super().__init__(
            system_instructions=self.SYSTEM_INSTRUCTIONS,
            chat_model_config=ChatModelClientConfig.from_env(client_name="QueryValidationClient"),
        )

    @override
    def invoke(
        self,
        query: str,
    ) -> bool:
        """
        Invoke the chat model to know if the query is relevant to the P0 Nominal Validation task.

        Parameters:
            query(str): the query to evaluate.

        Returns:
            bool: True if the query is relevant and contains all the necessary information, False otherwise.
        """
        prompt = HumanMessage(
            content=self.USER_INSTRUCTIONS.format(query=query)
        )
        response = super().invoke(prompt)
        response = response.content.strip().lower()
        if response not in ["true", "false"]:
            logger.warning(f"Unexpected Router response: {response}. Expected 'True' or 'False'. The response will be treated as 'False'.")
        return response == "true"
