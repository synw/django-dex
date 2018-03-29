from __future__ import print_function
import time
import os
import errno
import shutil
from datetime import datetime
from goerr import err
from django.utils._os import safe_join
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.sites.models import Site
from django.db import connections, transaction
from django.db.models.fields import AutoField
from django.utils.functional import partition
from django.db.models.query import QuerySet
from introspection.inspector import inspect
from .tofiles import ExportToFile
from ..db.django import DjangoDb
from ..conf import EXCLUDE
TERM = "term" in settings.INSTALLED_APPS
if TERM is True:
    from term.commands import rprint
    oprint = print
    print = rprint


class Exporter(DjangoDb, ExportToFile):

    def set_local(self):
        print = oprint

    def clone(self, dbsource, dbdest, applist=None, verbosity=1):
        global EXCLUDE
        st = time.time()
        if applist is None:
            applist = settings.INSTALLED_APPS
        source = self._get_django_db(dbsource)
        if source is None:
            msg = "Database", dbsource, "not found"
            err.new(self.clone, msg)
            return
        dest = self._get_django_db(dbdest)
        if dest is None:
            msg = "Database", dbdest, "not found"
            err.new(self.clone, msg)
            return
        if verbosity > 0:
            print("Cloning database", dbsource, "in database", dbdest)
        models = {}
        for appname in applist:
            appstr = appname.split('.')[-1]
            if appstr in EXCLUDE or appstr.startswith("django.") \
                    or appstr == "django.contrib.contenttypes":
                continue
            # remove all remaining dots to keep just the app name
            try:
                s = appname.split(".")
                appname = s[len(s) - 1]
            except Exception:
                pass
            models[appname] = inspect.models(appname)
        num_models = 0
        num_instances = 0
        stats = {}
        appname = "contenttypes"
        if verbosity > 0:
            print("Found", str(len(applist)), "applications")
        for appname in models:
            if appname == "contenttypes" or appname == "sessions":
                continue
            else:
                if len(models[appname]) > 0:
                    print("# Processing app", appname)
                    stats[appname] = {}
                    stats[appname]["num_models"] = 0
                    for model in models[appname]:
                        if model == Permission or model == Site:
                            continue
                        num_models += 1
                        stats, num_instances = self.clone_model(model, dbsource, dbdest,
                                                                num_instances, appname,
                                                                models, num_models, stats, verbosity)
                        err.fatal()
        self.stats(models, stats, num_models, num_instances, st)

    def clone_model(self, model, dbsource, dbdest, num_instances,
                    appname, models, num_models, stats, verbosity):
        q = model.objects.using(dbsource).all()
        if verbosity > 0:
            print("- Model", model.__name__, ":", q.count(), "objects found")
        num_model_instances = 0
        if inspect.has_m2m(model) is False:
            numi = q.count()
            if numi > 0:
                print("Bulk creating", str(numi), "instances for model",
                      model.__name__, "...")
            try:
                qs = QuerySet(model=model, query=q, using=dbdest)
                self.bulk_create(q, using=dbdest, qs=qs)
                num_instances += numi
                num_model_instances += numi
            except Exception as e:
                err.new(e, self.clone_model,
                        "Can not bulk create model " + model.__name__)
                return
        else:
            for instance in q:
                print(num_instances, appname, "-",
                      model.__name__, num_model_instances)
                num_instances += 1
                num_model_instances += 1
                try:
                    self._save_instance(model, instance, dbdest)
                except Exception as e:
                    err.new(e, self.clone_model,
                            "Can not clone model " + model.__name__)
                    return
        stats[appname]["num_models"] = len(models[appname])
        stats[appname][model.__name__] = num_model_instances
        return stats, num_instances

    def bulk_create(self, objs, using=None, qs=None):
        """
        Fork of the original bulk_create function from django to be able
        to use another database than the default
        """
        for parent in qs.model._meta.get_parent_list():
            if parent._meta.concrete_model is not qs.model._meta.concrete_model:
                raise ValueError(
                    "Can't bulk create a multi-table inherited model")
        fields = qs.model._meta.concrete_fields
        fields = [f for f in fields if not isinstance(f, AutoField)]
        with transaction.atomic(using=using, savepoint=False):
            qs._batched_insert(objs, fields, batch_size=None)

    def archive_replicas(self):
        filename = safe_join(settings.BASE_DIR, "replica.sqlite3")
        has_file = os.path.exists(filename)
        if not has_file:
            return
        dirpath = safe_join(settings.BASE_DIR, "replicas")
        replicas = os.path.exists(dirpath)
        if not replicas is True:
            try:
                print("Creating replicas archive directory ...")
                os.makedirs(safe_join(settings.BASE_DIR, "replicas"))
            except OSError as exc:  # Guard against race condition
                if exc.errno != errno.EEXIST:
                    raise
        dst = safe_join(settings.BASE_DIR, "replicas")
        ts = datetime.now().strftime('%Y-%m-%d-%H-%M')
        newname = "replica." + ts + ".sqlite3"
        os.rename("replica.sqlite3", newname)
        src = safe_join(settings.BASE_DIR, newname)
        print("Archiving current replica ...")
        shutil.move(src, dst)

    def remove_media_archive(self):
        filename = safe_join(settings.BASE_DIR, "media.zip")
        has_file = os.path.exists(filename)
        if has_file is True:
            print("Removing old media archive ...")
            os.remove(filename)

    def zipdir(self):
        shutil.make_archive("media", 'zip', safe_join(
            settings.BASE_DIR, "media"))

    def stats(self, models, stats, num_models, num_instances, st):
        num_apps = len(models)
        elapsed_time = round(time.time() - st, 2)
        for appname in stats:
            if len(appname) > 1 and stats[appname]["num_models"] > 0:
                print("###", appname, ":",
                      stats[appname]["num_models"], "models")

            for m in stats[appname]:
                ni = stats[appname][m]
                if ni > 0 and m != "num_models":
                    print("|--", m, ":", ni, "instances")
                elif ni == 0:
                    print("|xx", m, ": no instances")

        print("[OK] Saved", num_instances, "instances of", num_models,
              "models from", num_apps, "apps in", elapsed_time, "s")
