from config.constants import GPS_TRAFFIC_LOGIC


def get_users_queries_key(user_uid: int) -> str:
    return f"users:{user_uid}:information"


def get_company_uuid_by_project_key(project_id: str) -> str:
    return f"project:{project_id}:company"


def get_harvester_config_key(harvester_uid: str) -> str:
    return f"harvester:{harvester_uid}:configuration"


def get_gps_key(harvester_uid: str) -> str:
    return f"harvester:{harvester_uid}:{GPS_TRAFFIC_LOGIC}"


def get_harvester_matching_details_key(harvester_uid: str) -> str:
    return f"harvester:{harvester_uid}:payload:details"


def get_equipment_key(harvester_uid: str, equipment_id: str) -> str:
    return f"harvester:{harvester_uid}:equipment:{equipment_id}"
