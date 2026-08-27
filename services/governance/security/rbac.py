from enum import Enum


class Role(Enum):
    USER = "user"
    REVIEWER = "reviewer"
    ADMIN = "admin"


class Permission(Enum):
    READ_DOCUMENT = "read_document"
    EXECUTE_TOOL = "execute_tool"
    APPROVE_DOCUMENT = "approve_document"
    MANAGE_USERS = "manage_users"

ROLE_PERMISSIONS = {
    Role.USER: {
        Permission.READ_DOCUMENT,
        Permission.EXECUTE_TOOL
    },

    Role.REVIEWER: {
        Permission.READ_DOCUMENT,
        Permission.EXECUTE_TOOL,
        Permission.APPROVE_DOCUMENT
    },

    Role.ADMIN: {
        Permission.READ_DOCUMENT,
        Permission.EXECUTE_TOOL,
        Permission.APPROVE_DOCUMENT,
        Permission.MANAGE_USERS
    }
}

def is_allowed(role, permission):
    return permission in ROLE_PERMISSIONS.get(role, set())

