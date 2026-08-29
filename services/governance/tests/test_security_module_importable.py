"""services/governance/{agent,gateway,main}.py previously imported the
security/ RBAC package as a top-level `security` module (`from security.models
import ...`), which only resolves if services/governance itself happens to be
on sys.path -- it is not, under the fully-qualified `services.governance.*`
import convention used everywhere else in this repo (and by pytest). Running
any of those three files raised ModuleNotFoundError.

This does not wire services/governance/security into the orchestrator's
executor -- per services/governance/README.md, that RBAC implementation is a
separate, not-yet-merged module (owner: Role 4 / Arpit) and the executor
continues to use policy_engine/base.py's DefaultPolicyEngine. This test only
proves the module itself is importable and functions as documented, so the
demo entry points (agent.py/gateway.py/main.py) actually run.
"""
from __future__ import annotations


def test_security_package_is_importable_via_fully_qualified_path():
    from services.governance.security.policy import check_tool_access
    from services.governance.security.rbac import Role
    from services.governance.security.tools import Tool

    allowed = check_tool_access(Role.ADMIN, Tool.DATABASE_ACCESS)
    assert allowed.decision == "ALLOW"

    denied = check_tool_access(Role.USER, Tool.DATABASE_ACCESS)
    assert denied.decision == "DENY"


def test_network_access_is_denied_by_default():
    from services.governance.security.network import request_network_access
    from services.governance.security.rbac import Role

    result = request_network_access(Role.USER, "https://example.com")
    assert result["status"] == "BLOCKED"
