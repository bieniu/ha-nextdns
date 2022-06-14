"""Constants for NextDNS integration."""
from datetime import timedelta

ATTR_ANALYTICS = "analytics"
ATTR_STATUS = "status"

CONF_PROFILE_ID = "profile_id"
CONF_PROFILE_NAME = "profile_name"

ANALYTICS_UPDATE_INTERVAL = timedelta(minutes=10)
STATUS_UPDATE_INTERVAL = timedelta(minutes=1)

DOMAIN = "nextdns"
