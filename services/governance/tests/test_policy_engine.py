from services.governance.policy_engine.base import PolicyEngine
from services.governance.security.rbac import Role


def test_user_can_use_file_read_permission():
    engine = PolicyEngine()

    decision = engine.check(
        actor="demo-user",
        action="tool.invoke",
        tool_id="file.read",
        required_permissions=["file.read"],
    )

    assert decision.allow is True


def test_user_cannot_manage_users():
    engine = PolicyEngine()

    decision = engine.check(
        actor="demo-user",
        action="tool.invoke",
        tool_id="user.manage",
        required_permissions=["user.manage"],
    )

    assert decision.allow is False
    assert "not authorized" in decision.reason


def test_unknown_permission_is_denied():
    engine = PolicyEngine()

    decision = engine.check(
        actor="demo-user",
        action="tool.invoke",
        tool_id="unknown.tool",
        required_permissions=["something.unknown"],
    )

    assert decision.allow is False
    assert "Unknown required permission" in decision.reason


def test_network_access_is_always_denied():
    engine = PolicyEngine()

    decision = engine.check(
        actor="demo-user",
        action="tool.invoke",
        tool_id="network.fetch_demo",
        declares_network_access=True,
    )

    assert decision.allow is False
    assert "Network access is denied" in decision.reason


def test_tool_without_permission_is_allowed():
    engine = PolicyEngine()

    decision = engine.check(
        actor="demo-user",
        action="tool.invoke",
        tool_id="text.summarize_naive",
        required_permissions=[],
    )

    assert decision.allow is True