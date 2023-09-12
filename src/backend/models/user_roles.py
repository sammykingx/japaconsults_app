# file that contains the user roles for the application
from enum import Enum


class UserRoles(Enum):
    user: str = "user"
    staff: str = "staff"
    manager: str = "manager"
    admin: str = "admin"
