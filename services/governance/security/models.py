from dataclasses import dataclass


@dataclass
class PolicyDecision:
    decision: str
    reason: str
    role: str
    action: str
    timestamp: str


@dataclass
class AgentRequest:
    role: str
    action: str


@dataclass
class AccessRequest:
    status: str
    requester_team: str
    target_team: str
    resource: str
    permission: str