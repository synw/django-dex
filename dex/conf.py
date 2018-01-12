from django.conf import settings


EXCLUDE = getattr(settings, 'DEX_EXCLUDE', ["filebrowser", "admin"])

PREFETCH = getattr(settings, "DEX_PREFETCH", {})

SITE_SLUG = getattr(settings, "SITE_SLUG")

COMMAND_CHANNEL = getattr(
    settings, "DEX_COMMAND_CHANNEL", "$" + SITE_SLUG + "_command")

DBS = getattr(settings, "DEX_DBS", {})
