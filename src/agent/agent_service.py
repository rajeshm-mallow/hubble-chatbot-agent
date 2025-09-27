from typing import Any

from src.agent.agent_factory import MCPClientFactory, OrderManagementAgentFactory
from src.config import settings
from src.context.request_context import RequestContext


class OrderManagementAgentService:
    """Service for handling order management agent operations."""

    def __init__(self, session_id: str) -> None:
        self.session_id = session_id
        self.agent_factory = OrderManagementAgentFactory(
            settings.MODEL.NAME,
            settings.MODEL.API_KEY,
            settings.SESSION_REPOSITORY.get_session_manager(self.session_id),
        )
        self.client_factory = MCPClientFactory(settings.MCP_SERVER.URL)

    async def process_chat_request(
        self,
        session_uuid: str,
        query: str,
        context: RequestContext,
        authorization_token: str = "",
    ) -> dict[str, Any]:
        """
        Process a chat request using the order management agent.

        Args:
            request: Chat request containing query and session info
            authorization_token: Authorization token for MCP tools

        Returns:
            Dictionary containing the agent's response message
        """
        client = await self.client_factory.create_client(authorization_token)

        with client:
            tools = client.list_tools_sync()

            agent = await self.agent_factory.create_agent(
                session_id=session_uuid,
                tools=tools,
                context=context,
                authorization_token=authorization_token,
            )

            response = agent(query)

            return response
