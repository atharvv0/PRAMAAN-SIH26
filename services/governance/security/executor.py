from .tools import Tool
from .policy import check_tool_access


def execute_tool(role, tool):
    decision = check_tool_access(role, tool)

    if decision.decision == "DENY":
        print("Tool execution BLOCKED")
        return "BLOCKED"

    print(f"Executing tool: {tool.value}")
    return "EXECUTED"