from goerr import err
from django.conf import settings
from django.db import IntegrityError
from ...conf import PREFETCH


class DjangoDb():

    def _get_django_db(self, dbname):
        dbs = getattr(settings, "DATABASES")
        for name in dbs:
            db = dbs[name]
            if name == dbname:
                return db
        return

    def _queryset(self, model, dbsource, prefetch=True):
        modelname = model.__name__
        if modelname in PREFETCH and prefetch is True:
            qs = model.objects.using(dbsource).all().prefetch_related(
                *PREFETCH[modelname])
        else:
            qs = model.objects.using(dbsource).all()
        return qs

    def _save_instance(self, model, instance, dbdest):
        try:
            self._disable_auto_now_fields(model)
            instance.save(using=dbdest, force_insert=True)
        except IntegrityError as e:
            msg = "ERROR inserting", instance, "- ", model.__name__
            err.new(e, self._save_instance, msg)
            raise(e)
        return

    def _disable_auto_now_fields(self, *models):
        for model in models:
            for field in model._meta.local_fields:
                if hasattr(field, 'auto_now'):
                    field.auto_now = False
                if hasattr(field, 'auto_now_add'):
                    field.auto_now_add = False
