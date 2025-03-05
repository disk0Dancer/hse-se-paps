from abc import ABC, abstractmethod
from typing import Optional

from src.models.user import User


# State Pattern - Abstract base state for permissions
class PermissionState(ABC):
    @abstractmethod
    def can_read(self) -> bool:
        pass

    @abstractmethod
    def can_write(self) -> bool:
        pass

    @abstractmethod
    def can_delete(self) -> bool:
        pass

    @abstractmethod
    def can_admin(self) -> bool:
        pass


# Concrete states for different permission levels
class GuestPermission(PermissionState):
    def can_read(self) -> bool:
        return True

    def can_write(self) -> bool:
        return False

    def can_delete(self) -> bool:
        return False

    def can_admin(self) -> bool:
        return False


class UserPermission(PermissionState):
    def can_read(self) -> bool:
        return True

    def can_write(self) -> bool:
        return True

    def can_delete(self) -> bool:
        return False

    def can_admin(self) -> bool:
        return False


class AdminPermission(PermissionState):
    def can_read(self) -> bool:
        return True

    def can_write(self) -> bool:
        return True

    def can_delete(self) -> bool:
        return True

    def can_admin(self) -> bool:
        return True


# Context class that maintains the current permission state
class PermissionContext:
    def __init__(self, user: Optional[User] = None):
        self.user = user
        self._set_state_from_user()

    def _set_state_from_user(self):
        if self.user is None:
            self.state = GuestPermission()
        # In a real application, this would check user roles from the database
        # For simplicity, we'll use a naming convention
        elif self.user.login.startswith("admin"):
            self.state = AdminPermission()
        else:
            self.state = UserPermission()

    def set_user(self, user: User):
        self.user = user
        self._set_state_from_user()

    def can_read(self) -> bool:
        return self.state.can_read()

    def can_write(self) -> bool:
        return self.state.can_write()

    def can_delete(self) -> bool:
        return self.state.can_delete()

    def can_admin(self) -> bool:
        return self.state.can_admin()


# Flyweight Pattern - PermissionFactory to reduce memory footprint by reusing permission states
class PermissionFactory:
    _admin_permission = AdminPermission()
    _user_permission = UserPermission()
    _guest_permission = GuestPermission()

    @staticmethod
    def get_permission_state(user: Optional[User] = None) -> PermissionState:
        if user is None:
            return PermissionFactory._guest_permission
        # In a real application, this would check user roles from the database
        # For simplicity, we'll use a naming convention
        elif user.login.startswith("admin"):
            return PermissionFactory._admin_permission
        else:
            return PermissionFactory._user_permission
