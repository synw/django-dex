import importlib
import json
from django.conf import settings
from django.core import serializers as SRZ
from dex.conf import DBS


class DexDb():

    def __init__(self, dbname):
        self.name = dbname
        self.err = None
        conf = self._get_db(dbname)
        if conf is None:
            err = "Database " + dbname + " not found in settings"
            self.err = err
            return
        self.conf = conf
        # init db
        fstr = "dex.db." + self.conf["type"] + ".init"
        init_func = self._importfunc(fstr)
        init_func(self)

    def serialize(self, instance, model, serializers, measurement, time_field, enable_text_field):
        modelname = model.__name__
        if modelname in serializers:
            serializer = self._get_model_serializer(serializers, modelname)
        else:
            serializer = self._get_default_serializer()
        if serializer is None:
            data = self._serialize_json(instance)
        else:
            data = serializer(instance, enable_text_field)
        protocol_serializer = self._get_protocol_serializer()
        if protocol_serializer is not None:
            data = protocol_serializer(
                model, instance, data, measurement, time_field, enable_text_field)
        return data

    def write(self, data, force_save=False):
        fstr = "dex.db." + self.conf["type"] + ".write"
        write_func = self._importfunc(fstr)
        write_func(data, force_save)

    def _serialize_json(self, instance):
        data = json.loads(SRZ.serialize("json", [instance])[1:-1])
        return data["fields"]

    def _get_default_serializer(self):
        fstr = "dex.db.serializers." + self.conf["type"] + ".serialize"
        srz = self._importfunc(fstr)
        return srz

    def _get_protocol_serializer(self):
        fstr = "dex.db." + self.conf["type"] + \
            ".serializers.serialize_protocol"
        srz = self._importfunc(fstr)
        return srz

    def _get_model_serializer(self, serializers, modelname):
        try:
            fstr = serializers[modelname][0]
        except:
            raise
        srz = self._importfunc(fstr)
        return srz

    def _get_writer(self):
        fstr = "dex.db." + self.conf["type"] + ".write"
        f = self._importfunc(fstr)
        return f

    def _get_db(self, dbname):
        for name in DBS:
            db = DBS[name]
            if name == dbname:
                return db
        return None

    def _importfunc(self, fstr):
        try:
            function_string = fstr
            mod_name, func_name = function_string.rsplit('.', 1)
            mod = importlib.import_module(mod_name)
            w = getattr(mod, func_name)
            return w
        except:
            return None
