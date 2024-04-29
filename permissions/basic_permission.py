from config.constants import OWNER, ADMINISTRATOR, GET, POST, PATCH, DELETE
from typing import List

class BasicPermission():
    def __init__(self, is_superuser: bool = False) -> None:
        self.is_superuser = is_superuser

    def check_if_superuser(self) -> bool:
        return self.is_superuser

    def has_permission(self) -> bool:
        if self.check_if_superuser():
            return True
        return False
    
class BasicCrudPermission(BasicPermission):
    def __init__(
            self,
            is_superuser: bool = False,
            method: str = None,
            role: str = None,
            model_harvester_uid: str = None,
            user_harvesters: List[str] = None,

    ) -> None:
        super().__init__(is_superuser)
        self.method = method
        self.role = role
        self.model_harvester_uid = model_harvester_uid
        self.user_harvesters = user_harvesters

    def has_permission(self) -> bool:
        if super().has_permission():
            return True

        if self.method == GET:
            if self.model_harvester_uid in self.user_harvesters:
                return True
        elif self.method == POST or self.method == PATCH or self.method == DELETE:
            if self.role in [OWNER, ADMINISTRATOR]:
                return True

        return False