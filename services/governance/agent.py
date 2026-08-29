from services.governance.security.models import AgentRequest
from services.governance.security.policy import check_tool_access
from services.governance.security.rbac import Role
from services.governance.security.tools import Tool


def agent_request(request):
    role = Role(request.role)
    tool = Tool(request.action)

    return check_tool_access(role, tool)


if __name__ == "__main__":
    request = AgentRequest(
        role="user",
        action="database_access"
    )

    print(agent_request(request))