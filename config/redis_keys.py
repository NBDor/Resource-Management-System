from config.constants import GPS_TRAFFIC_LOGIC


def get_users_queries_key(user_uid: int) -> str:
    return f"users:{user_uid}:information"


def get_client_uuid_by_agents_group_key(agents_group_id: str) -> str:
    return f"agents_group:{agents_group_id}:client"


def get_agent_config_key(agent_uid: str) -> str:
    return f"agent:{agent_uid}:configuration"


def get_gps_key(agent_uid: str) -> str:
    return f"agent:{agent_uid}:{GPS_TRAFFIC_LOGIC}"


def get_agent_matching_details_key(agent_uid: str) -> str:
    return f"agent:{agent_uid}:payload:details"


def get_agent_url_key(agent_uid: str) -> str:
    return f"agent:{agent_uid}:alerts_url"


def get_camera_key(agent_uid: str, camera_id: str) -> str:
    return f"agent:{agent_uid}:lp_camera:{camera_id}"
