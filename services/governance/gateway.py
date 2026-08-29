from services.governance.security.models import AgentRequest
from services.governance.security.policy import check_tool_access
from services.governance.security.rbac import Role
from services.governance.security.tools import Tool
from services.governance.security.network import request_network_access
from services.governance.security.audit import audit_events


def authorize(request):
    role = Role(request.role)
    tool = Tool(request.action)

    return check_tool_access(role, tool)


def main():
    print("=== TOOL TESTS ===")

    tests = [
        AgentRequest("user", "read_file"),
        AgentRequest("user", "database_access"),
        AgentRequest("reviewer", "write_file"),
        AgentRequest("reviewer", "database_access"),
        AgentRequest("admin", "database_access"),
    ]

    for request in tests:
        print(authorize(request))

    print("\n=== NETWORK TEST ===")

    network_result = request_network_access(
        Role.USER,
        "https://example.com"
    )

    print(network_result)

    print("\n=== AUDIT EVENTS ===")
    print(audit_events)


if __name__ == "__main__":
    main()