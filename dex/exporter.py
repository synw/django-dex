from __future__ import print_function
import importlib
import json
import time
from django.db import IntegrityError
from django.apps import apps as APPS
from django.core import serializers as SRZ
from django.conf import settings
from dex.db import DexDb
from dex.utils import Colors
from dex.conf import EXCLUDE, SERIALIZERS


class Exporter:

    def __init__(self, dbname=None):
        self.errors = []
        if dbname is None:
            return
        self.err = None
        self.db = DexDb(dbname)
        if self.db.err is not None:
            err = "Dex exporter initialization error:\n" + self.db.err
            self.err = err

    def clone(self, dbsource, dbdest, apps_list=None):
        if apps_list is None:
            apps_list = settings.INSTALLED_APPS
        st = time.time()
        source = self._get_django_db(dbsource)
        if source is None:
            print("Database", dbsource, "not found")
        dest = self._get_django_db(dbdest)
        if dest is None:
            print("Database", dbdest, "not found")
        models = self.models(apps_list)
        models["contenttypes"]
        num_models = 0
        num_instances = 0
        stats = {}
        stats["num_instances"] = 0
        # special cases
        appname = "contenttypes"
        stats[appname] = {}
        for model in models[appname]:
            stats = self.clone_model(model, dbsource, dbdest,
                                     num_instances, appname, models, num_models, stats)
        for appname in models:
            if appname == "contenttypes" or appname == "sessions":
                continue
            if len(models[appname]) > 0:
                print("# Processing app", appname)

            stats[appname] = {}
            stats[appname]["num_models"] = 0
            for model in models[appname]:
                num_models += 1
                stats = self.clone_model(model, dbsource, dbdest,
                                         stats["num_instances"], appname, models, num_models, stats)
        """
        appname = "permissions"
        stats[appname] = {}
        for model in models[appname]:
            stats = self.clone_model(model, dbsource, dbdest,
                                     stats["num_instances"], appname, models, num_models, stats)
        """
        num_apps = len(models)
        elapsed_time = time.time() - st
        for appname in stats:
            if len(appname) > 1:
                print("###", appname, ":",
                      stats[appname]["num_models"], "models")

            for m in stats[appname]:
                ni = stats[appname][m]
                if ni > 0 and m != "num_models":
                    print("|--", m, ":", ni, "instances")

        print("[OK] Saved", stats["num_instances"], "instances from", num_models,
              "models from", num_apps, "apps in", elapsed_time, "s")
        if len(self.errors) > 0:
            print("ERRORS")
            for err in self.errors:
                print(err)

    def clone_model(self, model, dbsource, dbdest, num_instances, appname, models, num_models, stats):
        qs = self._queryset(model, dbsource, False)
        print("- Model", model.__name__, ":",
              qs.count(), "objects found")
        num_model_instances = 0
        for instance in qs:
            print(num_instances, appname, "-",
                  model.__name__, num_model_instances)

            num_instances += 1
            num_model_instances += 1
            self._save_instance(model, instance, dbdest)
        num_models += 1
        stats[appname]["num_models"] = len(models[appname])
        stats[appname][model.__name__] = num_model_instances
        stats["num_instances"] = num_instances
        return stats

    def run(self, measurement, time_field, appname, report, enable_text_field):
        t = time.time()
        if report is False:
            print("Start exporting data to measurement", measurement)

        apps_list = settings.INSTALLED_APPS
        if appname is not None:
            apps_list = [appname]
        allmodels = self.models(apps_list)
        last_app = False
        num_apps = 0
        initapps = {}
        for a in allmodels:
            initapps[a] = {}
        stats = {"num_models": 0, "num_instances": 0, "apps": initapps}
        for appstr in allmodels:
            if len(allmodels) == num_apps + 1:
                last_app = True
            if report is False:
                print("*********************************** Processing", appstr)

            appmodels = allmodels[appstr]
            last_model = False
            num_models = 0
            for model in appmodels:
                modelname = model.__name__
                if num_models == len(appmodels):
                    last_model = True
                num_models += 1
                stats["apps"][appstr][modelname] = 0
                num_models += 1
                if num_models == len(appmodels) + 1:
                    last_model = True
                stats = self.process_model(model, appstr, measurement,
                                           time_field, last_app, last_model, stats, report, enable_text_field)
            num_apps += 1
        st = json.dumps(stats, indent=4)
        if report is False:
            elapsed_time = time.time() - t
            self.print_stats(stats)
            print("Processed", stats["num_models"], "models from",
                  num_apps, "applications in", str(elapsed_time) + "s")

        else:
            print(st)

    def print_stats(self, stats):
        for appname in stats["apps"]:
            print("# App", Colors.BOLD + appname + Colors.ENDC, ": processed", len(
                stats["apps"][appname]), "models")
            for m in stats["apps"][appname]:
                print("|--", m, ": processed",
                      stats["apps"][appname][m], "instances")

    def process_model(self, model, appstr, measurement, time_field, last_app, last_model, stats, report, enable_text_field):
        global POINTS
        modelname = model.__name__
        if report is False:
            print("######### Processing model", modelname)

        if modelname in SERIALIZERS:
            qs = model.objects.all().prefetch_related(
                *SERIALIZERS[modelname][1])
        else:
            qs = model.objects.all()
        last_instance = False
        stats["apps"][appstr][modelname] = 0
        ti = len(qs)
        ni = 0
        for instance in qs:
            stats["num_instances"] += 1
            if report is False:
                print(stats["num_instances"], appstr, ":", modelname)

            stats["apps"][appstr][modelname] += 1
            ni += 1
            if ti == ni:
                last_instance = True
            data = self.db.serialize(
                instance, model, SERIALIZERS, measurement, time_field, enable_text_field)
            force_save = False
            if last_app is True and last_model is True and last_instance is True:
                force_save = True
            self.db.write(data, force_save)
        stats["num_models"] += 1
        return stats

    def models(self, oapps):
        apps = settings.INSTALLED_APPS
        if oapps is not None:
            apps = oapps
        models = {}
        for appstr in apps:
            appstr = appstr.split('.')[-1]
            if appstr in EXCLUDE or appstr.startswith("django.") and not appstr == "django.contrib.contenttypes":
                continue
            app = APPS.get_app_config(appstr)
            appname = app.label
            app_models = app.get_models()
            appmods = []
            for model in app_models:
                appmods.append(model)
            models[appname] = appmods
        return models

    def serialize(self, instance, modelname, serializers):
        if modelname in serializers:
            serializer = self._get_serializer(serializers[modelname][0])
            data = serializer(instance, self.enable_text_field)
            return data
        else:
            data = json.loads(SRZ.serialize("json", [instance])[1:-1])
            return data["fields"]

    def _get_fields(self, model, instance):
        fields = model._meta.get_fields()
        vals = {}
        for field in fields:
            vals[field.name] = getattr(instance, field.name)
        return vals

    def _get_serializer(self, path):
        function_string = path
        mod_name, func_name = function_string.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        serz = getattr(mod, func_name)
        #print(serz, type(serz))
        return serz

    def _get_django_db(self, dbname):
        dbs = getattr(settings, "DATABASES")
        for name in dbs:
            db = dbs[name]
            if name == dbname:
                return db
        return None

    def _queryset(self, model, dbsource, prefetch=True):
        modelname = model.__name__
        if modelname in SERIALIZERS and prefetch is True:
            qs = model.objects.using(dbsource).all().prefetch_related(
                SERIALIZERS[modelname][1])
        else:
            qs = model.objects.using(dbsource).all()
        return qs

    def _save_instance(self, model, instance, dbdest):
        """
        try:
            fields = self._get_fields(model, instance)
            model.objects.using(dbdest).get_or_create(fields)
        except Exception as e:
            print("ERROR", e)
        """
        try:
            instance.save(using=dbdest, force_insert=True)
        except IntegrityError as e:
            err = "ERROR inserting", instance, "- ", model.__name__
            self.errors.append(err)
            print(err, e)
        return
