from django.conf import settings


EXCLUDE = getattr(settings, 'DEX_EXCLUDE', ["filebrowser", "admin"])
PREFETCH = getattr(settings, "DEX_PREFETCH", {})
MEASUREMENT = getattr(settings, 'DEX_MEASUREMENT', "django_model")
TIME_FIELD = getattr(settings, 'DEX_DEFAULT_TIME_FIELD', "date")
TIME_FIELDS = getattr(settings, 'DEX_TIME_FIELDS', {
                      "User": "date_joined", "MEvent": "date_posted"})
SITE_SLUG = getattr(settings, "SITE_SLUG")
COMMAND_CHANNEL = getattr(
    settings, "DEX_COMMAND_CHANNEL", "$" + SITE_SLUG + "_command")

DBS = getattr(settings, "DEX_DBS", {})
