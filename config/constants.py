# permissions Roles
IS_SUPERUSER = "is_superuser"
OWNER = "owner"
ADMINISTRATOR = "administrator"
OPERATOR = "operator"
VIEWER = "viewer"

# Token Fields
USER_UID = "user_uid"
ROLE = "role"

EARLIEST_DATE = "2000-01-01T10:10:10Z"

USER_FORBIDDEN = "User is not allowed to perform this action"

# harvester brands:
HC = "Herba-Cutter"
TG = "Terra-Gather"
PH = "Phyto-Harvest"

# HerbTech Harvesting
HERBTECH_HARVESTER = f"{HC}-harvest"
HERBTECH_HEARTBEAT = f"{HC}-keep_alive"
DATA_TYPE = "data_type"
HARVESTER_UID = "harvester_uid"
EQUIPMENT_ID = "equipment_id"

# default values
DEFAULT_MIN_CHEMICAL_ANALYSIS_VALUE = 70.0
DATA_CACHE_EXPIRATION = 1800

# Herb Classification
CLASSIFY_PROCESSED_HERB = "Classify_Processed_Herb"


OPENING_LINE = "Each model field supports the following filters: "
FILTERS = "['exact', 'in', 'icontains']"
EXAMPLES = "<br><br>For example:"
START_OF_LIST = "<ul>"
END_OF_LIST = "</ul>"
ICONTAINS_EXAMPLE = "<li><strong>'?field_name__icontains=123'</strong> will return all instances that contain 123 in the field</li><br>"
IN_EXAMPLE = "<li><strong>'?field_name__in=[1, 2, 3]'</strong> will return all instances that their field value equals to 1, 2 or 3</li><br>"
EXACT_EXAMPLE = "<li><strong>'?field_name__exact=123'</strong> will return all instances that their field value equals to 123</li><br>"

COMMON_DESCRIPTION = f"{OPENING_LINE}{FILTERS}{EXAMPLES}{START_OF_LIST}{ICONTAINS_EXAMPLE}{IN_EXAMPLE}{EXACT_EXAMPLE}{END_OF_LIST}"