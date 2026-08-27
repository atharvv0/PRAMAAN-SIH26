from datetime import datetime

from .rbac import Role
from .tools import Tool, can_use_tool
from .models import PolicyDecision
from .audit import log_event


def check_tool_access(role, tool):
    if can_use_tool(role, tool):
        decision = "ALLOW"
        reason = "Role is authorized to use this tool"
    else:
        decision = "DENY"
        reason = "Role is not authorized to use this tool"

    result = PolicyDecision(
        decision=decision,
        reason=reason,
        role=role.value,
        action=tool.value,
        timestamp=datetime.now().isoformat()
    )

    log_event(
        role,
        tool,
        decision,
        reason
    )

    return result