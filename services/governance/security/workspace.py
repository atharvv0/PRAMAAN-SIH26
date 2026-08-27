from dataclasses import dataclass


@dataclass
class Team:
    team_id: str
    name: str


@dataclass
class Workspace:
    workspace_id: str
    name: str
    team_id: str


@dataclass
class Resource:
    resource_id: str
    name: str
    workspace_id: str