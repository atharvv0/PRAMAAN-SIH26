from security.models import AgentRequest
from security.policy import check_tool_access
from security.rbac import Role
from security.tools import Tool


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