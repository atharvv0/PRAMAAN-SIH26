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