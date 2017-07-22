from __future__ import print_function
import importlib
import json
import time
from django.apps import apps as APPS
from django.core import serializers as SRZ
from django.conf import settings
from dex.db import DexDb
from dex.utils import Colors
from dex.conf import EXCLUDE, SERIALIZERS


class Exporter:

    def __init__(self, name):
        self.err = None
        self.db = DexDb(name)
        if self.db.err is not None:
            err = "Dex exporter initialization error:\n" + self.db.err
            self.err = err

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
            if appstr in EXCLUDE or appstr.startswith("django."):
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

    def _get_serializer(self, path):
        function_string = path
        mod_name, func_name = function_string.rsplit('.', 1)
        mod = importlib.import_module(mod_name)
        serz = getattr(mod, func_name)
        #print(serz, type(serz))
        return serz
