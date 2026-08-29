from services.governance.security.policy import check_tool_access
from services.governance.security.rbac import Role
from services.governance.security.tools import Tool
from services.governance.security.network import request_network_access


def main():
    print(check_tool_access(Role.USER, Tool.READ_FILE))
    print(check_tool_access(Role.USER, Tool.DATABASE_ACCESS))
    print(check_tool_access(Role.ADMIN, Tool.DATABASE_ACCESS))

    print("\nNETWORK TEST:")

    result = request_network_access(
        Role.USER,
        "https://example.com"
    )

    print(result)


if __name__ == "__main__":
    main()