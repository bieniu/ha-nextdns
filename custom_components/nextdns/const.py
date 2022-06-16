"""Constants for NextDNS integration."""
from datetime import timedelta

ATTR_ANALYTICS = "analytics"
ATTR_CONNECTION = "connection"

CONF_PROFILE_ID = "profile_id"
CONF_PROFILE_NAME = "profile_name"

UPDATE_INTERVAL_ANALYTICS = timedelta(minutes=10)
UPDATE_INTERVAL_CONNECTION = timedelta(minutes=1)

DOMAIN = "nextdns"
