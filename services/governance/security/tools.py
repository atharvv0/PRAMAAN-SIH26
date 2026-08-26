from enum import Enum
from .rbac import Role


class Tool(Enum):
    READ_FILE = "read_file"
    WRITE_FILE = "write_file"
    EXECUTE_COMMAND = "execute_command"
    DATABASE_ACCESS = "database_access"
    NETWORK_ACCESS = "network_access"


ROLE_TOOLS = {
    Role.USER: {
        Tool.READ_FILE
    },

    Role.REVIEWER: {
        Tool.READ_FILE,
        Tool.WRITE_FILE
    },

    Role.ADMIN: {
        Tool.READ_FILE,
        Tool.WRITE_FILE,
        Tool.EXECUTE_COMMAND,
        Tool.DATABASE_ACCESS,
        Tool.NETWORK_ACCESS
    }
}

def can_use_tool(role, tool):
    return tool in ROLE_TOOLS.get(role, set())

