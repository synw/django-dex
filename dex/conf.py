from django.conf import settings


EXCLUDE = getattr(settings, 'DEX_EXCLUDE', ["filebrowser", "admin"])
SERIALIZERS = getattr(settings, "DEX_SERIALIZERS", {})
MEASUREMENT = getattr(settings, 'DEX_MEASUREMENT', "django_model")
TIME_FIELD = getattr(settings, 'DEX_DEFAULT_TIME_FIELD', "date")
TIME_FIELDS = getattr(settings, 'DEX_TIME_FIELDS', {
                      "User": "date_joined", "MEvent": "date_posted"})

DBS = getattr(settings, "DEX_DBS", {})