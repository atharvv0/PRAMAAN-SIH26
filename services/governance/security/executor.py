from rbac import Role
from tools import Tool
from policy import check_tool_access


def execute_tool(role, tool):
    decision = check_tool_access(role, tool)

    if decision == "DENY":
        print("Tool execution BLOCKED")
        return

    print(f"Executing tool: {tool.value}")
